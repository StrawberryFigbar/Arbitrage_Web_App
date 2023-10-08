from Website import db
from flask_login import UserMixin
import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    bet_amount = db.Column(db.Integer)
    key = db.relationship('Api_Key', backref="User")
    events = db.relationship('Event')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(30))
    sports_key = db.Column(db.Integer)
    earnings = db.Column(db.Float)
    arbitrage_percent = db.Column(db.Float)
    outcomes = db.relationship('Outcome')
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookmaker = db.Column(db.String(50))
    name = db.Column(db.String(100))
    odds = db.Column(db.Integer)
    bet_amount = db.Column(db.Float)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))


class Api_Key(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True),
                     default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
