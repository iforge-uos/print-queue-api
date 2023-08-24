import re
from datetime import datetime

from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError

from print_api.common.emails import email
from print_api.common.routing import custom_response
from print_api.models import PrintJob, PrintJobSchema, Printer, User
from print_api.models.print_jobs import JobStatus
from print_api.resources.api_routes.printer_route import increment_printer_details

print_job_api = Blueprint("print jobs", __name__)
print_job_schema = PrintJobSchema()

JOB_NOT_FOUND = "job(s) not found"
USER_ID_ERROR = "user(s) not found"
STATUS_ERROR = "status not found"


@print_job_api.route("/add", methods=["POST"])
@jwt_required()
def create():
    req_data = request.get_json()

    user_level = check_user_id(req_data["user_id"])
    validation_error = validate_create_input(req_data)
    if validation_error:
        return validation_error

    prepared_data = prepare_create_data(req_data, user_level)
    if isinstance(prepared_data, tuple):  # check if it's an error response
        return prepared_data

    try:
        data = print_job_schema.load(prepared_data)
    except ValidationError as err:
        return custom_response(status_code=400, details=err.messages)

    job = PrintJob(data)
    job.save()
    return custom_response(
        status_code=200, extra_info="success", details=print_job_schema.dump(job)
    )


@print_job_api.route("/view/<int:job_id>", methods=["GET"])
@jwt_required()
def view_job_single(job_id):
    """
    Function return a serialized job by its id
    :param int job_id: PK of the job record to retrieve
    :return response: error or serialized job
    """
    return get_single_job_details(PrintJob.get_print_job_by_id(job_id))


@print_job_api.route("/view/<string:status>", methods=["GET"])
@jwt_required()
def view_jobs_by_status(status):
    """
    Function to return a list of serialized jobs filtered by their status
    :param str status: status from the job_status enum of which status to filter by
    :return response: error or list of serialized jobs matching filter
    """
    # Sanity check url
    if status not in JobStatus._member_names_:
        return custom_response(status_code=400, details=STATUS_ERROR)
    # Return a list of jason objects that match status query
    return get_multiple_job_details(PrintJob.get_print_jobs_by_status(status))


@print_job_api.route("/approve/accept/<int:job_id>", methods=["PUT"])
@jwt_required()
def accept_approval_job(job_id):
    job = PrintJob.get_print_job_by_id(job_id)

    validation_error = validate_job_exists(job)
    if validation_error:
        return validation_error

    validation_error = validate_job_status(job, JobStatus.approval)
    if validation_error:
        return validation_error

    return update_job_details(job, {"status": "queued"})


@print_job_api.route("/approve/reject/<int:job_id>", methods=["PUT"])
@jwt_required()
def reject_approval_job(job_id):
    job = PrintJob.get_print_job_by_id(job_id)

    validation_error = validate_job_exists(job)
    if validation_error:
        return validation_error

    validation_error = validate_job_status(job, JobStatus.approval)
    if validation_error:
        return validation_error

    result = email(job.user_id, job.print_name, "rejected")
    if not result:
        return custom_response(status_code=404, details=USER_ID_ERROR)

    return update_job_details(job, {"status": "rejected"})


@print_job_api.route("/start/<int:job_id>", methods=["PUT"])
@jwt_required()
def start_queued_job(job_id):
    req_data = request.get_json()
    request_dict = validate_start_queued_input(req_data)

    job = PrintJob.get_print_job_by_id(job_id)

    validation_error = validate_job_exists(job)
    if validation_error:
        return validation_error

    validation_error = validate_job_status(job, JobStatus.queued)
    if validation_error:
        return validation_error

    validation_error = validate_printer(request_dict["printer"], job)
    if validation_error:
        return validation_error

    request_dict["status"] = JobStatus.running.name
    request_dict["date_started"] = datetime.now().isoformat()
    return update_job_details(job, request_dict)


