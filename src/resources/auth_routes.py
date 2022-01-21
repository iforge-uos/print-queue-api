from flask import Blueprint, request, current_app
from marshmallow.exceptions import ValidationError
from common.routing import custom_response
from common.auth import generate_hash_key, requires_access_level
from models.auth_keys import auth_model, auth_schema


auth_api = Blueprint('auth', __name__)
auth_schema = auth_schema()


@auth_api.route('/generate-key/<int:permission_level>', methods=['POST'])
@requires_access_level(3)
def create_key(permission_level):
    """
    Route to change the current environment version of the server used to verify print queue clients \n
    Arguments:
        permission_level: the permission level for the key
    Returns:
        response: success or error
    """
    if permission_level not in [0,1,2,3]:
        return custom_response({"Error": "Invalid permission_level"}, 400)
    req_data = request.get_json()

    # generate new api_key
    api_key = generate_hash_key()
    req_data['key'] = api_key
    req_data['permission_value'] = permission_level
    print(req_data)

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
    return custom_response({"new key": api_key}, 200)


@auth_api.route('/app/get', methods=['GET'])
def get_allowed_version():
    """
    Route to get the current environment version of the server used to verify print queue clients \n
    Arguments:
        none:
    Returns:
        response: value or error
    """
    app_ver = current_app.config['ALLOWED_APP_VERSION']
    if app_ver is not None:
        return custom_response({"version": int(app_ver)}, 200)
    else:
        return custom_response(
            {"error": "App version not set, please set it"}, 404)
