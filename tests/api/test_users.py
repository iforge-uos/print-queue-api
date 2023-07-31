from tests.conftest import check_response, remove_datetime_fields
from print_api.models import User, db


def empty_database():
    db.session.query(User).delete()
    db.session.commit()


def seed_users(n):
    empty_database()
    user_objects = []

    for i in range(1, n + 1):
        user_params = {
            "name": f"Test User {i}",
            "email": f"user_{i}@test.com",
            "uid": f"test_{i}",
            "short_name": f"Test {i}",
            "user_score": i,
            "is_rep": False,
            "score_editable": True,
            "completed_count": 0,
            "failed_count": 0,
            "rejected_count": 0,
            "slice_completed_count": 0,
            "slice_failed_count": 0,
            "slice_rejected_count": 0,
        }
        user = User(user_params)

        db.session.add(user)
        user_objects.append(user)

    db.session.commit()

    users = User.query.all()
    user_dicts = [user.to_dict() for user in users]

    return remove_datetime_fields(user_dicts)


def test_get_all_users(app, client):
    resp = {"users": seed_users(10)}
    response = client.make_request('get', "users/view/all")
    check_response(res=response, exp_status_code=200, exp_details=resp, exp_extra_info='success')


def test_get_user_by_id(app, client):
    user_dict = seed_users(1)
    resp = {"user": user_dict[0]}
    url = f"users/view/{user_dict[0]['id']}"
    response = client.make_request('get', url)
    check_response(res=response, exp_status_code=200, exp_details=resp, exp_extra_info='success')


def test_get_user_by_email(app, client):
    user_dict = seed_users(1)
    resp = {"user": user_dict[0]}
    url = f"users/view/{user_dict[0]['email']}"
    response = client.make_request('get', url)
    check_response(res=response, exp_status_code=200, exp_details=resp, exp_extra_info='success')


def test_get_user_no_users(app, client):
    empty_database()
    response = client.make_request('get', "users/view/all")
    check_response(res=response, exp_status_code=404, exp_details='Users not found', exp_extra_info=None)
