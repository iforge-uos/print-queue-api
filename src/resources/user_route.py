from flask import request, json, Response, Blueprint
from marshmallow.exceptions import ValidationError
from models.user import user_model, user_schema

user_api = Blueprint('users', __name__)
user_schema = user_schema()

user_level_struct = {
    0 : "Beginner",
    5 : "Advanced",
    10: "Expert",
    50: "Insane"
}



@user_api.route('/', methods=['GET','POST'])
def create():
    """
    Create User Function
    """
    req_data = request.get_json()
    score = req_data['social_credit_score']
    level = ""
    for key, value in user_level_struct.items():
        if score >= key:
            level = value
    req_data['user_level'] = level
    print(level)

    try:
        data = user_schema.load(req_data)
    except ValidationError as err:
        print(err.messages)  # => {"email": ['"foo" is not a valid email address.']}
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
    return custom_response("", 200)

def custom_response(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
