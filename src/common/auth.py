from dotenv import find_dotenv
from flask import current_app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# TODO
# Auth Print Q Clients
# Auth Admin Clients
# Return a token for either auth state

"""
Honestly this file is gonna be a bit of a mess.
Any ideas to make this better are appreciated
"""


def generate_client_auth_token(expiration, client_version):
    """
    Generate an authentication token for usage of basic features of the API. \n
    By default, this will expire after 24 hours
    Arguments:
        expiration: Seconds after which to expire the token.
        client_version : The version of the print Q client used for API
    Returns:
        None:
    """
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'CLIENT_VERSION': client_version})


def verify_client_auth_token(token):
    """
    Verifies the supplied authentication token. \n
    Arguments:
        token: The user's authentication token.
    Returns:
        boolean: if the token is verified or not
    """
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False  # Valid token supplied, but expired
    except BadSignature:
        return False  # Invalid token supplied
    return data['CLIENT_VERSION'] >= current_app.config['ALLOWED_APP_VERSION']


def write_version_to_dotenv(value):
    """
    Writes the new verifier to the env file so that the data persists through server reboots. \n
    Args:
        value: the new client version string in the format (YYYYMMDD)
    Returns:
        boolean: if the write was successful or not.
    """
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
