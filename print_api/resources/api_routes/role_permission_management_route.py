from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from print_api.common.routing import custom_response
from print_api.models import User, Role, Permission, RolePermission

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
    role = Role.get(role_id)
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
    user = User.get(user_id)
    if user is None:
        return custom_response(404, None, "User not found")
    return custom_response(200, user.get_roles(), None)


@role_permission_api.route("/view_role_users/<int:role_id>", methods=["GET"])
@jwt_required()
def view_role_users(role_id):
    """
    Function to return a list of all users a role has as an array of IDs
    """
    role = Role.get(role_id)
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
        role = Role.get_by_name(role_name)
        return custom_response(200, role.to_dict(), "Role created")
    return custom_response(500, None, "Failed to create role")


@role_permission_api.route("/update_role/<int:role_id>", methods=["PUT"])
@jwt_required()
def update_role(role_id):
    data = request.get_json()
    role_name = data.get("role_name")

    if role_id is None or role_name is None:
        return custom_response(400, None, "Missing role_id or role_name")

    role = Role.get(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")
    if role.name == role_name:
        return custom_response(400, None, "Role name cannot be the same")
    if role.update(role_name):
        return custom_response(200, role.to_dict(), "Role updated")
    return custom_response(500, None, "Failed to update role")


@role_permission_api.route("/delete_role/<int:role_id>", methods=["DELETE"])
@jwt_required()
def delete_role(role_id):
    if role_id is None:
        return custom_response(400, None, "Missing role_id")

    role_id = int(role_id)

    role = Role.get(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")
    if role.delete():
        return custom_response(200, None, "Role deleted")
    return custom_response(500, None, "Failed to delete role")


@role_permission_api.route("/view_role/<int:role_id>", methods=["GET"])
@jwt_required()
def view_role(role_id):
    """ """
    role = Role.get(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")
    return custom_response(200, role.to_dict(), None)


@role_permission_api.route("/view_all_roles", methods=["GET"])
@jwt_required()
def view_all_roles():
    """ """
    roles = Role.get_all()
    if roles is None:
        return custom_response(404, None, "No roles found")
    return custom_response(200, [role.to_dict() for role in roles], None)


@role_permission_api.route("/assign_permission_to_role", methods=["POST"])
@jwt_required()
def assign_permission_to_role():
    """
    Function to assign a permission to a role
    {
    "role_id": 1,
    "permission_id": 1
    }
    """

    data = request.get_json()
    role_id = data.get("role_id")
    permission_id = data.get("permission_id")

    if role_id is None or permission_id is None:
        return custom_response(400, None, "Missing role_id or permission_id")

    role = Role.get(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")
    permission = Permission.get_permission_by_id(permission_id)
    if permission is None:
        return custom_response(404, None, "Permission not found")

    if role.has_permission(permission):
        return custom_response(400, None, "Role already has permission")
    if role.add_permission(permission):
        return custom_response(200, None, "Permission assigned to role")
    return custom_response(500, None, "Failed to assign permission to role")


@role_permission_api.route("/create_permission", methods=["POST"])
@jwt_required()
def create_permission():
    """
    Function to create a new permission
    {
    "permission_name": "create_user"
    }
    """
    data = request.get_json()
    permission_name = data.get("permission_name")
    permission_description = data.get("permission_description")
    if permission_name is None:
        return custom_response(400, None, "Missing permission_name")

    if Permission.add(permission_name, permission_description):
        permission = Permission.get_permission_by_name(permission_name)
        return custom_response(200, permission.to_dict(), "Permission created")
    return custom_response(500, None, "Failed to create permission")
    pass


@role_permission_api.route("/update_permission/<int:permission_id>", methods=["PUT"])
@jwt_required()
def update_permission(permission_id):
    data = request.get_json()
    permission_name = data.get("permission_name")
    permission_description = data.get("permission_description")

    if permission_id is None:
        return custom_response(400, None, "Missing permission_id")

    permission = Permission.get(permission_id)
    if permission is None:
        return custom_response(404, None, "Permission not found")
    if permission.name == permission_name:
        return custom_response(400, None, "Permission name cannot be the same")
    if permission.update(permission_name, permission_description):
        return custom_response(200, permission.to_dict(), "Permission updated")
    return custom_response(500, None, "Failed to update permission")


@role_permission_api.route("/delete_permission/<int:permission_id>", methods=["DELETE"])
@jwt_required()
def delete_permission(permission_id):
    if permission_id is None:
        return custom_response(400, None, "Missing permission_id")

    permission = Permission.get(permission_id)
    if permission is None:
        return custom_response(404, None, "Permission not found")
    if permission.delete():
        return custom_response(200, None, "Permission deleted")
    return custom_response(500, None, "Failed to delete permission")


@role_permission_api.route("/view_permission/<int:permission_id>", methods=["GET"])
@jwt_required()
def view_permission(permission_id):
    if permission_id is None:
        return custom_response(400, None, "Missing permission_id")

    permission = Permission.get(permission_id)
    if permission is None:
        return custom_response(404, None, "Permission not found")
    return custom_response(200, permission.to_dict(), None)


@role_permission_api.route("/view_all_permissions", methods=["GET"])
@jwt_required()
def view_all_permissions():
    permissions = Permission.get_all_permissions()
    if permissions is None:
        return custom_response(404, None, "No permissions found")
    return custom_response(
        200, [permission.to_dict() for permission in permissions], None
    )


@role_permission_api.route("/view_role_permissions/<int:role_id>", methods=["GET"])
@jwt_required()
def view_role_permissions(role_id):
    """
    Function to return a list of all permissions a role has as an array of IDs
    """
    role = Role.query.get(role_id)
    if role is None:
        return custom_response(404, None, "Role not found")

    # Get the permissions through the role_permissions association
    permissions = [
        Permission.get(rp.permission_id).to_dict() for rp in role.permissions
    ]

    if not permissions:
        return custom_response(200, [], None)

    return custom_response(200, permissions, None)


@role_permission_api.route(
    "/view_permission_roles/<int:permission_id>", methods=["GET"]
)
@jwt_required()
def view_permission_roles(permission_id):
    """
    Function to return a list of all roles a permission has as an array of IDs
    """
    permission = Permission.query.get(permission_id)
    if permission is None:
        return custom_response(404, None, "Permission not found")

    # Get the roles through the role_permissions association
    roles = [Role.get(rp.role_id).to_dict() for rp in permission.roles]

    if not roles:
        return custom_response(200, [], None)

    return custom_response(200, roles, None)


@role_permission_api.route("/remove_permission_from_role", methods=["POST"])
@jwt_required()
def remove_permission_from_role():
    """
    Function to remove a permission from a role
    {
    "role_id": 1,
    "permission_id": 1
    }
    """

    data = request.get_json()
    role_id = data.get("role_id")
    permission_id = data.get("permission_id")

    if role_id is None or permission_id is None:
        return custom_response(400, None, "Missing role_id or permission_id")

    rp = RolePermission.get(role_id, permission_id)
    if rp is None:
        return custom_response(404, None, "RolePermission not found")
    if rp.delete():
        return custom_response(200, None, "RolePermission deleted")
    return custom_response(500, None, "Failed to delete RolePermission")


@role_permission_api.route("/get_permissions_for_user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_permissions_for_user(user_id):
    """
    Function to return a list of all permissions a user has as an array of IDs
    """
    user = User.get_user_by_id(user_id)
    if user is None:
        return custom_response(404, None, "User not found")

    # Get the permissions through the UserRole and RolePermission associations
    permissions = [rp.permission.to_dict() for ur in user.roles for rp in ur.role.permissions]

    if not permissions:
        return custom_response(200, [], None)

    return custom_response(200, permissions, None)
