import enum
import os
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from print_api.models import db
from sqlalchemy.sql import func

from print_api.models import User, Printer
from print_api.models.printers import printer_type


class job_status(enum.Enum):
    queued = "Queued"
    approval = "Awaiting Approval"
    running = "Running"
    completed = "Completed"
    failed = "Failed"
    rejected = "Rejected"
    under_review = "Under Review"


class project_types(enum.Enum):
    personal = "Personal"
    uni_module = "Module"
    co_curricular = "Co-curricular"
    society = "Society"
    other = "Other"


class PrintJob(db.Model):
    """
    Print Jobs Model
    """

    __tablename__ = "print_jobs"
    gcode_slug = db.Column(db.String, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    # Filament in grams
    filament_usage = db.Column(db.Integer, nullable=False)
    print_name = db.Column(db.String(60), nullable=False)
    # Print time in seconds
    print_time = db.Column(db.Integer, nullable=False)
    printer_type = db.Column(db.Enum(printer_type), nullable=False)
    project = db.Column(db.Enum(project_types), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    date_added = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_ended = db.Column(
        db.DateTime(timezone=True), nullable=True, server_onupdate=func.now()
    )
    date_started = db.Column(
        db.DateTime(timezone=True), nullable=True, server_onupdate=func.now()
    )
    colour = db.Column(db.String, nullable=True)
    printer = db.Column(db.Integer, db.ForeignKey(Printer.id), nullable=True)
    project_string = db.Column(db.String, nullable=True)
    queue_notes = db.Column(db.String, nullable=True, default="")
    rep_check = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    status = db.Column(db.Enum(job_status), nullable=False)
    stl_slug = db.Column(db.String, nullable=True)
    upload_notes = db.Column(db.String, nullable=True)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.gcode_slug = data.get("gcode_slug")
        self.filament_usage = data.get("filament_usage")
        self.print_name = data.get("print_name")
        self.print_time = data.get("print_time")
        self.printer_type = data.get("printer_type")
        self.project = data.get("project")
        self.user_id = data.get("user_id")
        self.colour = None
        self.date_started = None
        self.date_ended = None
        self.printer = None
        self.rep_check = data.get("rep_check")
        self.upload_notes = data.get("upload_notes")

        # if data

        # Making it so that approval jobs can be part of the print job model
        if data.get("status") == job_status.approval:
            self.status = job_status.approval
            self.stl_slug = data.get("stl_slug")
        else:
            self.stl_slug = None

            # catch high failure risk and long prints with auto-review
            fail_threshold = float(os.getenv('AUTOREVIEW_FAIL_THRESHOLD'))
            start_threshold = int(os.getenv('AUTOREVIEW_START_THRESHOLD'))
            time_threshold = int(os.getenv('AUTOREVIEW_TIME_THRESHOLD'))

            check_rep = User.get_user_by_id(self.rep_check)

            if (check_rep.slice_completed_count + check_rep.slice_failed_count + check_rep.slice_rejected_count) < start_threshold:
                # catch when reps are only just starting slicing
                self.status = job_status.under_review
            else:
                # catch based on failure(/reject) rate
                fail_rate = (check_rep.slice_failed_count + check_rep.slice_rejected_count) / (check_rep.slice_completed_count + check_rep.slice_failed_count + check_rep.slice_rejected_count)
                if fail_rate < fail_threshold and self.print_time < time_threshold:
                    # failure rate low enough AND print short enough
                    self.status = job_status.queued
                else:
                    self.status = job_status.under_review

        # If co-curricular or uni module store group name / code
        self.project = data.get("project")
        if self.project is not project_types.personal:
            self.project_string = data.get("project_name")

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
    def get_all_print_jobs():
        """
        Function to get all the print jobs in the database
        :return query_object: a query object containing all the print jobs
        """
        return PrintJob.query.all()

    @staticmethod
    def get_print_job_by_id(id):
        """
        Function to get a single print job from the database
        :param int id: the PK of the job
        :return query_object: a query object containing the print job
        """
        return PrintJob.query.get(id)

    @staticmethod
    def get_print_jobs_by_status(status):
        """
        Function to get all the pint jobs from the database filtered by the job status
        :param str status: the key of the status enum that carries the job state
        :return query_object: a query object containing all the print jobs of the aforementioned status
        """
        return PrintJob.query.filter_by(status=job_status[status]).all()

    def __repr__(self):
        return "<Job ID: %r>" % self.id


class print_job_schema(Schema):
    """
    Print Job Schema
    """

    gcode_slug = fields.String(required=True)
    id = fields.Int(dump_only=True)
    filament_usage = fields.Int(required=True)
    print_name = fields.String(required=True)
    print_time = fields.Int(required=True)
    printer_type = EnumField(printer_type, required=True)
    project = EnumField(project_types, required=True)
    user_id = fields.Int(required=True)

    colour = fields.String(required=False)
    date_added = fields.DateTime(required=False)
    date_started = fields.DateTime(required=False)
    date_ended = fields.DateTime(required=False)
    printer = fields.Int(required=False)
    project_string = fields.String(required=False)
    queue_notes = fields.String(required=False)
    rep_check = fields.Int(required=False)
    status = EnumField(job_status, required=False)
    stl_slug = fields.String(required=False)
    upload_notes = fields.String(required=False)
