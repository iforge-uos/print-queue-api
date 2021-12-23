import enum
from typing_extensions import Required
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from . import db
from sqlalchemy.sql import func
from src.models.user import user
from src.models.printers import printer


class job_status(enum.Enum):
    queued = "Queued"
    accepted = "Accepted"
    awaiting = "Awaiting Approval"
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


class print_job_model (db.Model):
    """
    Print Jobs Model
    """
    __tablename__ = 'print_jobs'
    id = db.Column(db.Integer, primary_key=True)
    is_queued = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey(user.ID))
    print_name = db.Column(db.String(60), nullable=False)
    gcode_slug = db.Column(db.String, nullable=False)
    stl_slug = db.Column(db.String, nullable=True) 
    date_added = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    date_started = db.Column(db.DateTime(timezone=True), nullable=True)
    date_ended = db.Column(db.DateTime(timezone=True), nullable=True)
    colour = db.Column(db.String, nullable=True)
    upload_notes = db.Column(db.String, nullable=True)
    queue_notes = db.Column(db.String, nullable=True)
    checked_by = db.Column(db.Integer, db.ForeignKey(user.ID), nullable=True)
    printer = db.Column(db.Integer, db.ForeignKey(printer.ID), nullable=True)
    project = db.Column(enum(project_types), nullable=False)
    project_string = db.Column(db.String, nullable=True)
    status = db.Column(enum(job_status), nullable=False)
    # Print time in seconds
    print_time = db.Column(db.Integer, nullable=True)
    # Filament in grams
    filament = db.Column(db.Integer, nullable=True)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        # Making it so that approval jobs can be part of the print job model
        if (data.get("job_status") == job_status.awaiting):
            self.is_queued = False
            self.status = job_status.awaiting
            self.stl_slug = data.get('stl_slug')
        else:
            self.is_queued = True
            self.status = job_status.queued
            self.stl_slug = None
        
        # If co-curricular or uni module store group name / code
        project = data.get('project')
        if (project == project_types.personal):
            self.project = project
        else:
            self.project = project
            self.project_string = data.get('project_name')

        self.user_id = data.get('user_id')
        self.print_name = data.get('print_name')
        self.gcode_slug = data.get('gcode_slug')
        self.date_started = None
        self.date_ended = None
        self.colour = None
        self.upload_notes = data.get('notes')
        self.checked_by = data.get('rep_id')
        self.printer = None
        self.project = data.get('project')
        self.print_time = data.get('print_time')
        self.filament = data.get('filament_used')

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
        return print_job_model.query.all()

    @staticmethod
    def get_print_job_by_id(id):
        return print_job_model.query.get(id)

    @staticmethod
    def get_print_jobs_by_status(status):
        return print_job_model.query.filter_by(status=status).all()
    
    
    
    def __repr__(self):
        return "<Job ID: %r>" % self.id

    
class print_job_schema(Schema):
    """
    Print Job Schema
    """
    id = fields.Int(dump_only=True)
    is_queued = fields.Boolean(required=True)
    user_id = fields.Int(required=True)
    print_name = fields.String(required=True)
    gcode_slug = fields.String(required=True)
    stl_slug = fields.String(required=False)
    date_added = fields.DateTime()
    date_started = fields.DateTime()
    date_finished = fields.DateTime()
    colour = fields.String(required=True)
    upload_notes = fields.String(required=False)
    queue_notes = fields.String(required=False)
    checked_by = fields.Int(required=True)
    printer = fields.Int(required=False)
    project = EnumField(project_types, required=True)
    project_string = fields.String(required=False)
    status = EnumField(job_status, required=True)
    print_time = fields.Int(required=False)
    filament = fields.Int(required=False)