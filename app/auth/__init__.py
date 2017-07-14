#auth blueprint
# tf 14/07/17
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views