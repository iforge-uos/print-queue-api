from flask import Blueprint, request, current_app
from common.routing import custom_response
from common.auth import write_version_to_dotenv

auth_api = Blueprint('auth', __name__)


@auth_api.route('/app/update', methods=['POST'])
def change_allowed_version():
    """
    Route to change the current environment version of the server used to verify print queue clients \n
    Arguments:
        none:
    Returns:
        response: success or error
    """
    req_data = request.json
    output = write_version_to_dotenv(req_data["version"])
    if output:
        return custom_response("success", 200)
    else:
        return custom_response("error", 500)


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
