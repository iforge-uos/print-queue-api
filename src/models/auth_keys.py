from marshmallow import fields, Schema
from extensions import db
from sqlalchemy.sql import func

"""
Permission Values
3 All Rights (Admin Access)
2 Print Server Access Only (Reading and Writing to all Databases except auth)
1 Print Queue Client Access Only (Writing to Users and Print Jobs)
0 No rights

"""

class auth_model(db.Model):
    """
    Auth Model
    """
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    associated_version = db.Column(db.String,nullable=True)
    permission_value = db.Column(db.Integer, nullable=False)
    # class constructor

    def __init__(self, data):
        """
        Class constructor
        """
        print(data)
        self.key = data.get('key')
        self.associated_version = data.get('associated_version')
        self.permission_value = data.get('permission_value')

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
    def get_all_keys():
        """
        Function to get all the keys in the database
        :return query_object: a query object containing all the keys
        """
        return auth_model.query.all()

    @staticmethod
    def get_key_by_id(id):
        """
        Function to get a key by their ID
        :param int id: PK of the key
        :return query_object: a query object containing the key
        """
        return auth_model.query.get(id)

    @staticmethod
    def get_key_by_key(key):
        """
        Function to get a key by their ID
        :param str key: the key value
        :return query_object: a query object containing the key
        """
        return auth_model.query.filter_by(key=key).first()


    @staticmethod
    def get_keys_by_associated_version(version):
        """
        Function to get keys by its associated version
        :param str version: the software version of the client used with the key
        :return query_object: a query object containing the keys
        """
        return auth_model.query.filter_by(associated_version=version).all()

    def __repr__(self):
        return "<Key: %r>" % self.key


class auth_schema(Schema):
    """
    Key Schema
    """
    id = fields.Int(dump_only=True)
    key = fields.String(required=True)
    date_added = fields.DateTime(required=False)
    associated_version = fields.String(required=True)
    permission_value = fields.Int(required=True)