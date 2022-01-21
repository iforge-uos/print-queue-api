from flask import Blueprint, request, current_app
from marshmallow.exceptions import ValidationError
from common.routing import custom_response
from common.auth import generate_hash_key, requires_access_level
from models.auth_keys import auth_model, auth_schema


auth_api = Blueprint('auth', __name__)
auth_schema = auth_schema()


@auth_api.route('/generate-key', methods=['POST'])
@requires_access_level(3)
def create_key():
    """
    Route to change the current environment version of the server used to verify print queue clients
    :return response: success or error
    """
    req_data = request.get_json()

    if req_data['permission_value'] not in [0,1,2,3]:
        return custom_response({"Error": "Invalid permission value supplied"}, 400)

    # generate new api_key
    api_key = generate_hash_key()
    req_data['key'] = api_key
    

    # Try and load the data into the model
    try:
        data = auth_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)

    key = auth_model(data)
    key.save()
    return custom_response({"Key": api_key}, 200)