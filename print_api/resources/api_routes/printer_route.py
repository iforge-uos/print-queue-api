from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError

from print_api.common.routing import custom_response
from print_api.models import Printer, PrinterSchema

printer_api = Blueprint("printers", __name__)
printer_schema = PrinterSchema()

NOTFOUNDPRINTER = "printer(s) not found"


@printer_api.route("/printer/<int:printer_id>", methods=["PUT"])
@jwt_required()
def update_by_id(printer_id):
    """
    Function to increment a printers details by its name \n
    :param int printer_id: PK of the printer record
    :return response: error or serialized updated printer
    """
    req_data = request.get_json()
    printer = Printer.get_printer_by_id(printer_id)
    return update_printer_details(printer, req_data)


@printer_api.route("/printer/<string:printer_name>", methods=["PUT"])
@jwt_required()
def update_by_name(printer_name):
    """
    Function to update a printers details by its name
    :param str printer_name: name of the printer
    :return response: error or serialized updated printer
    """
    req_data = request.get_json()
    printer = Printer.get_printer_by_name(printer_name)
    return update_printer_details(printer, req_data)


@printer_api.route("/printer/<int:printer_id>/increment", methods=["PUT"])
@jwt_required()
def increment_by_id(printer_id):
    """
    Function to increment a printers details by its ID \n
    Arguments:
        printer_id: PK of the printer record
    Returns:
        Response: error or serialized incremented printer
    """
    req_data = request.get_json()
    printer = Printer.get_printer_by_id(printer_id)
    return increment_printer_details(printer, req_data)


@printer_api.route("/printer/<string:printer_name>/increment", methods=["PUT"])
@jwt_required()
def increment_by_name(printer_name):
    """
    Function to increment a printers details by its name
    :param str printer_name: name of the printer
    :return response: error or serialized incremented printer
    """
    req_data = request.get_json()
    printer = Printer.get_printer_by_name(printer_name)
    ser_printer = increment_printer_details(printer, req_data)
    if ser_printer is None:
        return custom_response(status_code=404, details=NOTFOUNDPRINTER)
    return custom_response(status_code=200, details=ser_printer)


@printer_api.route("/printer", methods=["GET"])
@jwt_required()
def view_all_printers():
    """
    Function to view all printer records in the database
    :return response: error or serialized printers
    """
    return get_multiple_printer_details(Printer.get_all_printers())


@printer_api.route("/printer/<int:printer_id>", methods=["GET"])
@jwt_required()
def view_by_id(printer_id):
    """
    Function to view a printer record in the database
    :param int printer_id: PK of the printer record
    :return response: error or serialized printer
    """
    return get_printer_details(Printer.get_printer_by_id(printer_id))


@printer_api.route("/printer/<string:printer_name>", methods=["GET"])
@jwt_required()
def view_by_name(printer_name):
    """
    Function to view a printer record in the database
    :param str printer_name: name of the printer
    :return response: error or serialized printer
    """
    return get_printer_details(Printer.get_printer_by_name(printer_name))


@printer_api.route("/printer/<int:printer_id>", methods=["DELETE"])
@jwt_required()
def delete_by_id(printer_id):
    """
    Function to delete a printer record in the database
    :param int printer_id: PK of the printer record
    :return response: error or success message
    """
    return delete_printer(Printer.get_printer_by_id(printer_id))


@printer_api.route("/printer/<string:printer_name>", methods=["DELETE"])
@jwt_required()
def delete_by_name(printer_name):
    """
    Function to delete a printer record in the database
    :param str printer_name: name of the printer
    :return response: error or success message
    """
    return delete_printer(Printer.get_printer_by_name(printer_name))


@printer_api.route("/printer", methods=["POST"])
@jwt_required()
def create():
    """
    Function to create a new printer record in the database
    :return response: error or success message
    """
    req_data = request.get_json()

    try:
        data = printer_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)

    # check if printer already exists in the db
    printer_in_db = Printer.get_printer_by_name(data.get("printer_name"))
    if printer_in_db:
        message = {
            "error": "Printer already exists, please supply another printer name"
        }
        return custom_response(status_code=400, details=message)

    printer = Printer(data)
    printer.save()
    return custom_response(
        status_code=200, extra_info="success", details=printer_schema.dump(printer)
    )


def delete_printer(printer):
    """
    Function to delete a printer record from the database
    :param printer: the printer object to delete
    :return response: error or success message
    """
    if not printer:
        return custom_response(status_code=404, details=NOTFOUNDPRINTER)
    printer.delete()
    return custom_response(status_code=200, extra_info="deleted")


def get_printer_details(printer):
    """
    Function to serialize a printers details
    :param printer: the printer object to serialize
    :return response: error or serialized printer
    """
    if not printer:
        return custom_response(status_code=404, details=NOTFOUNDPRINTER)
    ser_printer = printer_schema.dump(printer)
    return custom_response(status_code=200, details=ser_printer, extra_info="success")


def update_printer_details(printer, req_data):
    """
    Function to take a dictionary of values, and update the printer to match those values
    :param printer: the printer object to update
    :param dict req_data: the dictionary of values used to update the printer
    :return response: error or serialized updated printer
    """
    if not printer:
        return custom_response(status_code=404, details=NOTFOUNDPRINTER)
    # Try and load printer data to the schema
    try:
        data = printer_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    printer.update(data)
    ser_printer = printer_schema.dump(printer)
    return custom_response(status_code=200, details=ser_printer, extra_info="success")


def increment_printer_details(printer, req_data):
    """
    Function to take a dictionary of values, and increment the printer telemetry by those values
    :param printer: the printer object to increment
    :param dict req_data: the dictionary of values used to increment the printer
    :return response: error or serialized updated printer
    """
    allowed_keys = (
        "total_time_printed",
        "completed_prints",
        "failed_prints",
        "total_filament_used",
        "days_on_time",
    )
    if not printer:
        return None  # Printer not found

    # Calculating what data to fetch from printer model
    request_dict = {k: req_data[k] for k in allowed_keys if k in req_data}

    # Removing non incrementable values from the printer dict using the keys
    # to be incremented from the request
    printer_data = printer.get_model_dict()
    printer_values = {
        k: printer_data[k] for k in request_dict.keys() if k in printer_data
    }

    # Iterate over both dictionaries and increment the printer values by the
    # request values
    incremented_items = {}
    for (_, p_value), (i_key, i_value) in zip(
        printer_values.items(), request_dict.items()
    ):
        if p_value is None:
            p_value = i_value
        else:
            p_value += i_value
        incremented_items[i_key] = p_value
    # Try and load printer data to the schema
    try:
        data = printer_schema.load(incremented_items, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(status_code=400, details=err.messages)
    printer.update(data)
    ser_printer = printer_schema.dump(printer)
    return ser_printer


def get_multiple_printer_details(printers):
    """
    Function to take a query object of multiple printers and serialize them
    :param printers: the query object containing printers
    :return response: error or a list of serialized printers
    """
    jason = []
    for printer in printers:
        jason.append(printer_schema.dump(printer))
    final_res = {"printers": jason}
    return custom_response(status_code=200, details=final_res, extra_info="success")
