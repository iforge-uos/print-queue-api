from flask import Blueprint
from print_api.common.auth import requires_access_level
from print_api.common.routing import custom_response

other_api = Blueprint('misc', __name__)

# This whole file is more or less of a joke


@other_api.route('/toast', methods=["GET"])
@requires_access_level(0)
def test():
    '''
    Test Endpoint 1
    '''
    return custom_response(status_code=418, details="sweet cheeks")


@other_api.route('/legal', methods=["GET"])
@requires_access_level(0)
def test_2():
    '''
    Test Endpoint 2
    '''
    return custom_response(status_code=451, details="Pipis Room")
