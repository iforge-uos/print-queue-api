from sqlalchemy.sql import func
from marshmallow import fields, Schema
from print_api.extensions import db


class user_model(db.Model):
    """
    User Model
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
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

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get("name")
        self.email = data.get("email")
        self.short_name = data.get("short_name")

        self.user_score = data.get("user_score")
        self.is_rep = data.get("is_rep")
        self.score_editable = data.get("score_editable")


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

    @staticmethod
    def get_all_users():
        """
        Function to get all the users in the database
        :return query_object: a query object containing all the users
        """
        return user_model.query.all()

    @staticmethod
    def get_user_by_id(id):
        """
        Function to get a user by their ID
        :param int id: the PK of the user
        :return query_object: a query object containing the user
        """
        return user_model.query.get(id)

    @staticmethod
    def get_user_by_email(value):
        """
        Function to get a user by their email
        :param str value: the email of the user
        :return query_object: a query object containing the user
        """
        return user_model.query.filter_by(email=value).first()

    def __repr__(self):
        if self.short_name is None:
            return "<User: %r>" % self.name
        else:
            return "<User: %r>" % self.short_name


class user_schema(Schema):
    """
    User Schema
    """

    id = fields.Int(dump_only=True)
    email = fields.String(required=True)
    name = fields.String(required=True)
    short_name = fields.String(required=False)
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
