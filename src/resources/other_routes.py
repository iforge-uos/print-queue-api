from flask import Blueprint
from common.routing import custom_response

other_api = Blueprint('misc', __name__)

# This whole file is more or less of a joke

@other_api.route('/toast', methods=["GET"])
def test():
    '''
    Test Endpoint 1
    '''
    return custom_response("sweet cheeks", 418)


@other_api.route('/legal', methods=["GET"])
def test_2():
    '''
    Test Endpoint 2
    '''
    return custom_response("Pipis Room", 451)
