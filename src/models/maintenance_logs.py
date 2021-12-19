from flask import Flask
from . import db
from src.models.printers import printer
from sqlalchemy.sql import func


class maintenance_log (db.Model):
    """
    Maintennance Logs Model
    """
    __tablename__ = 'maintennance_logs'
    id = db.Column(db.Integer, primary_key = True)
    printer_ID = db.column(db.Integer, db.ForeignKey(printer.ID))
    maintenance_date = db.column(db.DateTime(timezone=True), default=func.now())
    maintenance_info = db.column(db.String, nullable=False)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.printer = data.get('printer_id')
        self.maintenance_info = data.get('maintenance_info')

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
    def get_all_maintenance_logs():
        return maintenance_log.query.all()

    @staticmethod
    def get_one_maintenance_log(id):
        return maintenance_log.query.get(id)

    def __repr__(self):
        return "<Maintennance ID: %r>" % self.id
