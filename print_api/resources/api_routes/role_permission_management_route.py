from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from print_api.common.routing import custom_response
from print_api.models import User, Role

role_permission_api = Blueprint("role_permission", __name__)


@role_permission_api.route("/assign_role_to_user", methods=["POST"])
@jwt_required()
def assign_role_to_user():
    """
    Function to assign a role to a user
    {
    "user_id": 1,
    "role_id": 1
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    role_id = data.get("role_id")
    if user_id is None or role_id is None:
        return custom_response(400, None, "Missing user_id or role_id")

    user = User.get_user_by_id(user_id)
    if user is None:
        return custom_response(404, None, "User not found")
    role = Role.get_role_by_id(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")

    if user.has_role(role):
        return custom_response(400, None, "User already has role")
    if user.add_role(role):
        return custom_response(200, None, "Role assigned to user")
    return custom_response(500, None, "Failed to assign role to user")


@role_permission_api.route("/remove_role_from_user", methods=["POST"])
@jwt_required()
def remove_role_from_user():
    """
    Function to remove a role from a user
    {
    "user_id": 1,
    "role_id": 1
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    role_id = data.get("role_id")
    if user_id is None or role_id is None:
        return custom_response(400, None, "Missing user_id or role_id")

    user = User.get_user_by_id(user_id)
    if user is None:
        return custom_response(404, None, "User not found")
    role = Role.get_role_by_id(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")

    if not user.has_role(role):
        return custom_response(400, None, "User does not have role")
    if user.remove_role(role):
        return custom_response(200, None, "Role removed from user")
    return custom_response(500, None, "Failed to remove role from user")


@role_permission_api.route("/view_user_roles/<int:user_id>", methods=["GET"])
@jwt_required()
def view_user_roles(user_id):
    """
    Function to return a list of all serialised roles a user has
    """
    user = User.get_user_by_id(user_id)
    if user is None:
        return custom_response(404, None, "User not found")
    return custom_response(200, user.get_roles(), None)


@role_permission_api.route("/view_role_users/<int:role_id>", methods=["GET"])
@jwt_required()
def view_role_users(role_id):
    """
    Function to return a list of all users a role has as an array of IDs
    """
    role = Role.get_role_by_id(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")
    if role.users is None:
        return custom_response(200, [], None)
    return custom_response(200, [user.id for user in role.users], None)


@role_permission_api.route("/create_role", methods=["POST"])
@jwt_required()
def create_role():
    """
    Function to create a new role
    {
    "role_name": "admin"
    }
    """
    data = request.get_json()
    role_name = data.get("role_name")
    if role_name is None:
        return custom_response(400, None, "Missing role_name")

    if Role.add(role_name):
        role = Role.get_role_by_name(role_name)
        return custom_response(200, role.to_dict(), "Role created")
    return custom_response(500, None, "Failed to create role")


@role_permission_api.route("/update_role", methods=["PUT"])
@jwt_required()
def update_role():
    """ """
    pass


@role_permission_api.route("/delete_role", methods=["DELETE"])
@jwt_required()
def delete_role():
    pass


@role_permission_api.route("/view_role", methods=["GET"])
@jwt_required()
def view_role():
    pass


@role_permission_api.route("/view_all_roles", methods=["GET"])
@jwt_required()
def view_all_roles():
    pass


@role_permission_api.route("/assign_permission_to_role", methods=["POST"])
@jwt_required()
def assign_permission_to_role():
    pass


@role_permission_api.route("/create_permission", methods=["POST"])
@jwt_required()
def create_permission():
    pass


@role_permission_api.route("/update_permission", methods=["PUT"])
@jwt_required()
def update_permission():
    pass


@role_permission_api.route("/delete_permission", methods=["DELETE"])
@jwt_required()
def delete_permission():
    pass


@role_permission_api.route("/view_permission", methods=["GET"])
@jwt_required()
def view_permission():
    pass


@role_permission_api.route("/view_all_permissions", methods=["GET"])
@jwt_required()
def view_all_permissions():
    pass
