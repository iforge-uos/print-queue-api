from print_api.models import db


class RolePermission(db.Model):
    __tablename__ = "role_permissions"
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
    permission_id = db.Column(
        db.Integer, db.ForeignKey("permissions.id"), primary_key=True
    )

    role = db.relationship("Role", back_populates="permissions")
    permission = db.relationship("Permission", back_populates="roles")

    def __repr__(self):
        return f"<RolePermission {self.role_id} {self.permission_id}>"

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "permission_id": self.permission_id,
        }

    @staticmethod
    def add(role_id, permission_id) -> bool:
        if RolePermission.get(role_id, permission_id) is not None:
            return False
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        db.session.add(role_permission)
        db.session.commit()
        return True

    @staticmethod
    def get(role_id, permission_id):
        return RolePermission.query.get((role_id, permission_id))

    @staticmethod
    def get_all_by_role(role_id):
        return RolePermission.query.filter_by(role_id=role_id).all()

    @staticmethod
    def get_all_by_permission(permission_id):
        return RolePermission.query.filter_by(permission_id=permission_id).all()

    @staticmethod
    def remove(role_id, permission_id) -> bool:
        role_perm = RolePermission.get(role_id, permission_id)
        if role_perm is None:
            return False
        db.session.delete(role_perm)
        db.session.commit()
        return True

    @staticmethod
    def remove_all_by_permission(permission_id) -> bool:
        role_perms = RolePermission.get_all_by_permission(permission_id)
        if role_perms is None:
            return False
        for role_perm in role_perms:
            db.session.delete(role_perm)
        db.session.commit()
        return True

    @staticmethod
    def remove_all_by_role(role_id) -> bool:
        role_perms = RolePermission.get_all_by_role(role_id)
        if role_perms is None:
            return False
        for role_perm in role_perms:
            db.session.delete(role_perm)
        db.session.commit()
        return True
