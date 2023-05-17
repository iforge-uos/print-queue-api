from print_api.models import db


class UserRole(db.Model):
    __tablename__ = "user_roles"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")

    def __init__(self, user_id, role_id):
        self.user_id = user_id
        self.role_id = role_id

    def save(self):
        """
        Save Object Function
        """
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<UserRole {self.user_id} {self.role_id}>"
