from sqlalchemy import DateTime
import datetime
from InterfaceSoft import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)

    @repr
    def __repr__(self):
        return f'<User {self.firstname, self.lastname}>'


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trans_id = db.Column(db.String(120), nullable=False)
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    order_num = db.Column(db.BigInteger, nullable=False)
    requestor_id = db.Column(db.String(20), nullable=False)
    temp_1 = db.Column(db.Float, nullable=False)
    temp_2 = db.Column(db.Float, nullable=False)
    rtd_1 = db.Column(db.Float, nullable=False)
    rtd_2 = db.Column(db.Float, nullable=False)
    is_data_transmitted = db.Column(db.Boolean, default=False)

    @repr
    def __repr__(self):
        return f'<Reading {self.trans_id, self.id}>'

    # define the as_dict method here
    def as_dict(self):
        # return a dictionary representation of the model object
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


