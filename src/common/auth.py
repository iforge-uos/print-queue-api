from dotenv import find_dotenv
from flask import current_app


def write_version_to_dotenv(value):
    dotenv = find_dotenv()
    try:
        with open(dotenv, "r") as f:
            data = f.readlines()
        data[-1] = f"ALLOWED_APP_VERSION={value}"
        with open(dotenv, "w") as f:
            f.writelines(data)
    except IOError:
        return False
    current_app.config['ALLOWED_APP_VERSION'] = str(value)
    return True

def get_allowed_app_version():
    return current_app.config['ALLOWED_APP_VERSION']