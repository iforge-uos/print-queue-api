from functools import wraps

from flask import current_app
from flask_jwt_extended import create_refresh_token, create_access_token, jwt_required, get_jwt_identity

import print_api.common.cache as c
from print_api.common.ldap import LDAP
from print_api.common.routing import custom_response
from print_api.common.tasks import update_user_roles_in_cache
from print_api.models import User, UserRole


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


def check_user_roles(required_roles):
    """Check the user's roles against the required roles."""
    uid = get_jwt_identity()

    user = User.get_user_by_uid(uid)

    if user is None:
        return False

    cache = c.RedisCache(
        uri=current_app.config["REDIS_URI"],
        ex=current_app.config["REDIS_EXPIRY"]

    )

    if not cache.has_user_roles(user.id):
        update_user_roles_in_cache.delay(user.id)  # Trigger Celery task
        # Fetch roles from the database if not in cache
        role_mapping = UserRole.get_all_by_user(user.id)  # Assuming UserRole has this method

        role_list = []
        for rm in role_mapping:
            role_list.append(rm.role.name)
    else:
        role_list = cache.get_user_roles(user.id)

    return set(required_roles).issubset(set(role_list))


def role_required(*required_roles):
    """Wrapper function to protect an endpoint by required roles."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if not check_user_roles(required_roles):
                return custom_response(403, None, "Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
