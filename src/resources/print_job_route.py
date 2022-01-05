from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from models.print_jobs import print_job_model, print_job_schema, project_types, job_status
from models.printers import printer_model
from models.user import user_model
from common.routing import custom_response

print_job_api = Blueprint('print jobs', __name__)
print_job_schema = print_job_schema()

NOTFOUNDJOB = "job not found"


@print_job_api.route('/add', methods=['POST'])
def create():
    """
    Create Print Job Function
    """
    req_data = request.get_json()

    # Check if printer_id exists
    # if not check_printer_id(req_data['printer_id']):
    #   return custom_response({"error" : "printer is not found"}, 404)

    # Get user level
    user_level = check_user_id(req_data['user_id'])
    if user_level is None:
        return custom_response({"error": "user is not found"}, 404)

    # Check if a rep approved this print <- this should pass but sanity check
    if user_level == "Beginner" and not check_rep_id(req_data['checked_by']):
        return({"error": "rep details are incorrect"}, 404)
    elif user_level == "Advanced":
        req_data["status"] = "awaiting"
        if not "stl_slug" in req_data:
            return({"error": "stl slug needed"}, 404)
        req_data.pop("checked_by")
    else:
        req_data["status"] = "queued"

    # Try and load the data into the model
    try:
        data = print_job_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)

    job = print_job_model(data)
    job.save()
    return custom_response({"message": "success"}, 200)


@print_job_api.route('/view/single/<int:job_id>', methods=['GET'])
def view_job_single(job_id):
    return get_single_job_details(print_job_model.get_print_job_by_id(job_id))


@print_job_api.route('/view/all/<string:status>', methods=['GET'])
def view_jobs_by_status(status):
    # Sanity check url
    if status not in job_status._member_names_:
        return custom_response({"error": "Status not found"}, 404)
    # Return a list of json objects that match status query
    return get_multiple_job_details(print_job_model.get_print_jobs_by_status(status))


def check_printer_id(printer_id):
    if (printer_model.get_printer_by_id(printer_id) is None):
        return False
    return True


def check_user_id(user_id):
    user = user_model.get_user_by_id(user_id)
    if (user is None):
        return None
    return user.user_level


def check_rep_id(rep_id):
    user = user_model.get_user_by_id(rep_id)
    if (user is None or user.is_rep == False):
        return False
    return True


def get_single_job_details(job):
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    ser_job = print_job_schema.dump(job)
    print(ser_job)
    return custom_response(ser_job, 200)


def get_multiple_job_details(jobs):
    if not jobs:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    # This is jank af but it works and I can't think of a better way to do this lol
    jason = []
    for log in jobs:
        jason.append(print_job_schema.dump(log))
    return custom_response(jason, 200)
