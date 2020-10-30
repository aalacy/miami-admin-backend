import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from dotenv import load_dotenv
from config import Config
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

jobstores = {
  'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
  'default': ThreadPoolExecutor(20),
  'processpool': ProcessPoolExecutor(10)
}
job_defaults = {
  'coalesce': False,
  'max_instances': 10
}
sched = BackgroundScheduler(jobstores=jobstores, 
executors=executors, job_defaults=job_defaults, timezone='GMT')
sched.start()

def create_app(config_class=Config):
	app = Flask(__name__, static_folder='static')
	CORS(app)
	app.config.from_object(config_class)

	from app.api import bp as api_bp
	app.register_blueprint(api_bp, url_prefix='/api')

	if app.config['LOG_TO_STDOUT']:
		stream_handler = logging.StreamHandler()
		stream_handler.setLevel(logging.INFO)
		app.logger.addHandler(stream_handler)
	else:
		if not os.path.exists('logs'):
			os.mkdir('logs')
		file_handler = RotatingFileHandler('logs/automation.log',
											maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter(
			'%(asctime)s %(levelname)s: %(message)s '
			'[in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)

	app.logger.setLevel(logging.INFO)
	app.logger.info('automation startup')

	return app