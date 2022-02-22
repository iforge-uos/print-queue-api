from flask import Blueprint, request, render_template
from marshmallow.exceptions import ValidationError
from common.routing import custom_response
from common.auth import generate_hash_key, requires_access_level
from models.print_jobs import print_job_schema, print_job_model, job_status


management_view = Blueprint("management view", __name__)


@management_view.route('/', methods=['GET'])
def home_page():
    """
    Gets the main print dashboard for the reps
    """
    return render_template('base_layout.html', page_title="Home")


@management_view.route('/print_dashboard', methods=['GET'])
def print_dashboard():
    """
    Gets the main print dashboard for the reps
    """
    args = request.args.to_dict()
    if len(args) == 0:
        return render_template('print_dashboard.html', page_title="Print Dashboard")
    status = args["status"]
    if status not in job_status._member_names_:
        return render_template('print_dashboard.html', page_title="Print Dashboard")
    return render_template('print_dashboard.html', page_title="Print Dashboard", print_jobs=print_jobs_by_status(status), selected_status=job_status[status].value)


def print_jobs_by_status(status) -> list:
    if status not in job_status._member_names_:
        return []
    jason = []
    for job in print_job_model.get_print_jobs_by_status(status):
        jason.append(job)
    return jason
