from flask import Blueprint, request
from marshmallow.exceptions import ValidationError
from print_api.common.routing import custom_response
from print_api.common.auth import generate_hash_key, requires_access_level
from print_api.models.auth_keys import auth_model, auth_schema


auth_api = Blueprint('auth', __name__)
auth_schema = auth_schema()

NOTFOUNDKEYS = 'key(s) not found'


@auth_api.route('/generate/single', methods=['POST'])
@requires_access_level(3)
def create_key():
    """
    Route to create a new API key to use with the rest of the system
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


@auth_api.route('/generate/set/<string:client_version>', methods=['POST'])
@requires_access_level(3)
def create_key_set(client_version):
    """
    Route to create a new set of keys for both clients
    :return response: success or error
    """
    # Create a key for each client type, 1 ~ 2
    jason = []
    for i in range(1, 3):
        api_key = generate_hash_key()
        data = {
            'associated_version': client_version,
            'permission_value' : i,
            'key' : api_key
            }
        key = auth_model(data)
        key.save()
        jason.append(auth_schema.dump(key))
    return custom_response(jason, 200)



@auth_api.route('/delete/<int:key_id>', methods=['DELETE'])
@requires_access_level(3)
def delete_key(key_id):
    """
    Route to delete keys thereby invalidating clients.
    :param int key_id: PK of the key to delete
    :return response: success or error
    """
    key = auth_model.get_key_by_id(key_id)
    if not key:
        return custom_response({'error': NOTFOUNDKEYS}, 404)
    key.delete()
    return custom_response({'message': 'deleted'}, 200)


@auth_api.route('/view/single/<int:key_id>', methods=['GET'])
@requires_access_level(3)
def get_key(key_id):
    """
    Route to get a single key and serialize it
    :param int key_id: PK of the key to fetch
    :return response: error or serialized key
    """
    key = auth_model.get_key_by_id(key_id)
    if not key:
        return custom_response({'error': NOTFOUNDKEYS}, 404)
    ser_key = auth_schema.dump(key)
    return custom_response(ser_key, 200)


@auth_api.route('/view/all', methods=['GET'])
@requires_access_level(3)
def get_all_keys():
    """
    Route to get all keys and serialize them
    :return response: error or serialized keys
    """
    return get_multiple_key_details(auth_model.get_all_keys())


@auth_api.route('/view/multiple/<string:client_version>', methods=['GET'])
@requires_access_level(3)
def get_keys_by_version(client_version):
    """
    Route to get all keys and serialize them
    :param str client_version: client Version to fetch keys for
    :return response: error or serialized keys
    """
    return get_multiple_key_details(auth_model.get_keys_by_associated_version(client_version))


def get_multiple_key_details(keys):
    """
    Function to take a query object and serialize each key inside it.
    :param keys: the query object containing all the keys
    :return response: error the a list of serialized key objects.
    """
    if not keys:
        return custom_response({'error': NOTFOUNDKEYS}, 404)
    jason = []
    for key in keys:
        jason.append(auth_schema.dump(key))
    return custom_response(jason, 200)
