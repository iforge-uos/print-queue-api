from flask import Flask
from marshmallow import fields, Schema
from marshmallow.schema import SchemaOpts
from . import db


class user(db.Model):
    """
    User Model
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    social_credit_score = db.Column(db.Integer, nullable=False)
    user_level = db.Column(db.String, nullable=False)
    is_rep = db.Column(db.Boolean, nullable=False)
    score_editable = db.Column(db.Boolean, default=True)
    short_name = db.Column(db.String, nullable=True)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.name = data.get('name')
        self.email = data.get('email')
        self.social_credit_score = data.get('social_credit_score') or 0
        self.user_level = data.get('user_level') or "Beginner"
        self.is_rep = data.get('rep_status') or False
        self.score_editable = data.get('score_editable') or True
        self.short_name = data.get('short_name') or None

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_users():
        return user.query.all()

    @staticmethod
    def get_one_user(id):
        return user.query.get(id)

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
    name = fields.String(required=True)
    email = fields.String(required=True)
    social_credit_score = fields.Int(required=True)
    user_level = fields.String(required=True)
    is_rep = fields.Boolean(dump_only=True)
    score_editable = fields.Boolean(required=True)
    short_name = fields.String(required=False)