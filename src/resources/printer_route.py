from flask import request, Blueprint
from marshmallow.exceptions import ValidationError
from models.printers import printer_model, printer_schema
from common.routing import custom_response

printer_api = Blueprint('printers', __name__)
printer_schema = printer_schema()

NOTFOUNDPRINTER = "printer not found"


@printer_api.route('/update/<int:printer_id>', methods=['PUT'])
def update_by_id(printer_id):
    """
    Updates a single printer by its ID
    """
    req_data = request.get_json()
    printer = printer_model.get_printer_by_id(printer_id)
    return update_printer_details(printer, req_data)


@printer_api.route('/view/<int:printer_id>', methods=['GET'])
def view_by_id(printer_id):
    """
    Get a single printer by its ID
    """
    return get_printer_details(printer_model.get_printer_by_id(printer_id))


@printer_api.route('/delete/<int:printer_id>', methods=['DELETE'])
def delete_by_id(printer_id):
    """
    Delete a single printer by its ID
    """
    return delete_printer(printer_model.get_printer_by_id(printer_id))


@printer_api.route('/add', methods=['POST'])
def create():
    """
    Create Printer Function
    """
    req_data = request.get_json()

    try:
        data = printer_schema.load(req_data)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)

    # check if printer already exists in the db
    printer_in_db = printer_model.get_printer_by_name(data.get('printer_name'))
    if printer_in_db:
        message = {
            'error': 'Printer already exists, please supply another printer name'}
        return custom_response(message, 400)

    printer = printer_model(data)
    printer.save()
    return custom_response({"message": "success"}, 200)


def delete_printer(printer):
    if not printer:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)
    printer.delete()
    return custom_response({'message': 'deleted'}, 200)


def get_printer_details(printer):
    if not printer:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)
    ser_printer = printer_schema.dump(printer)
    return custom_response(ser_printer, 200)


def update_printer_details(printer, req_data):
    if not printer:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)

    # Try and load printer data to the schema
    try:
        data = printer_schema.load(req_data, partial=True)
    except ValidationError as err:
        # => {"email": ['"foo" is not a valid email address.']}
        print(err.messages)
        print(err.valid_data)  # => {"name": "John"}
        return custom_response(err.messages, 400)
    printer.update(data)
    ser_printer = printer_schema.dump(printer)
    return custom_response(ser_printer, 200)