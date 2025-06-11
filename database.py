from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.String(8), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    type = db.Column(db.String(50), nullable=False)  # 'deposit' or 'transfer'
    def __repr__(self):
        return f"<Transaction {self.id} - {self.amount} {self.type}>"

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

class Check(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String(4), unique=True, nullable=False)  # код чека должен быть 4-значным
    amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='checks')

User.checks = relationship('Check', order_by=Check.id, back_populates='user')

