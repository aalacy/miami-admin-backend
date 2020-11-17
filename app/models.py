import base64
from datetime import datetime, date, timedelta
from hashlib import md5
import json
import os
import uuid0
from time import time
import pdb
import jwt
from flask import current_app, url_for, jsonify

from app import db
from app.email import Email

myemail = Email()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    status = db.Column(db.String(32), default="Active")
    role = db.Column(db.String(32), default="Customer")
    code = db.Column(db.String(32), index=True, unique=True)
    code_expiration = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'status': self.status,
            'role': self.role,
            'code': self.code,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in data:
            setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def encode_auth_token(self):
        """Generates the auth token"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(
                    days=10000,
                    seconds=0
                ),
                'iat': datetime.utcnow(),
                'id': self.id,
                'email' : self.email,
                'role' : self.role # staff, admin, root
            }
            return jwt.encode(
                payload,
                'secret',
                algorithm='HS256'
            ).decode()
        except Exception as e:
            raise e

    @staticmethod
    def decode_auth_token(auth_token):
        """Decodes the auth token

        :params auth_token:

        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, 'secret')
            return (0, payload)
        # except jwt.ExpiredSignatureError:
        #     return (1, 'Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            return (2, 'Invalid token. Please log in again.')




    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    def get_status(self):
        return self.status

    def send_request_code(self, expires_in=3000):
        self.code = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.code_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        msg = f'Here is your login request code. \n{self.code} \nIt will expire in 5 mins.'
        subject = '[Miami] Authentication'
        myemail.send_message(msg, subject, [self.email])

    @staticmethod
    def verify_code(code='', keep_me_login=False):
        user = User.query.filter_by(code=code).first()
        if user is None or user.code_expiration is None or user.code_expiration < datetime.utcnow():
            return None
        
        user.code_expiration = datetime.utcnow()
        return user

    @staticmethod
    def get_all():
        users = User.query.all()
        items = [user.to_dict() for user in users]
        return items

    @staticmethod
    def verify_token(token):
        status = True
        user = User.query.filter_by(email=token['email']).first()
        if user:
            if user.status != 'Active':
                status = False

        else:
            status = False

        return status