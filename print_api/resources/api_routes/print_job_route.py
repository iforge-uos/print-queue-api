import re
from flask_jwt_extended import jwt_required
from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from print_api.resources.api_routes.printer_route import increment_printer_details
from print_api.models.print_jobs import (
    print_job_model,
    print_job_schema,
    project_types,
    job_status,
)
from print_api.models.printers import printer_model
from print_api.models.user import user_model
from print_api.resources.api_routes.user_route import calculate_level_from_score
from print_api.common.routing import custom_response
from print_api.common.emails import email
from datetime import datetime

print_job_api = Blueprint("print jobs", __name__)
print_job_schema = print_job_schema()

JOBNOTFOUND = "job(s) not found"
USERIDERROR = "user(s) not found"
STATUSERROR = "status not found"

# TODO ADD CANCELLING JOBS


@print_job_api.route("/add", methods=["POST"])
@jwt_required()
def create():
    """
    Function to create a new job from json sent in the POST request
    :return response: error or success message
    """
    req_data = request.get_json()

    # Get user level
    user_level = check_user_id(req_data["user_id"])
    if user_level is None:
        return custom_response(status_code=404, data="user is not found")

    if "rep_check" not in req_data:
        req_data["rep_check"] = req_data["user_id"]

    if not check_rep_id(req_data["rep_check"]):
        return ({"error": "rep is incorrect or not permitted to check prints"}, 404)

    if user_level == "advanced":
        req_data["status"] = "approval"
        if not "stl_slug" in req_data:
            return ({"error": "stl slug needed"}, 404)
    else:
        req_data["status"] = "queued"

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
        return custom_response(status_code=400, data=err.messages)

    job = print_job_model(data)
    job.save()
    return custom_response(status_code=200, data="success")


@print_job_api.route("/view/<int:job_id>", methods=["GET"])
@jwt_required()
def view_job_single(job_id):
    """
    Function return a serialized job by its id
    :param int job_id: PK of the job record to retrieve
    :return response: error or serialized job
    """
    return get_single_job_details(print_job_model.get_print_job_by_id(job_id))


@print_job_api.route("/view/<string:status>", methods=["GET"])
@jwt_required()
def view_jobs_by_status(status):
    """
    Function to return a list of serialized jobs filtered by their status
    :param str status: status from the job_status enum of which status to filter by
    :return response: error or list of serialized jobs matching filter
    """
    # Sanity check url
    if status not in job_status._member_names_:
        return custom_response(404, {"error": "Status not found"})
    # Return a list of jason objects that match status query
    return get_multiple_job_details(print_job_model.get_print_jobs_by_status(status))


@print_job_api.route("/approve/accept/<int:job_id>", methods=["PUT"])
@jwt_required()
def accept_approval_job(job_id):
    """
    Function to mark an awaited job asapproved and add to the queue
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)

    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)
    if job.status != job_status.approval:
        return custom_response(status_code=400, data="wrong job status")
    return update_job_details(job, {"status": "queued"})


@print_job_api.route("/approve/reject/<int:job_id>", methods=["PUT"])
@jwt_required()
def reject_approval_job(job_id):
    """
    Function to mark an awaited job asapproved and add to the queue
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)
    if job.status != job_status.approval:
        return custom_response(status_code=400, data="wrong job status")
    result = email(job.user_id, job.print_name, 2)
    if not result:
        return custom_response(status_code=404, data=USERIDERROR)
    return update_job_details(job, {"status": "rejected"})


@print_job_api.route("/start/<int:job_id>", methods=["PUT"])
@jwt_required()
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
        return custom_response(status_code=404, data=JOBNOTFOUND)
    # Check job is allowed to run
    if job.status != job_status.queued:
        return custom_response(status_code=400, data="Job Cannot be run")
    printer_id = request_dict["printer"]
    if not check_printer_id(printer_id):
        return custom_response(status_code=404, data="Printer Not Found")
    if printer_model.get_printer_by_id(printer_id).printer_type != job.printer_type:
        return custom_response(status_code=400, data="Printer Type mismatch")
    if running_on_printer(printer_id):
        return custom_response(status_code=400, data="Associated Printer is in use")

    request_dict["status"] = job_status.running.name
    request_dict["date_started"] = datetime.now().isoformat()
    return {'success': update_job_details(job, request_dict)}


