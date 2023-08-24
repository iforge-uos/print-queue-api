from print_api.models import db


class UserRole(db.Model):
    __tablename__ = "user_roles"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self):
        return f"<UserRole {self.user_id} {self.role_id}>"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "role_id": self.role_id,
        }

    @staticmethod
    def add(user_id, role_id):
        if UserRole.get(user_id, role_id) is not None:
            return False
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.session.add(user_role)
        db.session.commit()
        return True

    @staticmethod
    def get(user_id, role_id):
        return UserRole.query.get((user_id, role_id))

    @staticmethod
    def get_all_by_user(user_id):
        return UserRole.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_all_by_role(role_id):
        return UserRole.query.filter_by(role_id=role_id).all()

    @staticmethod
    def remove(user_id, role_id):
        user_role = UserRole.get(user_id, role_id)
        if user_role is None:
            return False
        db.session.delete(user_role)
        db.session.commit()
        return True

    @staticmethod
    def remove_all_by_user(user_id):
        user_roles = UserRole.get_all_by_user(user_id)
        if user_roles is None:
            return False
        for user_role in user_roles:
            db.session.delete(user_role)
        db.session.commit()
        return True

    @staticmethod
    def remove_all_by_role(role_id):
        user_roles = UserRole.get_all_by_role(role_id)
        if user_roles is None:
            return False
        # TODO WORK OUT HOW TO DO THIS IN ONE QUERY SO IT CAN BE ROLLEDBACKED IF NOT ALLOWED TO DELETE THE ROLE
        for user_role in user_roles:
            db.session.delete(user_role)
        db.session.commit()
        return True
