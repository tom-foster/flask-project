# Blueprints are only associated with an application
# until they are associated with it
# tf 09/07/17
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors