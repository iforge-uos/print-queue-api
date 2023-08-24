from print_api.models import db, RolePermission, UserRole


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    permissions = db.relationship("RolePermission", back_populates="role")
    users = db.relationship(
        "UserRole", back_populates="role"
    )  # refers to 'role' in 'UserRole'

    def __repr__(self):
        return f"<Role {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    @staticmethod
    def add(name) -> bool:
        if Role.get(name) is not None:
            return False
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()
        return True

    @staticmethod
    def get(role_id):
        return Role.query.get(role_id)

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()

    @staticmethod
    def update(role_id, name):
        role = Role.get(role_id)
        role.name = name
        db.session.commit()

    @staticmethod
    def delete(role_id) -> bool:
        role = Role.get(role_id)
        if role is None:
            return False
        # TODO WORK OUT HOW TO DO THIS IN ONE QUERY SO IT CAN BE ROLLEDBACKED IF NOT ALLOWED TO DELETE THE ROLE
        if RolePermission.remove_all_by_role(role_id) is False:
            return False
        if UserRole.remove_all_by_role(role_id) is False:
            return False

        db.session.delete(role)
        db.session.commit()

    @staticmethod
    def get_all():
        return Role.query.all()
