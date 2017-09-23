# version 1 of an api
# tf 23/09/17
from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, posts, users, comments, errors