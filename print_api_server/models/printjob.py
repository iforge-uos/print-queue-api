from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from print_api_server.models.user import user


class maintenance_log (db.Model):
    __tablename__ = 'queue_jobs'
    id = db.Column(db.Integer, primary_key = True)
    is_queued = db.Column(db.Boolean, default = True)
    user_id = db.Column(db.Integer, ForeignKey(user.ID))
    gcode_slug = db.Column(db.String, nullable=True)
    dateAdded = db.Column(db.Date, nullable=False)
    dateStarted = db.Column(db.Date, nullable=False)
    dateEnded = db.Column(db.Date, nullable=False)
    color = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    checkedBy = db.Column(db.Integer, ForeignKey(user.ID))
    printer = db.Column(db.Integer, ForeignKey(printer.ID))
    project = db.Column(Enum(project_types), nullable=False)
    status = db.Column(Enum(job_status), nullable=False)

    def __repr__(self):
        return "<Maintennance ID: %r>" % self.id