@print_job_api.route("/complete/<int:job_id>", methods=["PUT"])
@jwt_required()
def complete_job(job_id):
    """
    Function to mark a print job as completed, email the user and change the printer telemetry
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)

    # Check the job is running otherwise error
    if job.status != job_status.running:
        return custom_response(status_code=400, data="Job not running")

    # Change job details
    printer_increment_values = {
        "total_time_printed": job.print_time,
        "completed_prints": 1,
        "total_filament_used": job.filament_usage,
    }

    # Increment Printer Values
    ser_printer = increment_printer_details(
        printer_model.get_printer_by_id(job.printer), printer_increment_values
    )
    if ser_printer is None:
        return custom_response(status_code=400, data="Printer Increment Error")

    # Change job values
    job_change_values = {
        "status": job_status.completed.name,
        "date_ended": datetime.now().isoformat(),
    }

    # Email user that the print is failed
    result = email(job.user_id, job.print_name, status='completed')
    if not result:
        return custom_response(status_code=404, data=USERIDERROR)

    # Update score of user and slicing rep
    result = score_print(job.user_id, job.rep_check, status='completed')
    if not result:
        return custom_response(status_code=404, data=STATUSERROR)

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, data=ser_job)


@print_job_api.route("/fail/<int:job_id>", methods=["PUT"])
@jwt_required()
def fail_job(job_id):
    """
    Function to fail a print job (with the option to requeue), email the user, update scores, and change the printer telemetry
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    requeue = request.args.get("requeue", default="no")

    if requeue not in ["yes", "no"]:
        return custom_response(status_code=400, data="Invalid Parameters in Request: Requeue needs to be yes or no")

    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)

    # Check the job is running otherwise error
    if job.status != job_status.running:
        return custom_response(status_code=400, data="Job not running")

    # Change job details
    printer_increment_values = {
        "total_time_printed": job.print_time,
        "failed_prints": 1,
        "total_filament_used": job.filament_usage,
    }

    # Increment Printer Values
    ser_printer = increment_printer_details(
        printer_model.get_printer_by_id(job.printer), printer_increment_values
    )
    if ser_printer is None:
        return custom_response(status_code=400, data="Printer Increment Error")

    # Change job values depending on requeue
    if requeue == "yes":
        queue_notes = job.queue_notes.splitlines()
        # if notes are list of entries: ['irrelevant', 'Requeue #N', 'irrelevant', ...]
        requeue_idx = [i for i, x in enumerate(queue_notes) if re.findall(r'(?<=[Rr]equeue \#)\d+', x) != []]
        if len(requeue_idx) == 0:
            # Not been requeued before, add requeue count marker
            queue_notes.append("Requeue #1")
        else:
            # increase and append requeue count marker to notes
            requeue_n = int(requeue_idx[-1])
            queue_notes.append(f"Requeue #{requeue_n + 1}")

        job_change_values = {
            "status": job_status.queued.name,
            "queue_notes": '\n'.join(queue_notes)
        }

    else:
        job_change_values = {
            "status": job_status.failed.name,
            "date_ended": datetime.now().isoformat(),
        }
        # Email user that the print is failed
        result = email(job.user_id, job.print_name, status='failed')
        if not result:
            return custom_response(status_code=404, data=USERIDERROR)

        # Update score of user and slicing rep
        result = score_print(job.user_id, job.rep_check, status='failed')
        if not result:
            return custom_response(status_code=404, data=STATUSERROR)

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, data=ser_job)


