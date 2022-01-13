from flask import Blueprint, request
from common.routing import custom_response
from common.auth import write_version_to_dotenv

auth_api = Blueprint('auth', __name__)


@auth_api.route('/update', methods=['POST'])
def change_allowed_version():
    req_data = request.json
    output = write_version_to_dotenv(req_data["version"])
    if output:
        return custom_response("success", 200)
    else:
        return custom_response("error", 500)