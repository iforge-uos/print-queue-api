from flask_jwt_extended import jwt_required

from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from print_api.models import Printer, MaintenanceLog, maintenance_schema
from print_api.common.routing import custom_response

maintenance_api = Blueprint('maintenance logs', __name__)
maintenance_schema = maintenance_schema()

NOTFOUNDMAINTENANCE = "maintenance log(s) not found"


@maintenance_api.route('/update/<int:log_id>', methods=['PUT'])
@jwt_required()
def update_by_id(log_id):
    """
    Function to update a logs details.
    :param int log_id: PK of the log record to update
    :return response: error or serialized updated log
    """
    req_data = request.get_json()
    log = MaintenanceLog.get_maintenance_log_by_id(log_id)
    return update_log_details(log, req_data)


@maintenance_api.route('/view/single/<int:log_id>', methods=['GET'])
@jwt_required()
def view_single_by_id(log_id):
    """
    Function to get a single log via its ID
    :param int log_id: PK of the log record to retrieve
    :return response: error or serialized log
    """
    return get_log_details(MaintenanceLog.get_maintenance_log_by_id(log_id))


@maintenance_api.route('/view/all/<string:printer_name>', methods=['GET'])
@jwt_required()
def view_all_by_printer_name(printer_name):
    """
    Get all logs via their linked printers name
    :param str printer_name: name of the printer
    :return response: an error or the serialized printers
    """
    # First check if the printer_name is valid
    printer = Printer.get_printer_by_name(printer_name)
    if printer is None:
        return custom_response(status_code=404, details="Printer not found")

    # Then return the jason payload of any logs for that printer
    return get_multiple_log_details(
        MaintenanceLog.get_maintenance_logs_by_printer_id(printer.id))


@maintenance_api.route('/view/all/<int:printer_id>', methods=['GET'])
@jwt_required()
def view_all_by_printer_id(printer_id):
    """
    Get all logs via their linked printers name
    :param int printer_id: PK ID of the printer
    :return response: an error or the serialized printers
    """
    return get_multiple_log_details(
        MaintenanceLog.get_maintenance_logs_by_printer_id(printer_id))


@maintenance_api.route('/delete/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_by_id(log_id):
    """
    Delete a single log via its ID
    :param int log_id: the PK of the log
    :return response: error or a success message
    """
    return delete_log(MaintenanceLog.get_maintenance_log_by_id(log_id))


@maintenance_api.route('/add', methods=['POST'])
@jwt_required()
def create():
    """
    Create Log Function
    :return response: error or a success message
    """
    req_data = request.get_json()

    # Check if printer_id exists
    printer_id = req_data['printer_id']
    if Printer.get_printer_by_id(printer_id) is None:
        return custom_response(status_code=404, details="Printer is not found")

    # Try and load the data into the model
    try:
        data = maintenance_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)

    log = MaintenanceLog(data)
    log.save()
    return custom_response(status_code=200, extra_info="success", details=maintenance_schema.dump(log))


def delete_log(log):
    """
    Function to check if the log exists then delete it
    :param log: the log object
    :return response: error or a success message
    """
    if not log:
        return custom_response(status_code=404, details=NOTFOUNDMAINTENANCE)
    log.delete()
    return custom_response(status_code=200, extra_info='deleted')


def get_log_details(log):
    """
    Function to check if a log exists and serialize it
    :param log: the log object
    :return response: error or the serialized log object
    """
    if not log:
        return custom_response(status_code=404, details=NOTFOUNDMAINTENANCE)
    ser_log = maintenance_schema.dump(log)
    return custom_response(status_code=200, details=ser_log, extra_info="success")


def get_multiple_log_details(logs):
    """
    Function to take a query object and serialize each log inside it.
    :param logs: the query object containing all the logs
    :return response: error the a list of serialized log objects.
    """
    if not logs:
        return custom_response(status_code=404, details=NOTFOUNDMAINTENANCE)
    jason = []
    final_res = {"maintenance_logs": jason}
    for log in logs:
        jason.append(maintenance_schema.dump(log))
    return custom_response(status_code=200, details=final_res, extra_info="success")


def update_log_details(log, req_data):
    """
    Function to update a log object by certain allowed parameters
    :param log: the log object to be updated.
    :param dict req_data: the request body data
    :return response: error or the serialized data of the updated object.
    """
    if not log:
        return custom_response(status_code=404, details=NOTFOUNDMAINTENANCE)

    # only allow updating log details
    if not ("maintenance_info" in req_data and len(req_data) == 1):
        return custom_response(status_code=403, details="You can only update the maintenance_info field")
    # Try and load log data to the schema
    try:
        data = maintenance_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    log.update(data)
    ser_log = maintenance_schema.dump(log)
    return custom_response(status_code=200, details=ser_log, extra_info="success")
