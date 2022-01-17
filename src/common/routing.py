from flask import Response, json


def custom_response(res, status_code):
    """
    Custom Response Function to encapsulate a json response with a status code. \n
    Arguments:
        res: the response as a dictionary
        status_code: the http status code
    Returns:
        Response: the response object.
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
