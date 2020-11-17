from functools import wraps
from flask import jsonify, request, make_response
import json

from app.models import User
from app import create_app
from app import db
import pdb

logger = create_app().logger

def parse_header(f):
	'''
		Authentiicates Users through checking assigned oAuth token.
		Valid: 30 days
		only company user can access his own data, while admin can access any data
	'''
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# parse data: email, role, id
		# parse auth
		response_object = {
			'status': 'failure',
			'message': ''
		}
		auth_header = request.headers.get('Authorization')
		if not auth_header:
			response_object['message'] = 'Provide a valid auth token.'
			return make_response(jsonify(response_object), 403)

		code, payload = User.decode_auth_token(auth_header)
		if code != 0:
			response_object['message'] = payload
			return make_response(jsonify(response_object), 403)
		else:
			if not User.verify_token(payload):
				return make_response(jsonify(response_object), 403)

		return f(*args, **kwargs)
	return decorated_function

