from datetime import timedelta, datetime
import os

from flask import Blueprint, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, \
    decode_token
from print_api.common.routing import custom_response
from print_api.common.auth import ldap_authenticate
from print_api.models.refresh_token import refresh_token
from print_api.models.user import user_model

auth_api = Blueprint("auth", __name__)


@auth_api.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins="*", supports_credentials=True)
def login():
    """
    API Route to LDAP authenticate with the sheffield LDAP server (mainly to be used for internal development)
    ValidateTicket should be used in production
    """
    if not request.is_json:
        return custom_response(status_code=400, data={"message": "Request must be JSON"})

    uid = request.json.get("uid", None)
    password = request.json.get("password", None)

    if not uid or not password:
        return custom_response(status_code=400, data={"message": "Must supply uid and password"})

    if ldap_authenticate(uid, password):
        gen_access_token = create_access_token(identity=uid)
        gen_refresh_token = create_refresh_token(identity=uid)

        # Extract the JTI from the refresh token and save it to the database
        decoded_refresh_token = decode_token(gen_refresh_token)
        jti = decoded_refresh_token['jti']

        # Get Expiration Time
        expires_at = datetime.utcnow() + timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
        revoked_refresh_token = gen_refresh_token(jti=jti, uid=uid, expires_at=expires_at)
        revoked_refresh_token.add()

        # Get the user object and serialise it

        return custom_response(status_code=200, data={"access_token": gen_access_token,
                                                      "refresh_token": gen_refresh_token,
                                                      "user": uid})
    else:
        return custom_response(status_code=401, data={"message": "Invalid credentials"})


@auth_api.route("/logout", methods=["DELETE"])
@jwt_required(refresh=True)
def logout():
    """
    API Route to log out a user
    """
    jti = get_jwt()['jti']
    refresh_token.revoke(jti)
    return custom_response(status_code=200, data={"message": "Successfully logged out"})


@auth_api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]
    if refresh_token.is_revoked(jti):
        return custom_response(status_code=401, data={"message": "Token has been revoked"})

    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return custom_response(status_code=200, data={"access_token": access_token})
