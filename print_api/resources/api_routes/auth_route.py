from datetime import timedelta, datetime
import os

from flask import Blueprint, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, \
    decode_token
from print_api.common.routing import custom_response
from print_api.common.auth import ldap_authenticate, generate_tokens
from print_api.models import BlacklistedToken, User, user_schema

auth_api = Blueprint("auth", __name__)
user_schema = user_schema()


@auth_api.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins="*", supports_credentials=True)
def login():
    """
    API Route to LDAP authenticate with the sheffield LDAP server (mainly to be used for internal development)
    ValidateTicket should be used in production
    """
    if not request.is_json:
        return custom_response(status_code=400, details="Request must be JSON")

    uid = request.json.get("uid", None)
    password = request.json.get("password", None)

    if not uid or not password:
        return custom_response(status_code=400, details="Must supply uid and password")

    if ldap_authenticate(uid, password):

        # Create tokens
        gen_access_token, gen_refresh_token = generate_tokens(uid)

        # Check if user exists in database and if not populate via LDAP
        user = return_or_create_user(uid)
        user_details = get_main_user_details(user)
        if user is None:
            return custom_response(status_code=409, details="User does not exist. Please contact an admin")

        return custom_response(status_code=200, details={"access_token": gen_access_token,
                                                         "refresh_token": gen_refresh_token,
                                                         "user": user_details},
                               extra_info="Successfully logged in")
    else:
        return custom_response(status_code=401, details="Invalid credentials")


@auth_api.route("/logout", methods=["DELETE"])
@jwt_required(refresh=True)
def logout():
    """
    API Route to log out a user
    """
    jti = get_jwt()['jti']
    BlacklistedToken(jti).add()
    return custom_response(status_code=200, extra_info="Successfully logged out")


@auth_api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]
    if BlacklistedToken.is_blacklisted(jti):
        return custom_response(status_code=401, details="Token has been revoked", extra_info="Reauthentication required")

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return custom_response(status_code=200, details={"access_token": access_token}, extra_info="Successfully refreshed")




def return_or_create_user(uid):
    user = User.query.filter_by(uid=uid).first()
    if not user:
        if User.create_from_ldap(uid):
            user = User.query.filter_by(uid=uid).first()
            return user
        else:
            return None
    else:
        return user


def get_main_user_details(user):
    ser_user = user_schema.dump(user)
    # Only return name, email, uid and user_level
    ser_user = {key: ser_user[key] for key in ser_user.keys() & {"name", "email", "uid", "user_level"}}
    return ser_user
