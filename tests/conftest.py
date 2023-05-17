from flask import Flask
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from print_api import create_app
from print_api.models import User, db
from print_api.common.auth import generate_tokens


init_sql_path = os.path.join(os.path.dirname(__file__), "init.sql")


@pytest.fixture(scope="session", autouse=True)
def app():
    app : Flask = create_app(config_env="testing")
    
    with app.app_context():
        db.create_all()
        seed_database()
        yield app
        db.session.close()
        db.drop_all()

    # clean up / reset resources here


def seed_database():
    # Create test users
    user_data = [
        {
            "email": "test_user1@example.com",
            "uid": "test_user",
            "name": "Test User",
            "short_name": "TU",
            "user_score": 100,
            "is_rep": False,
            "score_editable": True,
            "completed_count": 10,
            "failed_count": 2,
            "rejected_count": 1,
            "slice_completed_count": 5,
            "slice_failed_count": 1,
            "slice_rejected_count": 0
        },

    ]

    for data in user_data:
        user = User(data)
        db.session.add(user)

    db.session.commit()

def delete_database():
    # TODO IMPLEMENT
    pass


@pytest.fixture()
def client(app):
    test_client = app.test_client()

    def make_request(method, url, **kwargs):
        # Get a new token for each request
        token = get_new_token(app)
        headers = kwargs.pop('headers', {})
        headers["Authorization"] = f"Bearer {token}"
        
        response = test_client.open(method=method, path=url, headers=headers, **kwargs)
        if response.status_code == 401:
            # Token expired, get a new one and retry the request
            new_token = get_new_token(app)
            headers["Authorization"] = f"Bearer {new_token}"
            response = test_client.open(method=method, path=url, headers=headers, **kwargs)
        return response

    test_client.make_request = make_request
    return test_client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def get_new_token(app):
    with app.app_context():
        access_token, _ = generate_tokens("test_user")
    return access_token


def check_response(res, exp_status_code, exp_details, exp_extra_info):
    assert res.status_code == exp_status_code

    # Load the json data from the response
    data = json.loads(res.data)

    if 200 <= exp_status_code < 300:
        assert data['status'] == 'success'
        assert data['payload']['data'] == exp_details
        assert data['payload']['error'] is None
        assert data['meta']['message'] == exp_extra_info
    else:
        assert data['status'] == 'error'
        assert data['payload']['data'] is None
        assert data['payload']['error']['code'] == exp_status_code
        assert data['payload']['error']['message'] == exp_details
        assert data['meta']['message'] == exp_extra_info