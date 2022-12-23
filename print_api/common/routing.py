from flask import Response, json


def custom_response(status_code, details=None, extra_info=None):
    """
    Custom Response Function to encapsulate a json response with a status code.
    :param dict data: response
    :param int status_code: http status code
    :return response: response object

    iForge standards:
    {
      "status": "success"/"error",
      "data": { Success-specific data (eg application) / None or optional error payload },
      "message": { None or optional success message / Error-specific data (eg debug) }
    }
    """

    res = {
        "status": None,
        "data": None,
        "message": None
    }

    if 200 <= status_code < 300:
        res["status"] = "success"
    elif 300 <= status_code < 400:
        res["status"] = "redirect"
    elif 400 <= status_code < 500:
        res["status"] = "error"
    elif 500 <= status_code < 600:
        res["status"] = "server_error"
    else:
        res["status"] = "unknown"

    if res["status"] is "success":
        res["data"] = details
        res["message"] = extra_info
    else:
        res["data"] = extra_info
        res["message"] = details

    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
