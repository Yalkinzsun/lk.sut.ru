from flask import Flask
from . import users_db as db
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))