#views for auth blueprint
#14/07/17 tf
from flask import render_template
from flask_login import login_required
from . import auth

@auth.route('/login')
def login():
    ## templates are relative to the app's template folder
    ## it's where Flask will search for the templates
    ## you need to create a folder in templates called auth
    return render_template('auth/login.html')


@auth.route('/secret')
@login_required
def secret():
    return "Only authenticated users are allowed!"