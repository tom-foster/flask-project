from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
## i need to write the decorator
from .decorators import permission required
from .errors import forbidden


@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts' : [post.to_json() for post in posts]})