@print_job_api.route("/complete/<int:job_id>", methods=["PUT"])
@jwt_required()
def complete_job(job_id):
    job = PrintJob.get_print_job_by_id(job_id)

    validation_error = validate_job_exists(job)
    if validation_error:
        return validation_error

    validation_error = validate_job_status(job, JobStatus.running)
    if validation_error:
        return validation_error

    printer_increment_values = {
        "total_time_printed": job.print_time,
        "completed_prints": 1,
        "total_filament_used": job.filament_usage,
    }
    validation_error = update_printer_telemetry(job, printer_increment_values)
    if validation_error:
        return validation_error

    validation_error = update_user_and_rep_scores(job)
    if validation_error:
        return validation_error

    job_change_values = {
        "status": JobStatus.completed.name,
        "date_ended": datetime.now().isoformat(),
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        return custom_response(status_code=400, details=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, details=ser_job, extra_info="success")


@print_job_api.route("/fail/<int:job_id>", methods=["PUT"])
@jwt_required()
def fail_job(job_id):
    requeue = request.args.get("requeue", default="no")
    job = PrintJob.get_print_job_by_id(job_id)

    validation_error = validate_input(requeue, job)
    if validation_error:
        return validation_error

    if handle_printer_details(job) is None:
        return custom_response(status_code=400, details="Printer Increment Error")

    job_change_values = handle_requeue(job) if requeue == "yes" else handle_failure(job)

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        return custom_response(status_code=400, details=err.messages)

    job.update(data)
    ser_job = print_job_schema.dump(job)
    return custom_response(status_code=200, details=ser_job, extra_info="success")


@print_job_api.route("/reject/<int:job_id>", methods=["PUT"])
@jwt_required()
def reject_job(job_id):
    """
    Function to mark a print job as rejected and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = PrintJob.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)

    # Check the job is queued or under-review
    if job.status not in [JobStatus.queued, JobStatus.under_review]:
        return custom_response(
            status_code=400, details="Job not under-review (or queued)"
        )

    job_change_values = {
        "status": JobStatus.rejected.name,
        "date_ended": datetime.now().isoformat(),
    }

    # Email user that the print is failed
    result = email(job.user_id, job.print_name, status="rejected")
    if not result:
        return custom_response(status_code=404, details=USER_ID_ERROR)

    # Update score of user and slicing rep
    result = score_print(job.user_id, job.rep_check, status="rejected")
    if not result:
        return custom_response(status_code=404, details=STATUS_ERROR)

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, details=ser_job, extra_info="success")


@print_job_api.route("/queue/<int:job_id>", methods=["PUT"])
@jwt_required()
def queue_job(job_id):
    """
    Function to mark a print job as queued and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = PrintJob.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)

    # Check the job is queued or under-review
    if job.status is not JobStatus.under_review:
        return custom_response(status_code=400, details="Job not under-review")

    job_change_values = {
        "status": JobStatus.queued.name,
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, details=ser_job, extra_info="success")


@print_job_api.route("/review/<int:job_id>", methods=["PUT"])
@jwt_required()
def review_job(job_id):
    """
    Function to mark a print job as under-review and email the user
    :param int job_id: PK of the print_job record
    :return response: error or serialized updated job record
    """
    job = PrintJob.get_print_job_by_id(job_id)
    # Check job exists
    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)

    # Check the job is queued or under-review
    if job.status is not JobStatus.queued:
        return custom_response(status_code=400, details="Job not queued")

    job_change_values = {
        "status": JobStatus.under_review.name,
    }

    try:
        data = print_job_schema.load(job_change_values, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)

    return custom_response(status_code=200, details=ser_job, extra_info="success")


