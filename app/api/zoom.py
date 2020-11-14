import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, Column, Text, BLOB, \
					Integer, Text, String, MetaData, DateTime, JSON, select, Boolean
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pdb

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class ZoomDB:

	def __init__(self):
		Base = declarative_base()
		metadata = MetaData()
		engine = create_engine(os.environ.get('DATABASE_URL'))
		self.connection = engine.connect()
		metadata.bind = engine
		metadata.clear()

		self.recording_upload = Table(
			'recording_upload', 
			metadata,
			Column('id', Integer, primary_key=True),
			Column('topic', String(512)),
			Column('meeting_id', String(512)),
			Column('recording_id', String(512)),
			Column('meeting_uuid', String(512)),
			# Column('meeting_link', String(512)),
			Column('start_time', String(512)),
			Column('file_name', String(512)),
			Column('file_size', Integer),
			Column('cnt_files', Integer),
			Column('recording_link', String(512)),
			Column('folder_link', String(512)),
			Column('status', String(256)),
			Column('message', Text),
			Column('run_at', String(256)),
		)

		self.upload_status = Table(
			'meeting_upload_status', 
			metadata,
			Column('id', Integer, primary_key=True),
			Column('topic', String(512)),
			Column('meeting_id', String(512)),
			Column('meeting_uuid', String(512)),
			# Column('meeting_link', String(512)),
			Column('start_time', String(512)),
			Column('folder_link', String(512)),
			Column('cnt_files', Integer),
			Column('status', Boolean),
			Column('is_deleted', Boolean),
			Column('run_at', String(256)),
		)

		self.alert_email = Table(
			'alert_email', 
			metadata,
			Column('id', Integer, primary_key=True),
			Column('cc_emails', Text)
		)

		metadata.create_all()

	def add_item_to_items(self, item):
		is_exist = False
		new_items = []
		for _item in self.items:
			if _item['meeting_id'] == item['meeting_id']:
				is_exist = True
				_item['recording_files'].append(item)

			new_items.append(_item)

		if not is_exist:
			new_items.append({
				'meeting_id': item['meeting_id'],
				'topic': item['topic'],
				'start_time': item['start_time'],
				'cnt_files': item['cnt_files'],
				'run_at': item['run_at'],
				'show': False,
				'recording_files': [item]
			})

		self.items = new_items

	def read_today_recordings(self):
		self.read_all_recordings()

		today = (datetime.today()).strftime('%m/%d')
		yesterday = (datetime.today() - timedelta(days=1)).strftime('%m/%d')
		today_items = [item for item in self.items if today in item['run_at']]

		self.connection.close()

		return today_items

	def read_all_recordings(self):
		res = self.connection.execute('SELECT * FROM recording_upload')
		self.items = []
		for r in res:
			self.add_item_to_items(dict(r))
		
		self.connection.close()
		return self.items

	def get_alert_emails(self):
		res = self.connection.execute('SELECT * FROM alert_email LIMIT 1')
		items = [dict(r) for r in res]
		if items:
			return items[0]
		return {}

	def update_alert_emails(self, data):
		if data.get('id', ''):
			update_statement = self.alert_email.update().where(self.alert_email.c.id == data['id']).values({
					'cc_emails': data['cc_emails']
				})

			self.connection.execute(update_statement)
		else:
			self.connection.execute(self.alert_email.insert(), data)
