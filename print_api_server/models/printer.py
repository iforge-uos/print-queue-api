from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import enum

class printer_type(enum.Enum):
    ultimaker = "Ultimaker Extended 2+"
    prusa = "Prusa MK3S+"


class printer (db.Model):
    __tablename__ = 'printers'
    id = db.Column(db.Integer, primary_key = True)
    printer_name = db.Column(db.String(50), nullable = False) 
    printer_type = db.Column(Enum(printer_type), nullable = False)
    ip = db.Column(db.String(15), nullable = True)
    api_key = db.Column(db.String(50), nullable = False)
    total_timed_printed = db.Column(db.Integer(), nullable = False)
    completed_prints = db.Column(db.Integer(), nullable = False)
    failed_prints = db.Column(db.Integer(), nullable = False)
    total_filament_used = db.Column(db.Integer(), nullable = False)
    days_on_time = db.Column(db.Integer(), nullable = False)

    def __repr__(self):
        return "<Printer: %r>" % self.printer_name