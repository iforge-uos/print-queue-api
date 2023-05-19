import pytest
import dateutil.parser
from flask_jwt_extended import create_access_token
import json
import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from print_api import create_app
from print_api.models import db


@pytest.fixture(scope="session", autouse=True)
def app():
    app = create_app(config_env="testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.close()
        db.drop_all()


@pytest.fixture()
def client(app):
    test_client = app.test_client()

    def make_request(method, url, **kwargs):
        # Get a new token for each request
        token = get_new_token(app)
        headers = kwargs.pop('headers', {})
        headers["Authorization"] = f"Bearer {token}"
        url = f"/api/v1/{url}"

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
        access_token = create_access_token(identity="test_user", fresh=True)
    return access_token


def remove_datetime_fields(data):
    if isinstance(data, list):
        return [remove_datetime_fields(value) for value in data]
    elif isinstance(data, dict):
        return {
            key: remove_datetime_fields(value)
            for key, value in data.items()
            if not is_datetime_str(value)
        }
    else:
        return data


def is_datetime_str(value):
    if isinstance(value, datetime.datetime):
        return True
    elif not isinstance(value, str):
        return False
    try:
        dateutil.parser.parse(value)
        return True
    except (ValueError, TypeError):
        return False


def check_response(res, exp_status_code, exp_details, exp_extra_info):
    assert res.status_code == exp_status_code

    # Load the json data from the response
    data = json.loads(res.data)

    # Remove datetime fields from response data
    data = remove_datetime_fields(data)

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
