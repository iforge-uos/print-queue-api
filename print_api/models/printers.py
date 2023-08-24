import enum

from marshmallow import fields, Schema
from marshmallow_enum import EnumField

from print_api.models import db


class PrinterLocation(enum.Enum):
    heartspace = "Heartspace"
    diamond = "Diamond"


class PrinterType(enum.Enum):
    ultimaker = "Ultimaker Extended 2+"
    prusa = "Prusa MK3S+"


class Printer(db.Model):
    """
    Printer Model
    """

    __tablename__ = "printers"
    id = db.Column(db.Integer, primary_key=True)
    printer_name = db.Column(db.String(50), nullable=False, unique=True)
    printer_type = db.Column(db.Enum(PrinterType), nullable=False)
    ip = db.Column(db.String(15), nullable=True)
    api_key = db.Column(db.String(50), nullable=True)
    total_time_printed = db.Column(db.Integer(), nullable=True)
    completed_prints = db.Column(db.Integer(), nullable=True)
    failed_prints = db.Column(db.Integer(), nullable=True)
    total_filament_used = db.Column(db.Integer(), nullable=True)
    days_on_time = db.Column(db.Integer(), nullable=True)
    location = db.Column(db.Enum(PrinterLocation), nullable=False)

    # class constructor

    def __init__(self, data):
        """
        Class constructor
        """
        self.printer_name = data.get("printer_name")
        self.printer_type = data.get("printer_type")
        self.ip = data.get("ip") or None
        self.api_key = data.get("api_key") or None
        self.total_time_printed = data.get("total_time_printed")
        self.completed_prints = data.get("completed_prints")
        self.failed_prints = data.get("failed_prints")
        self.total_filament_used = data.get("total_filament_used")
        self.days_on_time = data.get("days_on_time")
        self.location = data.get("location")

    def __repr__(self):
        return "<Printer: %r>" % self.printer_name

    def to_dict(self):
        return {
            "id": self.id,
            "printer_name": self.printer_name,
            "printer_type": self.printer_type,
            "ip": self.ip,
            "api_key": self.api_key,
            "total_time_printed": self.total_time_printed,
            "completed_prints": self.completed_prints,
            "failed_prints": self.failed_prints,
            "total_filament_used": self.total_filament_used,
            "days_on_time": self.days_on_time,
            "location": self.location,
        }

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

    def get_model_dict(self):
        """
        Function to get the models attributes as a dictionary
        :return dictionary: a dict containing all the objects attributes
        """
        return self.__dict__

    @staticmethod
    def get_all_printers():
        """
        Function to get all the printers in the database
        :return query_object: a query object containing all the printer
        """
        return Printer.query.all()

    @staticmethod
    def get_printer_by_id(p_id):
        """
        Function to get a single printer from the database by its ID
        :param int p_id: the PK of the printer
        :return query_object: a query object containing the printer
        """
        return Printer.query.get(p_id)

    @staticmethod
    def get_printer_by_name(value):
        """
        Function to get a single printer from the database by its name
        :param str value: the string name of the printer
        :return query_object: a query object containing the printer
        """
        return Printer.query.filter_by(printer_name=value).first()


class PrinterSchema(Schema):
    """
    Printer Schema
    """

    id = fields.Int(dump_only=True)
    printer_name = fields.String(required=True)
    printer_type = EnumField(PrinterType, required=True)
    ip = fields.String(required=False, allow_none=True, missing="")
    api_key = fields.String(required=False, allow_none=True, missing="")
    total_time_printed = fields.Int(required=False)
    completed_prints = fields.Int(required=False)
    failed_prints = fields.Int(required=False)
    total_filament_used = fields.Int(required=False)
    days_on_time = fields.Int(required=False)
    location = EnumField(PrinterLocation, required=True)
