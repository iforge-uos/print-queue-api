from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow.exceptions import ValidationError
from print_api.models import Permission, Role, RolePermission, User, UserRole, user_schema
from print_api.common.routing import custom_response

role_permission_api = Blueprint("role_permission", __name__)
user_schema = user_schema()


@role_permission_api.route("/assign_role_to_user", methods=["POST"])
@jwt_required()
def assign_role_to_user():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        role_id = data.get("role_id")

        user = User.query.get(user_id)
        role = Role.query.get(role_id)

        if not user or not role:
            return custom_response(404, "User or role not found")

        user_role = UserRole(user_id=user_id, role_id=role_id)
        user_role.save()

        return custom_response(200, "Role assigned to user successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/remove_role_from_user", methods=["POST"])
@jwt_required()
def remove_role_from_user():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        role_id = data.get("role_id")

        user_role = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()

        if not user_role:
            return custom_response(404, "User role not found")

        user_role.delete()

        return custom_response(200, "Role removed from user successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_user_roles", methods=["GET"])
@jwt_required()
def view_user_roles():
    try:
        user_id = request.args.get("user_id")

        user = User.query.get(user_id)

        if not user:
            return custom_response(404, "User not found")

        roles = [role_permission.role.to_dict() for role_permission in user.roles]

        return custom_response(200, roles)
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_role_users", methods=["GET"])
@jwt_required()
def view_role_users():
    try:
        role_id = request.args.get("role_id")

        role = Role.query.get(role_id)

        if not role:
            return custom_response(404, "Role not found")

        users = [user_role.user.to_dict() for user_role in role.users]

        return custom_response(200, users)
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/create_role", methods=["POST"])
@jwt_required()
def create_role():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        role = Role(name=name, description=description)
        role.save()

        return custom_response(200, "Role created successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/update_role", methods=["PUT"])
@jwt_required()
def update_role():
    try:
        data = request.get_json()
        role_id = data.get("role_id")
        name = data.get("name")
        description = data.get("description")

        role = Role.query.get(role_id)

        if not role:
            return custom_response(404, "Role not found")

        role.name = name
        role.description = description
        role.save()

        return custom_response(200, "Role updated successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/delete_role", methods=["DELETE"])
@jwt_required()
def delete_role():
    try:
        role_id = request.args.get("role_id")

        role = Role.query.get(role_id)

        if not role:
            return custom_response(404, "Role not found")

        role.delete()

        return custom_response(200, "Role deleted successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_role", methods=["GET"])
@jwt_required()
def view_role():
    try:
        role_id = request.args.get("role_id")

        role = Role.query.get(role_id)

        if not role:
            return custom_response(404, "Role not found")

        return custom_response(200, role.to_dict())
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_all_roles", methods=["GET"])
@jwt_required()
def view_all_roles():
    try:
        roles = [role.to_dict() for role in Role.query.all()]

        return custom_response(200, roles)
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/assign_permission_to_role", methods=["POST"])
@jwt_required()
def assign_permission_to_role():
    try:
        data = request.get_json()
        role_id = data.get("role_id")
        permission_id = data.get("permission_id")

        role = Role.query.get(role_id)
        permission = Permission.query.get(permission_id)

        if not role or not permission:
            return custom_response(404, "Role or permission not found")

        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        role_permission.save()

        return custom_response(200, "Permission assigned to role successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/create_permission", methods=["POST"])
@jwt_required()
def create_permission():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        permission = Permission(name=name, description=description)
        permission.save()

        return custom_response(200, "Permission created successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/update_permission", methods=["PUT"])
@jwt_required()
def update_permission():
    try:
        data = request.get_json()
        permission_id = data.get("permission_id")
        name = data.get("name")
        description = data.get("description")

        permission = Permission.query.get(permission_id)

        if not permission:
            return custom_response(404, "Permission not found")

        permission.name = name
        permission.description = description
        permission.save()

        return custom_response(200, "Permission updated successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/delete_permission", methods=["DELETE"])
@jwt_required()
def delete_permission():
    try:
        permission_id = request.args.get("permission_id")

        permission = Permission.query.get(permission_id)

        if not permission:
            return custom_response(404, "Permission not found")

        permission.delete()

        return custom_response(200, "Permission deleted successfully")
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_permission", methods=["GET"])
@jwt_required()
def view_permission():
    try:
        permission_id = request.args.get("permission_id")

        permission = Permission.query.get(permission_id)

        if not permission:
            return custom_response(404, "Permission not found")

        return custom_response(200, permission.to_dict())
    except Exception as e:
        return custom_response(500, str(e))


@role_permission_api.route("/view_all_permissions", methods=["GET"])
@jwt_required()
def view_all_permissions():
    try:
        permissions = [permission.to_dict() for permission in Permission.query.all()]

        return custom_response(200, permissions)
    except Exception as e:
        return custom_response(500, str(e))
