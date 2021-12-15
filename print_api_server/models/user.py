from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from print_api_server.models.printer import printer


class user(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    social_credit_score = db.Column(db.Integer, nullable=False)
    user_level = db.Column(db.String, nullable=False)
    is_rep = db.Column(db.Boolean, nullable=False)
    score_editable = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<User: %r>" % self.name