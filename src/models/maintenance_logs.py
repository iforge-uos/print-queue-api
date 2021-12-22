from marshmallow import fields, Schema
from . import db
from models.printers import printer_model
from sqlalchemy.sql import func


class maintenance_model (db.Model):
    """
    Maintenance Logs Model
    """
    __tablename__ = 'maintenance_logs'
    id = db.Column(db.Integer, primary_key = True)
    printer_id = db.Column(db.Integer, db.ForeignKey(printer_model.id), nullable=False)
    maintenance_date = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    maintenance_info = db.Column(db.String, nullable=False)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.printer_id = data.get('printer_id')
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
        return maintenance_model.query.all()

    @staticmethod
    def get_maintenance_log_by_id(id):
        return maintenance_model.query.get(id)

    @staticmethod
    def get_maintenance_logs_by_printer_id(value):
        return maintenance_model.query.filter_by(printer_id=value).all()

    def __repr__(self):
        return "<Maintennance ID: %r>" % self.id

class maintenance_schema(Schema):
    """
    Maintenance Schema
    """
    id = fields.Int(dump_only=True)
    printer_id = fields.Int(required=True)
    maintenance_date = fields.Date()
    maintenance_info = fields.String(required=True)

