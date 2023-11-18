from flask import Blueprint

import print_api.common.tasks as tasks
from print_api.common.routing import custom_response

other_api = Blueprint("misc", __name__)


# This whole file is more or less of a joke


@other_api.route("/toast", methods=["GET"])
# @role_required("root")
def test():
    """
    Test Endpoint 1
    """
    return custom_response(status_code=418, extra_info="sweet cheeks")


@other_api.route("/legal", methods=["GET"])
# @role_required("root")
def test_2():
    """
    Test Endpoint 2
    """
    return custom_response(status_code=451, extra_info="Pipis Room")


@other_api.route("/test_celery", methods=["GET"])
# @role_required("root")
def test_celery():
    """
    Test Endpoint 3
    """
    tasks.wait_task.apply_async(kwargs={"sleep_time": 10})
    return custom_response(status_code=200, extra_info="Celery task has been sent")
