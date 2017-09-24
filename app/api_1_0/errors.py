from flask import jsonify
from app.exceptions import ValidationError
from . import api

def bad_request(message):
    response = jsonify({'error' : 'bad request', 'message': message})
    response.status_code = 400
    return response
