from flask import jsonify, request
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
import os

from app import create_app
from app.api import bp
from app.api.scraper import Driver
from app import sched
from flask import send_from_directory

logger = create_app().logger
SYSCO_DATASHEET = '_Item List.xlsx'

def run_scraper():
	Driver().run_scraper()

@bp.route('/static/download')
def root():
	root_dir = os.path.dirname(os.getcwd())
	path = f'{root_dir}/backend/app/api/data/'
	return send_from_directory(path, '_Item List.xlsx')

@bp.route('/admin/test', methods=['GET'])
def admin_test():
    return jsonify(message="ok")

@bp.route('/admin/sysco', methods=['GET'])
def get_sysco_prices():
	sched.add_job(run_scraper, DateTrigger(datetime.now()), replace_existing=True)

	return jsonify(status='data')

@bp.route('/admin/upload', methods=['POST'])
def upload_sheet():
	status = 'success'
	message = 'Successfully uploaded'
	code = 200
	file_obj = request.files

	UPLOAD_FOLDER = os.path.join(os.path.abspath(os.curdir), "app/api/data")
	csv_data = []
	file = file_obj.get('file')
	if file:
		try:
			keypath = os.path.join(UPLOAD_FOLDER, SYSCO_DATASHEET)
			file.save(keypath)
		except Exception as E:
			message = 'Something wrong happened on the server.'
			logger.warning(str(E))
			status = 'failure'
			code = 500
	else:
		status = 'failure'
		message = 'No file provided'
		logger.warning(message)
		code = 400

	return jsonify(status=status, message=message), code

@bp.route('/admin/read_sheet', methods=['GET'])
def read_sheetdata():
	items = []
	headers = []
	message = 'Successfully done.'
	status = 'success'
	code = 200
	try:
		items, headers = Driver().read_sheet_as_table()
	except Exception as E:
		logger.warning(str(E))
		message = str(E)
		status = 'failed'
		code = 500

	return jsonify(status=status, message=message, items=items, headers=headers), code