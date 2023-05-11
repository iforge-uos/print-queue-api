from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError
from print_api.common.routing import custom_response
from print_api.models import Permission, Role, RolePermission, User, UserRole, user_schema

role_permission_api = Blueprint("role_permission", __name__)


def assign_role_to_user():
    # Assign role to user
    pass


def remove_role_from_user():
    # Remove role from user
    pass


def view_user_roles():
    # Get all roles for user
    pass


def view_role_users():
    # Get all users with role
    pass


def create_role():
    # Create role
    pass


def update_role():
    # Update role
    pass


def delete_role():
    # Delete role
    pass


def view_role():
    # Get role
    pass


def view_all_roles():
    # Get all roles
    pass


def assign_permission_to_role():
    pass


def create_permission():
    pass


def update_permission():
    pass


def delete_permission():
    pass


def view_permission():
    pass


def view_all_permissions():
    pass
