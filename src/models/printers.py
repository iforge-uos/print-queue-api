from marshmallow import fields, Schema
from marshmallow_enum import EnumField
from . import db
import enum


class printer_type(enum.Enum):
    ultimaker = "Ultimaker Extended 2+"
    prusa = "Prusa MK3S+"


class printer_model (db.Model):
    """
        Printer Model
    """
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True)
    printer_name = db.Column(db.String(50), nullable=False)
    printer_type = db.Column(db.Enum(printer_type), nullable=False)
    ip = db.Column(db.String(15), nullable=True)
    api_key = db.Column(db.String(50), nullable=True)
    total_timed_printed = db.Column(db.Integer(), nullable=True)
    completed_prints = db.Column(db.Integer(), nullable=True)
    failed_prints = db.Column(db.Integer(), nullable=True)
    total_filament_used = db.Column(db.Integer(), nullable=True)
    days_on_time = db.Column(db.Integer(), nullable=True)

    # class constructor

    def __init__(self, data):
        """
        Class constructor
        """
        self.printer_name = data.get('printer_name')
        self.printer_type = data.get('printer_type')
        self.ip = data.get('ip') or None
        self.api_key = data.get('api_key') or None
        self.total_timed_printed = data.get('total_timed_printed')
        self.completed_prints = data.get('completed_prints')
        self.failed_prints = data.get('failed_prints')
        self.total_filament_used = data.get('total_filament_used')
        self.days_on_time = data.get('days_on_time')

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
    def get_all_printers():
        return printer_model.query.all()

    @staticmethod
    def get_printer_by_id(id):
        return printer_model.query.get(id)

    @staticmethod
    def get_printer_by_name(value):
        return printer_model.query.filter_by(printer_name=value).first()

    def __repr__(self):
        return "<Printer: %r>" % self.printer_name


class printer_schema(Schema):
    """
    Printer Schema
    """
    id = fields.Int(dump_only=True)
    printer_name = fields.String(required=True)
    printer_type = EnumField(printer_type, required=True)
    ip = fields.String(required=False)
    api_key = fields.String(required=False)
    total_time_printed = fields.Int(required=False)
    completed_prints = fields.Int(required=False)
    failed_prints = fields.Int(required=False)
    total_filament_used = fields.Int(required=False)
    days_on_time = fields.Int(required=False)