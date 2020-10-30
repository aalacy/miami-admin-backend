from flask import jsonify, request
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
import os

from app import create_app
from app.api import bp
from app.api.scraper import Driver
from app import sched
from flask import send_from_directory

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