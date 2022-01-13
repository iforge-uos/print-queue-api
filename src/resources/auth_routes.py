from flask import Blueprint, request
from common.routing import custom_response
from common.auth import write_version_to_dotenv, get_allowed_app_version

auth_api = Blueprint('auth', __name__)


@auth_api.route('/app/update', methods=['POST'])
def change_allowed_version():
    req_data = request.json
    output = write_version_to_dotenv(req_data["version"])
    if output:
        return custom_response("success", 200)
    else:
        return custom_response("error", 500)


@auth_api.route('/app/get', methods=['GET'])
def get_allowed_version():
    app_ver = get_allowed_app_version()
    if app_ver is not None:
        return custom_response({"version" : int(app_ver)}, 200)
    else:
        return custom_response({"error" : "App version not set, please set it"}, 404)
    

