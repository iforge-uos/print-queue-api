from flask import current_app
from marshmallow import fields, Schema
from sqlalchemy.sql import func

from print_api.common.ldap import LDAP
from print_api.models import db, UserRole


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    uid = db.Column(db.String(10), nullable=False, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    short_name = db.Column(db.String, nullable=True)
    user_score = db.Column(db.Integer, nullable=False, default=0)
    is_rep = db.Column(db.Boolean, nullable=False, default=False)
    score_editable = db.Column(db.Boolean, nullable=False, default=True)
    date_added = db.Column(db.DateTime(timezone=True), server_default=func.now())
    completed_count = db.Column(db.Integer, nullable=False, default=0)
    failed_count = db.Column(db.Integer, nullable=False, default=0)
    rejected_count = db.Column(db.Integer, nullable=False, default=0)
    slice_completed_count = db.Column(db.Integer, nullable=False, default=0)
    slice_failed_count = db.Column(db.Integer, nullable=False, default=0)
    slice_rejected_count = db.Column(db.Integer, nullable=False, default=0)

    roles = db.relationship("UserRole", back_populates="user")

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get("name")
        self.email = data.get("email")
        self.short_name = data.get("short_name")
        self.uid = data.get("uid")

        self.user_score = data.get("user_score")
        self.is_rep = data.get("is_rep")
        self.score_editable = data.get("score_editable")
        self.completed_count = data.get("completed_count")
        self.failed_count = data.get("failed_count")
        self.rejected_count = data.get("rejected_count")
        self.slice_completed_count = data.get("slice_completed_count")
        self.slice_failed_count = data.get("slice_failed_count")
        self.slice_rejected_count = data.get("slice_rejected_count")

    def __repr__(self):
        if self.short_name is None:
            return "<User: %r>" % self.name
        else:
            return "<User: %r>" % self.short_name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "short_name": self.short_name,
            "uid": self.uid,
            "user_score": self.user_score,
            "is_rep": self.is_rep,
            "score_editable": self.score_editable,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "rejected_count": self.rejected_count,
            "slice_completed_count": self.slice_completed_count,
            "slice_failed_count": self.slice_failed_count,
            "slice_rejected_count": self.slice_rejected_count,
            "user_level": User.calculate_level_from_score(self.user_score),
        }

    @staticmethod
    def create_from_ldap(uid) -> bool:
        ldap = LDAP()
        user_info = ldap.lookup(
            f"(&(objectclass=person)(uid={uid}))",
            ["givenName", "sn", "mail"],
            True,
        )
        if user_info is None:
            return False
        user = User(
            {
                "name": str(user_info["givenName"]) + " " + str(user_info["sn"]),
                "email": str(user_info["mail"]).lower(),
                "uid": uid,
            }
        )
        user.save()
        UserRole.add(user.id, 1)
        return True

    def save(self):
        """
        Save Object Function
        """
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """
        Update attributes function
        """
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        """
        Delete Object Function
        """
        db.session.delete(self)
        db.session.commit()

    def has_role(self, role_id) -> bool:
        return UserRole.get(self.id, role_id) is not None

    def give_role(self, role_id) -> bool:
        return UserRole.add(self.id, role_id)

    def remove_role(self, role_id) -> bool:
        return UserRole.remove(self.id, role_id)

    @staticmethod
    def get_all_users():
        """
        Function to get all the users in the database
        :return query_object: a query object containing all the users
        """
        return User.query.all()

    @staticmethod
    def get_user_by_id(u_id):
        """
        Function to get a user by their ID
        :param int u_id: the PK of the user
        :return query_object: a query object containing the user
        """
        return User.query.get(u_id)

    @staticmethod
    def get_user_by_email(value):
        """
        Function to get a user by their email
        :param str value: the email of the user
        :return query_object: a query object containing the user
        """
        return User.query.filter_by(email=value).first()

    @staticmethod
    def get_user_by_uid(value):
        """
        Function to get a user by their email
        :param str value: the uid of the user
        :return query_object: a query object containing the user
        """
        return User.query.filter_by(uid=value).first()

    @staticmethod
    def calculate_level_from_score(score):
        """
        Function to calculate what level the user would be with a given score.
        :param int score: score of the user
        """

        advanced_level = current_app.config["ADVANCED_LEVEL"]
        expert_level = current_app.config["EXPERT_LEVEL"]
        insane_level = current_app.config["INSANE_LEVEL"]

        # set boundaries
        user_level_struct = {
            0: "beginner",
            advanced_level: "advanced",
            expert_level: "expert",
            insane_level: "insane",
        }

        level = ""
        for key, value in user_level_struct.items():
            if score >= key:
                level = value
        return level


class UserSchema(Schema):
    """
    User Schema
    """

    id = fields.Int(dump_only=True)
    email = fields.String(required=True)
    uid = fields.String(required=True)
    name = fields.String(required=True)
    short_name = fields.String(required=False, allow_none=True, missing="")
    user_score = fields.Int(required=False)
    is_rep = fields.Boolean(required=False)
    score_editable = fields.Boolean(required=False)
    date_added = fields.DateTime(required=False)
    completed_count = fields.Int(required=False)
    failed_count = fields.Int(required=False)
    rejected_count = fields.Int(required=False)
    slice_completed_count = fields.Int(required=False)
    slice_failed_count = fields.Int(required=False)
    slice_rejected_count = fields.Int(required=False)
