from flask import Blueprint, request, render_template, current_app
from marshmallow.exceptions import ValidationError
from print_api.common.routing import custom_response
from print_api.common.auth import generate_hash_key, requires_access_level
from print_api.models.print_jobs import print_job_model, job_status, project_types
from print_api.models.user import user_model
from print_api.models.printers import printer_model, printer_type
from print_api.resources.api_routes.user_route import calculate_level_from_score


user_view = Blueprint("user view", __name__)


@user_view.route('/', methods=['GET'])
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


@user_view.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    """
    Gets the user dashboard for the reps
    """
    return render_template('user_dashboard.j2', page_title="User Dashboard", users=user_model.get_all_users(), level_calculate=calculate_level_from_score)


@user_view.route('/view_stl', methods=['GET'])
def view_stl():
    """
    Loads the STL Viewer
    """
    return render_template('view_stl.j2', page_title="STL Viewer")


@user_view.route('/printer_dashboard', methods=['GET'])
def printer_dashboard():
    """
    Gets the printer dashboard for the reps
    """
    return render_template('printer_dashboard.j2', page_title="Printer Dashboard", printers=printer_model.get_all_printers())

@user_view.route('/print_upload', methods=['GET', 'POST'])
def print_upload():
    """
    Gets the print_upload page
    """
    selected_project = request.form['project_type'] if 'project_type' in request.form else "personal"
    current_app.logger.debug("Selected project: %s", selected_project)
    return render_template('print_upload.j2', page_title="Print Upload", project_types=project_types, selected_project=selected_project)


@user_view.route('/view_gcode', methods=['GET'])
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
