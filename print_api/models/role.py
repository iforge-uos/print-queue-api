from print_api.models import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    permissions = db.relationship("RolePermission", back_populates="role")
    users = db.relationship("UserRole", back_populates="role")  # refers to 'role' in 'UserRole'

