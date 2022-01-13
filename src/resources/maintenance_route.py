from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from models.maintenance_logs import maintenance_model, maintenance_schema
from models.printers import printer_model
from common.routing import custom_response

maintenance_api = Blueprint('maintenance logs', __name__)
maintenance_schema = maintenance_schema()

NOTFOUNDMAINTENANCE = "maintenance route not found"


@maintenance_api.route('/update/<int:log_id>', methods=['PUT'])
def update_by_id(log_id):
    """
    Updates a single log via its ID
    """
    req_data = request.get_json()
    log = maintenance_model.get_maintenance_log_by_id(log_id)
    return update_log_details(log, req_data)


@maintenance_api.route('/view/single/<int:log_id>', methods=['GET'])
def view_single_by_id(log_id):
    """
    Get a single log via its ID
    """
    return get_log_details(maintenance_model.get_maintenance_log_by_id(log_id))


@maintenance_api.route('/view/all/<string:printer_name>', methods=['GET'])
def view_all_by_printer_name(printer_name):
    """
    Get a single log via its linked printers name
    """
    # First check if the printer_name is valid
    printer = printer_model.get_printer_by_name(printer_name)
    if (printer is None):
        return custom_response({"error": "Printer not found"}, 404)

    # Then return the jason payload of any logs for that printer
    return get_multiple_log_details(
        maintenance_model.get_maintenance_logs_by_printer_id(printer.id))


@maintenance_api.route('/view/all/<int:printer_id>', methods=['GET'])
def view_all_by_printer_id(printer_id):
    """
    Get all logs via their linked printer_id
    """
    return get_multiple_log_details(
        maintenance_model.get_maintenance_logs_by_printer_id(printer_id))


@maintenance_api.route('/delete/<int:log_id>', methods=['DELETE'])
def delete_by_id(log_id):
    """
    Delete a single log via its ID
    """
    return delete_log(maintenance_model.get_maintenance_log_by_id(log_id))


@maintenance_api.route('/add', methods=['POST'])
def create():
    """
    Create Log Function
    """
    req_data = request.get_json()

    # Check if printer_id exists
    printer_id = req_data['printer_id']
    if (printer_model.get_printer_by_id(printer_id) is None):
        return custom_response({"error": "Printer is not found"}, 404)

    # Try and load the data into the model
    try:
        data = maintenance_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)

    log = maintenance_model(data)
    log.save()
    return custom_response({"message": "success"}, 200)


def delete_log(log):
    if not log:
        return custom_response({'error': NOTFOUNDMAINTENANCE}, 404)
    log.delete()
    return custom_response({'message': 'deleted'}, 200)


def get_log_details(log):
    if not log:
        return custom_response({'error': NOTFOUNDMAINTENANCE}, 404)
    ser_log = maintenance_schema.dump(log)
    return custom_response(ser_log, 200)


def get_multiple_log_details(logs):
    if not logs:
        return custom_response({'error': NOTFOUNDMAINTENANCE}, 404)
    # This is jank af but it works and I can't think of a better way to do
    # this lol
    jason = []
    for log in logs:
        jason.append(maintenance_schema.dump(log))
    return custom_response(jason, 200)


def update_log_details(log, req_data):
    if not log:
        return custom_response({'error': NOTFOUNDMAINTENANCE}, 404)

    # only allow updating log details
    if not ("maintenance_info" in req_data and len(req_data) == 1):
        return custom_response({'error': "not allowed"}, 403)
    # Try and load log data to the schema
    try:
        data = maintenance_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    log.update(data)
    ser_log = maintenance_schema.dump(log)
    return custom_response(ser_log, 200)
