from flask import Flask
from . import db
import enum


class printer_type(enum.Enum):
    ultimaker = "Ultimaker Extended 2+"
    prusa = "Prusa MK3S+"


class printer (db.Model):
    """
        Printer Model
    """
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key=True)
    printer_name = db.Column(db.String(50), nullable=False)
    printer_type = db.Column(enum(printer_type), nullable=False)
    ip = db.Column(db.String(15), nullable=True)
    api_key = db.Column(db.String(50), nullable=True)
    total_timed_printed = db.Column(db.Integer(), nullable=False)
    completed_prints = db.Column(db.Integer(), nullable=False)
    failed_prints = db.Column(db.Integer(), nullable=False)
    total_filament_used = db.Column(db.Integer(), nullable=False)
    days_on_time = db.Column(db.Integer(), nullable=False)

    # class constructor

    def __init__(self, data):
        """
        Class constructor
        """
        self.printer_name = data.get('printer_name')
        self.printer_type = data.get('printer_type')
        self.ip = data.get('ip') or None
        self.api_key = data.get('api_key') or None
        self.total_timed_printed = data.get('total_timed_printed') or 0
        self.completed_prints = data.get('completed_prints') or 0
        self.failed_prints = data.get('failed_prints') or 0
        self.total_filament_used = data.get('total_filament_used') or 0
        self.days_on_time = data.get('days_on_time') or 0


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
        return printer.query.all()

    @staticmethod
    def get_one_printer(id):
        return printer.query.get(id)

    def __repr__(self):
        return "<Printer: %r>" % self.printer_name
