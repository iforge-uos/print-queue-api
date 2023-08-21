from print_api.models import db, RolePermission


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    roles = db.relationship("RolePermission", back_populates="permission")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Permission {self.name}>"

    @staticmethod
    def add(name, description) -> bool:
        if Permission.get(name) is not None:
            return False
        permission = Permission(name=name, description=description)
        db.session.add(permission)
        db.session.commit()
        return True

    @staticmethod
    def get(permission_id):
        return Permission.query.get(permission_id)

    @staticmethod
    def update(permission_id, name, description):
        permission = Permission.get(permission_id)
        permission.name = name
        permission.description = description
        db.session.commit()

    @staticmethod
    def delete(permission_id) -> bool:
        permission = Permission.get(permission_id)
        if permission is None:
            return False
        if RolePermission.remove_all_by_permission(permission_id) is False:
            return False
        db.session.delete(permission)
        db.session.commit()
        return True
