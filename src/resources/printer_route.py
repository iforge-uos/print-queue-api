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
    Function to increment a printers details by its name \n
    Arguments:
        printer_id: the integer PK of the printer record
    Returns:
        Response: error or serialized updated printer
    """
    req_data = request.get_json()
    printer = printer_model.get_printer_by_id(printer_id)
    return update_printer_details(printer, req_data)


@printer_api.route('/update/<string:printer_name>', methods=['PUT'])
def update_by_name(printer_name):
    """
    Function to update a printers details by its name \n
    Arguments:
        printer_name: the string name of the printer record
    Returns:
        Response: error or serialized updated printer
    """
    req_data = request.get_json()
    printer = printer_model.get_printer_by_name(printer_name)
    return update_printer_details(printer, req_data)


@printer_api.route('/increment/<int:printer_id>', methods=['PUT'])
def increment_by_id(printer_id):
    """
    Function to increment a printers details by its ID \n
    Arguments:
        printer_id: the integer PK of the printer record
    Returns:
        Response: error or serialized incremented printer
    """
    req_data = request.get_json()
    printer = printer_model.get_printer_by_id(printer_id)
    return increment_printer_details(printer, req_data)


@printer_api.route('/increment/<string:printer_name>', methods=['PUT'])
def increment_by_name(printer_name):
    """
    Function to increment a printers details by its name \n
    Arguments:
        printer_name: the string name of the printer record
    Returns:
        Response: error or serialized incremented printer
    """
    req_data = request.get_json()
    printer = printer_model.get_printer_by_name(printer_name)
    ser_printer = increment_printer_details(printer, req_data)
    if ser_printer is None:
        return custom_response({"error": NOTFOUNDPRINTER}, 404)
    return custom_response(ser_printer, 200)


@printer_api.route('/view/all/', methods=['GET'])
def view_all_printers():
    """
    Function to view all printer records in the database \n
    Arguments:
        none:
    Returns:
        Response: error or serialized printers
    """
    return get_multiple_printer_details(printer_model.get_all_printers())


@printer_api.route('/view/individual/<int:printer_id>', methods=['GET'])
def view_by_id(printer_id):
    """
    Function to view a printer record in the database \n
    Arguments:
        printer_id: the integer PK of the printer record
    Returns:
        Response: error or serialized printer
    """
    return get_printer_details(printer_model.get_printer_by_id(printer_id))


@printer_api.route('/view/individual/<string:printer_name>', methods=['GET'])
def view_by_name(printer_name):
    """
    Function to view a printer record in the database \n
    Arguments:
        printer_name: the string name of the printer
    Returns:
        Response: error or serialized printer
    """
    return get_printer_details(printer_model.get_printer_by_name(printer_name))


@printer_api.route('/delete/<int:printer_id>', methods=['DELETE'])
def delete_by_id(printer_id):
    """
    Function to delete a printer record in the database \n
    Arguments:
        printer_id: the integer PK of the printer record
    Returns:
        Response: error or success message
    """
    return delete_printer(printer_model.get_printer_by_id(printer_id))


@printer_api.route('/delete/<string:printer_name>', methods=['DELETE'])
def delete_by_name(printer_name):
    """
    Function to delete a printer record in the database \n
    Arguments:
        printer_name: the string name of the printer
    Returns:
        Response: error or success message
    """
    return delete_printer(printer_model.get_printer_by_name(printer_name))


@printer_api.route('/add', methods=['POST'])
def create():
    """
    Function to create a new printer record in the database \n
    Arguments:
        None:
    Returns:
        Response: error or success message
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
    """
    Function to delete a printer record from the database \n
    Arguments:
        printer: the printer object to delete
    Returns:
        Response: error or success message
    """
    if not printer:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)
    printer.delete()
    return custom_response({'message': 'deleted'}, 200)


def get_printer_details(printer):
    """
    Function to serialize a printers details \n
    Arguments:
        printer: the printer object to serialize
    Returns:
        Response: error or serialized printer
    """
    if not printer:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)
    ser_printer = printer_schema.dump(printer)
    return custom_response(ser_printer, 200)


def update_printer_details(printer, req_data):
    """
    Function to take a dictionary of values, and update the printer to match those values \n
    Arguments:
        printer: the printer object to update
        req_data: the dictionary of values used to update the printer
    Returns:
        Response: error or serialized updated printer
    """
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


def increment_printer_details(printer, req_data):
    """
    Function to take a dictionary of values, and increment the printer telemetry by those values \n
    Arguments:
        printer: the printer object to increment
        req_data: the dictionary of values used to increment the printer
    Returns:
        Response: error or serialized updated printer
    """
    allowed_keys = ("total_time_printed", "completed_prints",
                    "failed_prints", "total_filament_used", "days_on_time")
    if not printer:
        return None  # Printer not found

    # Calculating what data to fetch from printer model
    request_dict = {k: req_data[k]
                    for k in allowed_keys if k in req_data}

    # Removing non incrementable values from the printer dict using the keys
    # to be incremented from the request
    printer_data = printer.get_model_dict()
    printer_values = {k: printer_data[k]
                      for k in request_dict.keys() if k in printer_data}

    # Iterate over both dictionaries and increment the printer values by the
    # request values
    incremented_items = {}
    for (_, p_value), (i_key, i_value) in zip(
            printer_values.items(), request_dict.items()):
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
        return custom_response(err.messages, 400)
    printer.update(data)
    ser_printer = printer_schema.dump(printer)
    return ser_printer


def get_multiple_printer_details(printers):
    """
    Function to take a query object of multiple printers and serialize them \n
    Arguments:
        printers: the query object containing printers
    Returns:
        Response: error or a list of serialized printers
    """
    if not printers:
        return custom_response({'error': NOTFOUNDPRINTER}, 404)
    jason = []
    for printer in printers:
        jason.append(printer_schema.dump(printer))
    return custom_response(jason, 200)
