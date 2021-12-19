import enum
from flask import Flask
from . import db
from sqlalchemy.sql import func
from src.models.user import user
from src.models.printers import printer


class job_status(enum.Enum):
    queued = "Queued"
    running = "Running"
    complete = "Complete"
    failed = "Failed"
    rejected = "Rejected"
    under_review = "Under Review"


class project_types(enum.Enum):
    personal = "Personal"
    module = "Module :"
    co_curricular = "Co-curricular: "
    other = "Other"


class print_job (db.Model):
    """
    Print Jobs Model
    """
    __tablename__ = 'print_jobs'
    id = db.Column(db.Integer, primary_key=True)
    is_queued = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user.ID), nullable=False)
    gcode_slug = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    date_started = db.Column(db.DateTime(timezone=True), nullable=True)
    date_ended = db.Column(db.DateTime(timezone=True), nullable=True)
    colour = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    checked_by = db.Column(db.Integer, db.ForeignKey(user.ID))
    printer = db.Column(db.Integer, db.ForeignKey(printer.ID), nullable=True)
    project = db.Column(enum(project_types), nullable=False)
    status = db.Column(enum(job_status), nullable=False)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.is_queued = True
        self.user_id = data.get('user_id')
        self.gcode_slug = data.get('gcode_slug')
        self.date_started = None
        self.date_ended = None
        self.colour = None
        self.notes = data.get('notes')
        self.checked_by = data.get('rep_id')
        self.printer = None
        self.project = data.get('project')
        self.status = job_status.queued

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
    def get_all_print_jobs():
        return print_job.query.all()

    @staticmethod
    def get_one_print_job(id):
        return print_job.query.get(id)

    def __repr__(self):
        return "<Job ID: %r>" % self.id
