from flask import Response, json


def custom_response(res, status_code):
    """
    Custom Response Function to encapsulate a json response with a status code.
    :param dict res: response
    :param int status_code: http status code
    :return response: response object
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
