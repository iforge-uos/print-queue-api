from marshmallow import fields, Schema
from sqlalchemy.sql import func

from print_api.models import db
from print_api.models.printers import Printer


class MaintenanceLog(db.Model):
    """
    Maintenance Logs Model
    """

    __tablename__ = "maintenance_logs"
    id = db.Column(db.Integer, primary_key=True)
    printer_id = db.Column(
        db.Integer, db.ForeignKey(Printer.id, ondelete="cascade"), nullable=False
    )
    maintenance_date = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    maintenance_info = db.Column(db.String, nullable=False)
    done_by = db.Column(db.String, nullable=False)

    # class constructor
    def __init__(self, data):
        """
        Class constructor
        """
        self.printer_id = data.get("printer_id")
        self.maintenance_info = data.get("maintenance_info")
        self.done_by = data.get("done_by")

    def __repr__(self):
        return "<maintenance ID: %r>" % self.id

    def to_dict(self):
        return {
            "id": self.id,
            "printer_id": self.printer_id,
            "maintenance_date": self.maintenance_date,
            "maintenance_info": self.maintenance_info,
            "done_by": self.done_by,
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

    @staticmethod
    def get_all_maintenance_logs():
        """
        Function to get all the maintenance logs in the database
        :return query_object: a query object containing all the maintenance logs
        """
        return MaintenanceLog.query.all()

    @staticmethod
    def get_maintenance_log_by_id(m_id):
        """
        Function to get a single maintenance logs from the database
        :param int m_id: the PK of the log
        :return query_object: a query object containing the maintenance log
        """
        return MaintenanceLog.query.get(m_id)

    @staticmethod
    def get_maintenance_logs_by_printer_id(value):
        """
        Function to get all maintenance logs associated with a certain printer from the database
        :param int value: the PK of the printer in the database
        :return query_object: a query object containing the maintenance logs associated with that printer
        """
        return MaintenanceLog.query.filter_by(printer_id=value).all()


class MaintenanceSchema(Schema):
    """
    Maintenance Schema
    """

    id = fields.Int(dump_only=True)
    printer_id = fields.Int(required=True)
    maintenance_date = fields.Date()
    maintenance_info = fields.String(required=True)
    done_by = fields.String(required=True)
