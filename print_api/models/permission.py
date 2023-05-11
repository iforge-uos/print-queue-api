from print_api.extensions import db


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
