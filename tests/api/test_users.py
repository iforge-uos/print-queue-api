from tests.conftest import check_response
from print_api.models import User, db
from print_api.resources.api_routes.user_route import calculate_level_from_score


def empty_database():
    db.drop_all()
    db.create_all()


def seed_users(n):
    user_dicts = []

    for i in range(n + 1):
        i += 1
        user_params = {
            "name": f"Test User {i}",
            "id": i,
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
        user_params["user_level"] = calculate_level_from_score(user_params["user_score"])

        user_dicts.append(user_params)

    db.session.commit()

    return user_dicts


def test_get_all_users(app, client):
    empty_database()
    data = {"users": seed_users(10)}
    response = client.make_request('get', "users/view/all")
    check_response(res=response, exp_status_code=200, exp_details=data, exp_extra_info='success')
