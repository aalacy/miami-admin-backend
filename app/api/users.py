from flask import jsonify, request
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
import os
import uuid0

from app import create_app
from app.api import bp
from app import sched

from app.models import User
from app import db
from app.decorators import parse_header

logger = create_app().logger

@bp.route('/users/register/generate_code')
def generate_code():
    return jsonify(code=uuid0.generate().base62)

@bp.route('/users/register', methods=['POST'])
def register():
    status = 'failure'
    message = 'The user with this email already exists'
    code = 200
    user_data = {}
    data = request.get_json() or {}
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            return jsonify(status=status, message=message)
        user = User(email=data['email'])
        db.session.add(user)
        db.session.commit()
        status = 'success'
        message = 'Successfully sent your registration request to the admin.'
        user_data = user.to_dict()
    except Exception as E:
        code = 500
        logger.warning(str(E))
        message = str(E)

    return jsonify(status=status, message=message, user=user_data), code


@bp.route('/users/login/code', methods=['POST'])
def login():
    data = request.get_json() or {}
    status = 'failure'
    message = 'The user with this email does not exist'
    user = User.query.filter_by(email=data['email']).first()
    if user is None:
        return jsonify(status=status, message=message)
    else:
        if user.get_status() == 'Denied':
            message = 'This user is temporarily denied by admin. Please try it later.'
            return jsonify(status=status, message=message)
        elif user.get_status() == 'Pending':
            message = 'This user is not approved yet. Please contact the admin.'
            return jsonify(status=status, message=message)
        else:
            user.send_request_code()
            db.session.commit()
            status = 'success'
            message = 'Successfully sent a login request code to your email'
            return jsonify(status=status, message=message)

@bp.route('/users/login/verify', methods=['POST'])
def verifylogin():
    data = request.get_json() or {}
    status = 'failure'
    message = 'The user with this email does not exist'

    user = User().verify_code(code=data['code'].strip(), keep_me_login=data['keep'])
    if user:
        status = 'success'
        message = 'Successfully logged in'
        auth_token = user.encode_auth_token()
        db.session.commit()
        return jsonify(status=status, message=message, auth_token=auth_token)
    else:
        status = 'failure'
        message = 'Requested code was expired or does not exist, Please request another code.'
        return jsonify(status=status, message=message)


@bp.route('/users/all', methods=['GET'])
@parse_header
def get_all_users():
    users = User().get_all()

    return jsonify(users=users)


@bp.route('/users/<email>', methods=['PUT'])
@parse_header
def update_user(email):
    status = 'failure'
    message = 'User with this email does not exist'
    code = 200
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            code = 400
        else:
            data = request.get_json() or {}
            user.from_dict(data, new_user=False)
            db.session.commit()
            status = 'success'
            message = 'Successfully updated'
    except Exception as E:
        message = str(E)
        logger.warning(message)
        status = 'failure'
        code = 500

    return jsonify(status=status, message=message), code

@bp.route('/users/<email>', methods=['POST'])
@parse_header
def delete_user(email):
    status = 'failure'
    message = 'User with this email does not exist'
    code = 200
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            code = 400
        else:
            data = request.get_json() or {}
            db.session.delete(user)
            db.session.commit()
            status = 'success'
            message = 'Successfully deleted'
    except Exception as E:
        message = str(E)
        logger.warning(message)
        status = 'failure'
        code = 500

    return jsonify(status=status, message=message), code


