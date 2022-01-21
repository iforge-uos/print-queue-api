from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from common.auth import requires_access_level
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
USERIDERROR = "user not found"


@print_job_api.route('/add', methods=['POST'])
@requires_access_level(1)
def create():
    """
    Function to create a new job from json sent in the POST request
    :return response: error or success message
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
        req_data.pop("checked_by")

    # Tidying up some null values to make future functions easier
    if "filament_usage" not in req_data:
        req_data.__setitem__("filament_usage", 0)
    if "print_time" not in req_data:
        req_data.__setitem__("print_time", 0)

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
@requires_access_level(1)
def view_job_single(job_id):
    """
    Function return a serialized job by its id
    :param int job_id: PK of the job record to retrieve
    :return response: error or serialized job
    """
    return get_single_job_details(print_job_model.get_print_job_by_id(job_id))


@print_job_api.route('/view/all/<string:status>', methods=['GET'])
@requires_access_level(1)
def view_jobs_by_status(status):
    """
    Function to return a list of serialized jobs filtered by their status
    :param str status: status from the job_status enum of which status to filter by
    :return response: error or list of serialized jobs matching filter
    """
    # Sanity check url
    if status not in job_status._member_names_:
        return custom_response({"error": "Status not found"}, 404)
    # Return a list of jason objects that match status query
    return get_multiple_job_details(
        print_job_model.get_print_jobs_by_status(status))


@print_job_api.route('/approve/accept/<int:job_id>', methods=['PUT'])
@requires_access_level(2)
def accept_awaiting_job(job_id):
    """
    Function to mark an awaited job asapproved and add to the queue
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)

    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    if job.status != job_status.awaiting:
        return custom_response({'error': "wrong job status"}, 400)
    return update_job_details(job, {"status": "queued"})


@print_job_api.route('/approve/reject/<int:job_id>', methods=['PUT'])
@requires_access_level(2)
def reject_awaiting_job(job_id):
    """
    Function to mark an awaited job asapproved and add to the queue
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    if job.status != job_status.awaiting:
        return custom_response({'error': "wrong job status"}, 400)
    result = email(job.user_id, job.print_name, 2)
    if not result:
        return custom_response({'error': USERIDERROR}, 404)
    return update_job_details(job, {"status": "rejected"})


@print_job_api.route('/start/<int:job_id>', methods=['PUT'])
@requires_access_level(2)
def start_queued_job(job_id):
    """
    Function to mark a print job as started if the printer selected is not already in use.
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
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
    if printer_model.get_printer_by_id(
            printer_id).printer_type != job.printer_type:
        return custom_response({'error': "Printer Type mismatch"}, 400)
    if running_on_printer(printer_id):
        return custom_response({'error': "Associated Printer is in use"}, 400)

    request_dict['status'] = "running"
    request_dict['date_started'] = datetime.now().isoformat()
    return update_job_details(job, request_dict)


@print_job_api.route('/complete/<int:job_id>', methods=['PUT'])
@requires_access_level(2)
def complete_queued_job(job_id):
    """
    Function to mark a print job as completed, email the user and change the printer telemetry
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
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
        return custom_response({'error': USERIDERROR}, 404)

    # Change job values
    job_change_values = {
        "is_queued": False,
        "status": "complete",
        "date_ended": datetime.now().isoformat()
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
@requires_access_level(2)
def fail_queued_job(job_id):
    """
    Function to mark a print job as failed, email the user and change the printer telemetry
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
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
        return custom_response({'error': USERIDERROR}, 404)

    # Change job values
    job_change_values = {
        "is_queued": False,
        "status": "failed",
        "date_ended": datetime.now().isoformat()
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
@requires_access_level(3)
def delete_job(job_id):
    """
    Function to take a job ID and delete it from the database
    :param int job_id: PK of the record in the database.
    :return response: error or confirmation message
    """
    job = print_job_model.get_print_job_by_id(job_id)
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    job.delete()
    return custom_response({'message': 'deleted'}, 200)


# Helper Functions
def filter_request_to_keys(req, keys):
    """
    Function to take a dict and a list of keys and return the dict containing only the keys supplied
    :param dict req: the request dictionary that is to be filtered
    :param list keys: a list of keys to filter by
    :return dict: the filtered dictionary
    """
    return {k: req[k] for k in keys if k in req}


def check_printer_id(printer_id):
    """
    Function to verify that a printer_id exists in the datbase
    :param int printer_id: PK of the printer to search for
    :return bool result: true if it exists, false otherwise
    """
    if (printer_model.get_printer_by_id(printer_id) is None):
        return False
    return True


def running_on_printer(printer_id):
    """
    Function to check if a job is running on the same printer as another printer
    :param int printer_id: ID of the printer to be checked
    :return bool result: true if it is running on another printer (therefore do not run the job) or False if it is not
    """
    used_printer_ids = []
    running_jobs = print_job_model.get_print_jobs_by_status("running")
    for job in running_jobs:
        used_printer_ids.append(print_job_schema.dump(job)['printer'])
    if printer_id not in used_printer_ids:
        return False
    return True


def check_user_id(user_id):
    """
    Function to verify a users level.
    :param int user_id: user PK to lookup in the user_database
    :return str user_level: the level of the user or None if it does not exist
    """
    user = user_model.get_user_by_id(user_id)
    if (user is None):
        return None
    return user.user_level


def check_rep_id(user_id):
    """
    Function to verify if a user is a rep or not.
    :param int user_id: PK of the user to be checked
    :return bool result: true if successful, false otherwise
    """
    user = user_model.get_user_by_id(user_id)
    if (user is None or user.is_rep == False):
        return False
    return True


def get_single_job_details(job):
    """
    Function to take a job object and serialize it.
    :param job: the job object
    :return response: error or the serialized object
    """
    if not job:
        return custom_response({'error': NOTFOUNDJOB}, 404)
    ser_job = print_job_schema.dump(job)
    print(ser_job)
    return custom_response(ser_job, 200)


def get_multiple_job_details(jobs):
    """
    Function to take a query object of multiple print jobs and serialize them
    :param jobs: the query object containing print jobs
    :return response: error or a list of serialized print jobs
    """
    if not jobs:
        return custom_response({'error': "Jobs not found"}, 404)
    jason = []
    for job in jobs:
        jason.append(print_job_schema.dump(job))
    return custom_response(jason, 200)


def update_job_details(job, req_data):
    """
    Function to update the details of a job by a request.
    :param job: the job object to be updated
    :param dict req_data: the http body containing the data to be updated
    :return response: error or the serialized updated print job
    """
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
