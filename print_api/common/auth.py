from flask_jwt_extended import create_refresh_token, create_access_token
from print_api.common.ldap import LDAP
from print_api.models import User


def ldap_authenticate(uid: str, password: str) -> bool:
    """
    Function to authenticate with the sheffield LDAP server
    :param uid: the user's username
    :param password: the user's password
    :return bool success: True if authenticated, False otherwise
    """
    ldap = LDAP()
    return ldap.authenticate(uid, password)


def generate_tokens(uid: str) -> (str, str):
    user = User.query.filter_by(uid=uid).first()
    permissions = set()
    for user_role in user.roles:
        for role_permission in user_role.role.permissions:
            permissions.add(role_permission.permission.name)
    gen_access_token = create_access_token(identity=uid)
    gen_refresh_token = create_refresh_token(identity=uid)
    return gen_access_token, gen_refresh_token
