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


@user_api.route('/update/<int:user_id>', methods=['PUT'])
def update_by_id(user_id):
    """
    Function to update a user via their ID \n
    Arguments:
        user_id: the integer PK of the user record
    Returns:
        Response: error or success message
    """
    req_data = request.get_json()
    user = user_model.get_user_by_id(user_id)
    return update_user_details(user, req_data)


@user_api.route('/update/<string:user_email>', methods=['PUT'])
def update_by_email(user_email):
    """
    Function to update a user via their user email \n
    Arguments:
        user_email: the string email of the user record
    Returns:
        Response: error or success message
    """
    req_data = request.get_json()
    user = user_model.get_user_by_email(user_email)
    return update_user_details(user, req_data)


@user_api.route('/view/<int:user_id>', methods=['GET'])
def view_by_id(user_id):
    """
    Function to serialize a user via their ID \n
    Arguments:
        user_id: the integer PK of the user record
    Returns:
         Response: error or serialized user
    """
    return get_user_details(user_model.get_user_by_id(user_id))


@user_api.route('/view/<string:user_email>', methods=['GET'])
def view_by_email(user_email):
    """
    Function to serialize a user via their email \n
    Arguments:
        user_email: the string email of the user record
    Returns:
        Response: error or serialized user
    """
    return get_user_details(user_model.get_user_by_email(user_email))


@user_api.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_by_id(user_id):
    """
    Function to delete a user via their ID \n
    Arguments:
        user_id: the integer PK of the user record
    Returns:
        Response: error or success message
    """
    return delete_user(user_model.get_user_by_id(user_id))


@user_api.route('/delete/<string:user_email>', methods=['DELETE'])
def delete_by_email(user_email):
    """
    Function to delete a user via their user email \n
    Arguments:
        user_email: the string email of the user record
    Returns:
        Response: error or success message
    """
    return delete_user(user_model.get_user_by_email(user_email))


@user_api.route('/add', methods=['POST'])
def create():
    """
    Function to create a new user in the database \n
    Arguments:
        None:
    Returns:
        Response: error or success message
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
    """
    Function to delete a user from the database \n
    Arguments:
        user: user object to be deleted
    Returns:
        Response: error or success message
    """
    if not user:
        return custom_response({'error': NOTFOUNDUSER}, 404)
    user.delete()
    return custom_response({'message': 'deleted'}, 200)


def get_user_details(user):
    """
    Function to serialize the details of a user \n
    Arguments:
        user: user object to be serialized
    Returns:
        Response: error or serialized user
    """
    if not user:
        return custom_response({'error': NOTFOUNDUSER}, 404)
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


def update_user_details(user, req_data):
    """
    Function to update the details of a user
    Parameters:
        user: user object to update
        req_data: dict of data to update the user with
    Returns:
        Response: error or serialized updated user details
    """
    if not user:
        return custom_response({'error': NOTFOUNDUSER}, 404)

    # Check if user score is being changed and level needs to be updated
    if (req_data.get('social_credit_score') is not None):
        # Check if user score can be changed
        if (not user.score_editable):
            req_data['social_credit_score'] = user.social_credit_score
        # Recalculate user level
        req_data['user_level'] = calculate_level_from_score(
            req_data.get('social_credit_score'))
    # Try and load user data to the schema
    try:
        data = user_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    user.update(data)
    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


def calculate_level_from_score(score):
    """
    Function to calculate what level the user would be with a given score.
    Parameters:
        score: integer score of the user
    Returns:
        level: string level that the score falls into from the user_level_struct
    """
    level = ""
    for key, value in user_level_struct.items():
        if score >= key:
            level = value
    return level
