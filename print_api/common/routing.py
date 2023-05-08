from typing import Any, Dict, Optional
from flask import Response, json


def custom_response(status_code: int, details: Optional[Any] = None, extra_info: Optional[Any] = None) -> Response:
    """
    Custom Response Function to encapsulate a json response with a status code.
    :param int status_code: http status code
    :param details: Success-specific data or Error-specific message
    :param extra_info: None or optional success message or Error-specific data
    :return response: response object

    iForge Standard Response Format:
    {
      "status": "success" / "error",
      "payload": {
        "data": { Success-specific data },
        "error": {
          "code": { Error-specific code },
          "message": { Error-specific message }
        }
      },
      "meta": {
        "message": { Optional success message }
      }
    }
    """

    res: Dict[str, Any] = {
        "status": None,
        "payload": {
            "data": None,
            "error": None
        },
        "meta": {
            "message": None
        }
    }

    if 200 <= status_code < 300:
        res["status"] = "success"
        res["payload"]["data"] = details
        res["meta"]["message"] = extra_info
    else:
        res["status"] = "error"
        res["payload"]["data"] = None
        res["payload"]["error"] = {
            "code": status_code,
            "message": details
        }
        res["meta"]["message"] = extra_info

    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
