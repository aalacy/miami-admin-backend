from flask import jsonify, request
from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger

from app.api import bp
from app.api.scraper import Driver
from app import sched

def run_sysco():
	Driver().run_sysco()

@bp.route('/admin/test', methods=['GET'])
def admin_test():
    return jsonify(message="ok")

@bp.route('/admin/sysco', methods=['GET'])
def get_sysco_prices():
	sched.add_job(run_sysco, DateTrigger(datetime.now()), replace_existing=True)

	return jsonify(status='data')