@print_job_api.route("/reject/<int:job_id>", methods=["PUT"])
@jwt_required()
def reject_job(job_id):
    """
    Function to mark a print job as rejected and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)

    # Check the job is queued or under-review
    if job.status not in [job_status.queued, job_status.under_review]:
        return custom_response(status_code=400, data="Job not under-review (or queued)")

    job_change_values = {
        "status": job_status.rejected.name,
        "date_ended": datetime.now().isoformat(),
    }

    # Email user that the print is failed
    result = email(job.user_id, job.print_name, status='rejected')
    if not result:
        return custom_response(status_code=404, data=USERIDERROR)

    # Update score of user and slicing rep
    result = score_print(job.user_id, job.rep_check, status='rejected')
    if not result:
        return custom_response(status_code=404, data=STATUSERROR)

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, data=ser_job)


@print_job_api.route("/queue/<int:job_id>", methods=["PUT"])
@jwt_required()
def queue_job(job_id):
    """
    Function to mark a print job as queued and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)

    # Check the job is queued or under-review
    if job.status is not job_status.under_review:
        return custom_response(status_code=400, data="Job not under-review")

    job_change_values = {
        "status": job_status.queued.name,
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, data=ser_job)


@print_job_api.route("/review/<int:job_id>", methods=["PUT"])
@jwt_required()
def review_job(job_id):
    """
    Function to mark a print job as under-review and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = print_job_model.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)

    # Check the job is queued or under-review
    if job.status is not job_status.queued:
        return custom_response(status_code=400, data="Job not queued")

    job_change_values = {
        "status": job_status.under_review.name,
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, data=ser_job)

@print_job_api.route("/delete/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    """
    Function to take a job ID and delete it from the database
    :param int job_id: PK of the record in the database.
    :return response: error or confirmation message
    """
    job = print_job_model.get_print_job_by_id(job_id)
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)
    job.delete()
    return custom_response(status_code=200, data="deleted")


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
    if printer_model.get_printer_by_id(printer_id) is None:
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
        used_printer_ids.append(print_job_schema.dump(job)["printer"])
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
    if user is None:
        return None
    user_level = calculate_level_from_score(user.user_score)
    return user_level


def check_rep_id(user_id):
    """
    Function to verify if a user is a rep or not.
    :param int user_id: PK of the user to be checked
    :return bool result: true if successful, false otherwise
    """
    user = user_model.get_user_by_id(user_id)
    if user is None or user.is_rep is False:
        return False
    return True


def get_single_job_details(job):
    """
    Function to take a job object and serialize it.
    :param job: the job object
    :return response: error or the serialized object
    """
    if not job:
        return custom_response(status_code=404, data=JOBNOTFOUND)
    ser_job = print_job_schema.dump(job)
    return custom_response(status_code=200, data=ser_job)


def get_multiple_job_details(jobs):
    """
    Function to take a query object of multiple print jobs and serialize them
    :param jobs: the query object containing print jobs
    :return response: error or a list of serialized print jobs
    """
    if not jobs:
        return custom_response(status_code=404, data="Jobs not found")
    jason = []
    for job in jobs:
        jason.append(print_job_schema.dump(job))
    return custom_response(status_code=200, data=jason)


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
        return custom_response(status_code=400, data=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)
    return custom_response(status_code=200, data=ser_job)

def score_print(user_id, rep_id, status):
    """
    :param str status: Either "completed", "failed" or "rejected".
    """
    score_increments = {'completed': 1, 'failed': -1, 'rejected': -1}

    if status not in score_increments.keys():
        return False

    user = user_model.get_user_by_id(user_id)
    rep = user_model.get_user_by_id(rep_id)

    user_data = {}
    rep_data = {}

    # increment '{status}_count' (eg.'completed_count') depending on print outcome
    user_data[f"{status}_count"] = getattr(user, f"{status}_count") + 1
    user_data['user_score'] = user.user_score + score_increments[status]
    rep_data[f"slice_{status}_count"] = getattr(user, f"slice_{status}_count") + 1

    if user_data['user_score'] < 1:
        user_data['user_score'] = 1
    user_data['new_level'] = calculate_level_from_score(user_data['user_score'])

    user.update(user_data)
    rep.update(rep_data)

    return True
