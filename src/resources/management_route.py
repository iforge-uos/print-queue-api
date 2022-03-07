from flask import Blueprint, request, render_template
from marshmallow.exceptions import ValidationError
from common.routing import custom_response
from common.auth import generate_hash_key, requires_access_level
from models.print_jobs import print_job_model, job_status
from models.user import user_model
from models.printers import printer_model, printer_type
from resources.user_route import calculate_level_from_score


management_view = Blueprint("management view", __name__)


@management_view.route('/', methods=['GET'])
def print_dashboard():
    """
    Gets the main print dashboard for the reps
    """
    args = request.args.to_dict()
    if len(args) == 0:
        return render_template('print_dashboard.j2', page_title="Print Dashboard", print_jobs=print_jobs_by_status('queued'), selected_status=job_status['queued'].value)
    status = args["status"]
    if status not in job_status._member_names_:
        return render_template('print_dashboard.j2', page_title="Print Dashboard")
    return render_template('print_dashboard.j2', page_title="Print Dashboard", print_jobs=print_jobs_by_status(status), selected_status=job_status[status].value)


@management_view.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    """
    Gets the user dashboard for the reps
    """
    return render_template('user_dashboard.j2', page_title="User Dashboard", users=user_model.get_all_users(), level_calculate=calculate_level_from_score)


@management_view.route('/view_stl', methods=['GET'])
def view_stl():
    """
    Loads the STL Viewer
    """
    return render_template('view_stl.j2', page_title="STL Viewer")


@management_view.route('/printer_dashboard', methods=['GET'])
def printer_dashboard():
    """
    Gets the printer dashboard for the reps
    """
    return render_template('printer_dashboard.j2', page_title="Printer Dashboard", printers=printer_model.get_all_printers())

@management_view.route('/print_upload', methods=['GET'])
def print_upload():
    """
    Gets the print_upload page
    """
    return render_template('print_upload.j2', page_title="Print Upload")


@management_view.route('/view_gcode', methods=['GET'])
def view_gcode():
    """
    Loads the GCODE Viewer
    """
    return render_template('view_gcode.j2', page_title="GCode Viewer")


def print_jobs_by_status(status) -> list:
    """
    Function to take print jobs and serialize them to a list
    :param status: status in the job_status enum
    :return list: list of jobs matching the status
    """
    if status not in job_status._member_names_:
        return []
    jason = []
    for job in print_job_model.get_print_jobs_by_status(status):
        jason.append(job)
    return jason
