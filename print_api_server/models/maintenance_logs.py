from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from print_api_server.models.printer import printer


class maintenance_log (db.Model):
    __tablename__ = 'maintennance_logs'
    id = db.Column(db.Integer, primary_key = True)
    printer_ID = db.column(db.Integer, ForeignKey(printer.ID))
    maintenance_date = db.column(db.Date, nullable=False)
    maintenance_info = db.column(db.String, nullable=False)

    def __repr__(self):
        return "<Maintennance ID: %r>" % self.id
