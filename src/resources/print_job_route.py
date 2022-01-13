from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from resources.printer_route import increment_printer_details
from models.print_jobs import print_job_model, print_job_schema, project_types, job_status
from models.printers import printer_model
from models.user import user_model
from common.routing import custom_response
from common.emails import email
from datetime import datetime

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
    # Return a list of jason objects that match status query
    return get_multiple_job_details(print_job_model.get_print_jobs_by_status(status))


@print_job_api.route('/approve/list', methods=['GET'])
def list_awaiting_jobs():
    return get_multiple_job_details(print_job_model.get_print_jobs_by_status("awaiting"))


@print_job_api.route('/approve/accept/<int:job_id>', methods=['PUT'])
def accept_awaiting_job(job_id):
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    return update_job_details(job, {"status": "queued"})


@print_job_api.route('/approve/reject/<int:job_id>', methods=['PUT'])
def reject_awaiting_job(job_id):
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    result = email(job.user_id, job.print_name, 2)
    if not result:
        return custom_response({'error': 'user_id error'}, 404)
    return update_job_details(job, {"status": "rejected"})


@print_job_api.route('/start/<int:job_id>', methods=['PUT'])
def start_queued_job(job_id):
    req_data = request.get_json()
    # Check if the request body has the correct keys
    required_keys = ("colour", "printer")
    # Calculating what data to fetch from printer model
    request_dict = filter_request_to_keys(req_data, required_keys)

    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    # Check job is allowed to run
    if job.status != job_status.queued:
        return custom_response({'error': "Job Cannot be run"}, 400)
    printer_id = request_dict['printer']
    if not check_printer_id(printer_id):
        return custom_response({'error': "Printer Not Found"}, 404)
    if running_on_printer(printer_id):
        return custom_response({'error': "Already Running"}, 400)

    request_dict['status'] = "running"
    request_dict['date_started'] = datetime.now().isoformat()
    return update_job_details(job, request_dict)


@print_job_api.route('/complete/<int:job_id>', methods=['PUT'])
def complete_queued_job(job_id):

    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)

    # Check the job is running otherwise error
    if job.status != job_status.running:
        return custom_response({'error': "Job not running"}, 400)

    # Change job details
    printer_increment_values = {
        "total_time_printed": job.print_time,
        "completed_prints": 1,
        "total_filament_used": job.filament_usage
    }

    # Increment Printer Values
    ser_printer = increment_printer_details(
        printer_model.get_printer_by_id(job.printer), printer_increment_values)
    if ser_printer is None:
        return custom_response({"error": "Printer Increment Error"}, 400)

    # Email user that the print is complete
    result = email(job.user_id, job.print_name, 0)
    if not result:
        return custom_response({'error': 'user_id error'}, 404)

    # Change job values
    job_change_values = {
        "is_queued": False,
        "status": "complete",
        "date_ended" : datetime.datetime.now().isoformat()
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(ser_job, 200)


@print_job_api.route('/fail/<int:job_id>', methods=['PUT'])
def fail_queued_job(job_id):
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)

    # Check the job is running otherwise error
    if job.status != job_status.running:
        return custom_response({'error': "Job not running"}, 400)

    # Change job details
    printer_increment_values = {
        "total_time_printed": job.print_time,
        "failed_prints": 1,
        "total_filament_used": job.filament_usage
    }

    # Increment Printer Values
    ser_printer = increment_printer_details(
        printer_model.get_printer_by_id(job.printer), printer_increment_values)
    if ser_printer is None:
        return custom_response({"error": "Printer Increment Error"}, 400)

    # Email user that the print is complete
    result = email(job.user_id, job.print_name, 1)
    if not result:
        return custom_response({'error': 'user_id error'}, 404)

    # Change job values
    job_change_values = {
        "is_queued": False,
        "status": "failed",
        "date_ended" : datetime.now().isoformat()
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(ser_job, 200)


@print_job_api.route('/delete/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = print_job_model.get_print_job_by_id(job_id)
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    job.delete()
    return custom_response({'message': 'deleted'}, 200)


# Helper Functions
def filter_request_to_keys(req, keys):
    return {k: req[k] for k in keys if k in req}


def check_printer_id(printer_id):
    if (printer_model.get_printer_by_id(printer_id) is None):
        return False
    return True


def running_on_printer(printer_id):
    used_printer_ids = []
    running_jobs = print_job_model.get_print_jobs_by_status("running")
    for job in running_jobs:
        used_printer_ids.append(print_job_schema.dump(job)['printer'])
    if printer_id not in used_printer_ids:
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
        return custom_response({'error': "Jobs not found"}, 404)
    # This is jank af but it works and I can't think of a better way to do this lol
    jason = []
    for job in jobs:
        jason.append(print_job_schema.dump(job))
    return custom_response(jason, 200)


def update_job_details(job, req_data):
    # Try and load Job data to the schema
    try:
        data = print_job_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    job.update(data)
    ser_job = print_job_schema.dump(job)
    return custom_response(ser_job, 200)
