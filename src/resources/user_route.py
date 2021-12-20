from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from models.user import user_model, user_schema
from common.routing import custom_response

user_api = Blueprint('users', __name__)
user_schema = user_schema()

user_level_struct = {
    0: "Beginner",
    5: "Advanced",
    10: "Expert",
    50: "Insane"
}

NOTFOUNDUSER = "user not found"


@user_api.route('/view/<int:user_id>', methods=['GET'])
def view_by_id(user_id):
    """
    Get a single user via their user ID
    """
    return get_user_details(user_model.get_user_by_id(user_id))


@user_api.route('/view/<string:user_email>', methods=['GET'])
def view_by_email(user_email):
    """
    Get a single user via their user email
    """
    return get_user_details(user_model.get_user_by_email(user_email))


@user_api.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_by_id(user_id):
    """
    Delete a single user via their user id
    """
    return delete_user(user_model.get_user_by_id(user_id))


@user_api.route('/delete/<string:user_email>', methods=['DELETE'])
def delete_by_email(user_email):
    """
    Delete a single user via their user email
    """
    return delete_user(user_model.get_user_by_email(user_email))


@user_api.route('/add', methods=['POST'])
def create():
    """
    Create User Function
    """
    req_data = request.get_json()

    # Calculate the user level from score
    req_data['user_level'] = calculate_level_from_score(
        req_data['social_credit_score'])

    try:
        data = user_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)

    # check if user already exist in the db
    user_in_db = user_model.get_user_by_email(data.get('email'))
    if user_in_db:
        message = {
            'error': 'User already exists, please supply another email address'}
        return custom_response(message, 400)

    user = user_model(data)
    user.save()
    return custom_response({"message": "success"}, 200)

def delete_user(user):
    if not user:
        return custom_response({'error': NOTFOUNDUSER}, 404)
    user.delete()
    return custom_response({'message': 'deleted'}, 200)

def get_user_details(user):
    if not user:
        return custom_response({'error': NOTFOUNDUSER}, 404)
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)

def calculate_level_from_score(score):
    level = ""
    for key, value in user_level_struct.items():
        if score >= key:
            level = value
    return level
