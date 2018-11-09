# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
#from passlib.hash import pbkdf2_sha256 as sha256
from Crypto.Hash import SHA256


class UserProxy:

    def __init__(self, id):
        self.id = id

class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<KB %r>' % self.username

    def __str__(self):
        return "User(username='%s')" % self.username

    @staticmethod
    def generate_hash(password):
        sha256 = SHA256.new()
        sha256.update(password.encode())
        return sha256.hexdigest()






