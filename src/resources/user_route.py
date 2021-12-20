from flask import request, json, Response, Blueprint
from marshmallow.exceptions import ValidationError
from models.user import user_model, user_schema

user_api = Blueprint('users', __name__)
user_schema = user_schema()

user_level_struct = {
    0: "Beginner",
    5: "Advanced",
    10: "Expert",
    50: "Insane"
}


@user_api.route('/view/<int:user_id>', methods=['GET'])
def view_by_id(user_id):
    """
    Get a single user via their user ID
    """
    user = user_model.get_one_user(user_id)
    if not user:
        return custom_response({'error': 'user not found'}, 404)

    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/view/<string:user_email>', methods=['GET'])
def view_by_email(user_email):
    """
    Get a single user via their user email
    """
    user = user_model.get_user_by_email(user_email)
    if not user:
        return custom_response({'error': 'user not found'}, 404)

    ser_user = user_schema.dump(user)
    return custom_response(ser_user, 200)


@user_api.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_by_id(user_id):
    """
    Delete a single user via their user id
    """
    user = user_model.get_one_user(user_id)
    if not user:
        return custom_response({'error': 'user not found'}, 404)
    user.delete()
    return custom_response({'message': 'deleted'}, 204)


@user_api.route('/delete/<string:user_email>', methods=['DELETE'])
def delete_by_email(user_email):
    """
    Delete a single user via their user email
    """
    user = user_model.get_user_by_email(user_email)
    if not user:
        return custom_response({'error': 'user not found'}, 404)
    user.delete()
    return custom_response({'message': 'deleted'}, 204)


@user_api.route('/add', methods=['POST'])
def create():
    """
    Create User Function
    """
    req_data = request.get_json()
    print(req_data)

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
    return custom_response("Success", 200)


def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )


def calculate_level_from_score(score):
    level = ""
    for key, value in user_level_struct.items():
        if score >= key:
            level = value
    return level
