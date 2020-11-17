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
from app.decorators import parse_header

logger = create_app().logger

@bp.route('/static/download')
def root():
	root_dir = os.path.dirname(os.getcwd())
	path = f'{root_dir}/backend/app/api/data/'
	return send_from_directory(path, '_Item List.xlsx')

@bp.route('/admin/test', methods=['GET'])
def admin_test():
    return jsonify(message="ok")

@bp.route('/admin/read/today', methods=['GET'])
@parse_header
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
@parse_header
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
@parse_header
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
@parse_header
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
