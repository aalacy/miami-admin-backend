from flask import jsonify, request
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
import os

from app import create_app
from app.api import bp
from app import sched
from app.api.zoom import ZoomDB
from flask import send_from_directory

from app.models import User
from app import db

logger = create_app().logger
SYSCO_DATASHEET = '_Item List.xlsx'

@bp.route('/static/download')
def root():
	root_dir = os.path.dirname(os.getcwd())
	path = f'{root_dir}/backend/app/api/data/'
	return send_from_directory(path, '_Item List.xlsx')

@bp.route('/admin/test', methods=['GET'])
def admin_test():
    return jsonify(message="ok")

@bp.route('/admin/read/today', methods=['GET'])
def read_today_data():
	items = []
	message = 'Successfully done.'
	status = 'success'
	code = 200
	try:
		items = ZoomDB().read_today_recordings()
	except Exception as E:
		logger.warning(str(E))
		message = str(E)
		status = 'failed'
		code = 500

	return jsonify(status=status, message=message, items=items), code

@bp.route('/admin/read', methods=['GET'])
def read_all_data():
	items = []
	message = 'Successfully done.'
	status = 'success'
	code = 200
	try:
		items = ZoomDB().read_all_recordings()
	except Exception as E:
		logger.warning(str(E))
		message = str(E)
		status = 'failed'
		code = 500

	return jsonify(status=status, message=message, items=items), code

@bp.route('/admin/alert/get', methods=['GET'])
def read_alert_emails():
	items = []
	message = 'Successfully done.'
	status = 'success'
	code = 200
	try:
		items = ZoomDB().get_alert_emails()
	except Exception as E:
		logger.warning(str(E))
		message = str(E)
		status = 'failed'
		code = 500

	return jsonify(status=status, message=message, items=items), code

@bp.route('/admin/alert/update', methods=['POST'])
def read_update_emails():
	items = []
	message = 'Successfully done.'
	status = 'success'
	code = 200
	try:
		items = ZoomDB().update_alert_emails(request.get_json())
	except Exception as E:
		logger.warning(str(E))
		message = str(E)
		status = 'failed'
		code = 500

	return jsonify(status=status, message=message, items=items), code

# Auth


@bp.route('/users/register', methods=['POST'])
def register():
    status = 'failure'
    message = 'The user with this email already exists'
    code = 200
    user_data = {}
    data = request.get_json() or {}
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user and user.get_status() != 'Denied':
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