@print_job_api.route("/delete/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    """
    Function to take a job ID and delete it from the database
    :param int job_id: PK of the record in the database.
    :return response: error or confirmation message
    """
    job = PrintJob.get_print_job_by_id(job_id)
    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)
    job.delete()
    return custom_response(status_code=200, extra_info="deleted")


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
    if Printer.get_printer_by_id(printer_id) is None:
        return False
    return True


def running_on_printer(printer_id):
    """
    Function to check if a job is running on the same printer as another printer
    :param int printer_id: ID of the printer to be checked
    :return bool result: true if it is running on another printer (therefore do not run the job) or False if it is not
    """
    used_printer_ids = []
    running_jobs = PrintJob.get_print_jobs_by_status("running")
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
    user = User.get_user_by_id(user_id)
    if user is None:
        return None
    user_level = User.calculate_level_from_score(user.user_score)
    return user_level


def check_rep_id(user_id):
    """
    Function to verify if a user is a rep or not.
    :param int user_id: PK of the user to be checked
    :return bool result: true if successful, false otherwise
    """
    user = User.get_user_by_id(user_id)
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
        return custom_response(status_code=404, details=JOB_NOT_FOUND)
    ser_job = print_job_schema.dump(job)
    return custom_response(status_code=200, details=ser_job, extra_info="success")


def get_multiple_job_details(jobs):
    """
    Function to take a query object of multiple print jobs and serialize them
    :param jobs: the query object containing print jobs
    :return response: error or a list of serialized print jobs
    """
    if not jobs:
        return custom_response(status_code=404, details="Jobs not found")
    jason = []
    final_res = {"print_jobs": jason}
    for job in jobs:
        jason.append(print_job_schema.dump(job))
    return custom_response(status_code=200, details=final_res, extra_info="success")


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
        return custom_response(status_code=400, details=err.messages)
    job.update(data)
    ser_job = print_job_schema.dump(job)
    return custom_response(status_code=200, details=ser_job, extra_info="success")


def score_print(user_id, rep_id, status):
    """
    :param str status: Either "completed", "failed" or "rejected".
    """
    score_increments = {"completed": 1, "failed": -1, "rejected": -1}

    if status not in score_increments.keys():
        return False

    user = User.get_user_by_id(user_id)
    rep = User.get_user_by_id(rep_id)

    user_data = {}
    rep_data = {}

    # increment '{status}_count' (eg.'completed_count') depending on print outcome
    user_data[f"{status}_count"] = getattr(user, f"{status}_count") + 1
    user_data["user_score"] = user.user_score + score_increments[status]
    rep_data[f"slice_{status}_count"] = getattr(user, f"slice_{status}_count") + 1

    if user_data["user_score"] < 1:
        user_data["user_score"] = 1
    user_data["new_level"] = User.calculate_level_from_score(user_data["user_score"])

    user.update(user_data)
    rep.update(rep_data)

    return True


def validate_user(req_data):
    user_level = check_user_id(req_data["user_id"])
    if user_level is None:
        return None, custom_response(status_code=400, details="user is not found")
    return user_level, None


def validate_rep(req_data, user_level):
    if "rep_check" not in req_data:
        req_data["rep_check"] = req_data["user_id"]
    if not check_rep_id(req_data["rep_check"]) and user_level == "basic":
        return custom_response(
            status_code=400, details="rep is incorrect or not permitted to check prints"
        )
    return None


def set_request_status(req_data, user_level):
    if user_level == "advanced":
        req_data["status"] = "approval"
        if "stl_slug" not in req_data:
            return custom_response(status_code=404, details="stl slug needed")
    else:
        req_data["status"] = "queued"
    return None


def set_default_values(req_data):
    if "filament_usage" not in req_data:
        req_data["filament_usage"] = 0
    if "print_time" not in req_data:
        req_data["print_time"] = 0


def validate_job_exists(job):
    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)
    return None


def validate_job_status(job, expected_status):
    if job.status != expected_status:
        return custom_response(
            status_code=400, details=f"Disallowed status. Expected {expected_status}."
        )
    return None


def validate_create_input(req_data):
    user_level = check_user_id(req_data["user_id"])
    if user_level is None:
        return custom_response(status_code=400, details="user is not found")

    if "rep_check" not in req_data:
        req_data["rep_check"] = req_data["user_id"]

    if not check_rep_id(req_data["rep_check"]) and user_level == "basic":
        return custom_response(
            status_code=400, details="rep is incorrect or not permitted to check prints"
        )
    return None


def prepare_create_data(req_data, user_level):
    if user_level == "advanced":
        req_data["status"] = "approval"
        if "stl_slug" not in req_data:
            return custom_response(status_code=404, details="stl slug needed")
    else:
        req_data["status"] = "queued"

    req_data.setdefault("filament_usage", 0)
    req_data.setdefault("print_time", 0)
    return req_data


def validate_start_queued_input(req_data):
    required_keys = ["colour", "printer"]
    request_dict = filter_request_to_keys(req_data, required_keys)
    return request_dict


def validate_printer(printer_id, job):
    if not check_printer_id(printer_id):
        return custom_response(status_code=404, details="Printer Not Found")
    if Printer.get_printer_by_id(printer_id).PrinterType != job.PrinterType:
        return custom_response(status_code=400, details="Printer Type mismatch")
    if running_on_printer(printer_id):
        return custom_response(status_code=400, details="Associated Printer is in use")
    return None


def update_printer_telemetry(job, printer_increment_values):
    ser_printer = increment_printer_details(
        Printer.get_printer_by_id(job.printer), printer_increment_values
    )
    if ser_printer is None:
        return custom_response(status_code=400, details="Printer Increment Error")
    return None


def update_user_and_rep_scores(job):
    result = email(job.user_id, job.print_name, status="completed")
    if not result:
        return custom_response(status_code=404, details=USER_ID_ERROR)

    result = score_print(job.user_id, job.rep_check, status="completed")
    if not result:
        return custom_response(status_code=404, details=STATUS_ERROR)
    return None


def validate_input(requeue, job):
    if requeue not in ["yes", "no"]:
        return custom_response(
            status_code=400,
            details="Invalid Parameters in Request",
            extra_info="Requeue needs to be yes or no",
        )

    if not job:
        return custom_response(status_code=404, details=JOB_NOT_FOUND)

    if job.status != JobStatus.running:
        return custom_response(status_code=400, details="Job not running")
    return None


def handle_printer_details(job):
    printer_increment_values = {
        "total_time_printed": job.print_time,
        "failed_prints": 1,
        "total_filament_used": job.filament_usage,
    }

    return increment_printer_details(
        Printer.get_printer_by_id(job.printer), printer_increment_values
    )


def handle_requeue(job):
    queue_notes = job.queue_notes.splitlines()
    requeue_lines = [x for x in queue_notes if "Requeue #" in x]
    if not requeue_lines:
        queue_notes.append("Requeue #1")
    else:
        requeue_n = int(re.findall(r"\d+", requeue_lines[-1])[0])
        queue_notes.append(f"Requeue #{requeue_n + 1}")

    return {"status": JobStatus.queued.name, "queue_notes": "\n".join(queue_notes)}


def handle_failure(job):
    email_result = email(job.user_id, job.print_name, status="failed")
    score_result = score_print(job.user_id, job.rep_check, status="failed")

    if not email_result:
        return custom_response(status_code=404, details=USER_ID_ERROR)
    if not score_result:
        return custom_response(status_code=404, details=STATUS_ERROR)

    return {
        "status": JobStatus.failed.name,
        "date_ended": datetime.now().isoformat(),
    }
