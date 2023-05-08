import os

from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError
from print_api.models.user import user_model, user_schema
from print_api.common.routing import custom_response

user_api = Blueprint("users", __name__)
user_schema = user_schema()

# get params from .env
advanced_level = int(os.getenv('ADVANCED_LEVEL'))
expert_level = int(os.getenv('EXPERT_LEVEL'))
insane_level = int(os.getenv('INSANE_LEVEL'))
# set boundaries
user_level_struct = {0: "beginner", advanced_level: "advanced", expert_level: "expert", insane_level: "insane"}


@user_api.route("/update/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_by_id(user_id):
    """
    Function to update a user via their ID
    :param int user_id: PK of the user record
    :return response: error or success message
    """
    req_data = request.get_json()
    user = user_model.get_user_by_id(user_id)
    return update_user_details(user, req_data, search_string=user_id)


@user_api.route("/update/<string:user_email>", methods=["PUT"])
@jwt_required()
def update_by_email(user_email):
    """
    Function to update a user via their user email
    :param str user_email: email of the user record
    :return response: error or success message
    """
    req_data = request.get_json()
    user = user_model.get_user_by_email(user_email)
    return update_user_details(user, req_data, search_string=user_email)


@user_api.route("/view/<int:user_id>", methods=["GET"])
@jwt_required()
def view_by_id(user_id):
    """
    Function to serialize a user via their ID
    :param int user_id: PK of the user record
    :return response: error or serialized user
    """
    return get_user_details(user_model.get_user_by_id(user_id), search_string=user_id)


@user_api.route("/view/<string:user_email>", methods=["GET"])
@jwt_required()
def view_by_email(user_email):
    """
    Function to serialize a user via their email
    :param str user_email: email of the user record
    :return response: error or serialized user
    """
    return get_user_details(user_model.get_user_by_email(user_email), search_string=user_email)


@user_api.route("/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_by_id(user_id):
    """
    Function to delete a user via their ID
    :param int user_id: PK of the user record
    :return response: error or success message
    """
    return delete_user(user_model.get_user_by_id(user_id), search_string=user_id)


@user_api.route("/delete/<string:user_email>", methods=["DELETE"])
@jwt_required()
def delete_by_email(user_email):
    """
    Function to delete a user via their user email
    :param str user_email: email of the user record
    :return response: error or success message
    """
    return delete_user(user_model.get_user_by_email(user_email), search_string=user_email)


@user_api.route("/view/all", methods=["GET"])
@jwt_required()
def view_all_users():
    """
    Function to serialize all users
    :return response: error or serialized user
    """
    return get_multiple_user_details(user_model.get_all_users())


@user_api.route("/add", methods=["POST"])
@jwt_required()
def create():
    """
    Function to create a new user in the database
    :return response: error or success message
    """
    req_data = request.get_json()

    try:
        data = user_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, extra_info=err.messages)

    # check if user already exist in the db
    user_in_db = user_model.get_user_by_email(data.get("email"))
    if user_in_db:
        message = {"error": "User already exists, please supply another email address"}
        return custom_response(status_code=400, extra_info=message)

    user = user_model(data)
    user.save()
    return custom_response(status_code=200, extra_info="success", details=user_schema.dump(user))


def delete_user(user, search_string):
    """
    Function to delete a user from the database
    :param user: user object to be deleted
    :return response: error or success message
    """
    if not user:
        return custom_response(status_code=404, details=f"user '{search_string}' not found")
    user_name = user.name
    user.delete()
    return custom_response(status_code=200, extra_info=f"deleted user: {user_name}")


def get_user_details(user, search_string):
    """
    Function to serialize the details of a user
    :param user: user object to be serialized
    :return response: error or serialized user
    """
    if not user:
        return custom_response(status_code=404, details=f"user '{search_string}' not found")
    ser_user = user_schema.dump(user)
    ser_user["user_level"] = calculate_level_from_score(user.user_score)
    return custom_response(status_code=200, details=ser_user, extra_info="success")


def update_user_details(user, req_data, search_string):
    """
    Function to update the details of a user
    :param user: user object to update
    :param dict req_data: dict of data to update the user with
    :return response: error or serialized updated user details
    """
    if not user:
        return custom_response(status_code=404, details=f"user '{search_string}' not found")

    # Check if user score is being changed and level needs to be updated
    if (req_data.get("user_score") is not None) and not user.score_editable:
        req_data["user_score"] = user.user_score
    # Try and load user data to the schema
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    user.update(data)
    ser_user = user_schema.dump(user)
    return custom_response(status_code=200, details=ser_user, extra_info="success")


def calculate_level_from_score(score):
    """
    Function to calculate what level the user would be with a given score.
    :param int score: score of the user
    """
    level = ""
    for key, value in user_level_struct.items():
        if score >= key:
            level = value
    return level


def get_multiple_user_details(users):
    """
    Function to take a query object of multiple users and serialize them
    :param users: the query object containing the users
    :return response: error or a list of serialized user data
    """
    if not users:
        return custom_response(status_code=404, details="Users not found")
    jason = []
    for user in users:
        user_dict = user_schema.dump(user)
        user_dict["user_level"] = calculate_level_from_score(user.user_score)
        jason.append(user_dict)

    final_res = {"users": jason}
    return custom_response(status_code=200, details=final_res, extra_info="success")
