#tf 09/07/17
#now using blueprints
from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User, Permission
from ..emails import send_email
from ..decorators import admin_required, permission_required
from flask_login import login_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASK_ADMIN']:
                send_email(current_app.config['FLASK_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        ## Blueprints introduce the name space, so there are no conflicting errors
        ## in larger apps.
        ## you use .index to refer to main.index.
        ## redirects across blueprints must use the name spaced endpoint name.
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.now())

# examples for the new decorators that have been made.
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For admin eyes only"

@main.route('/moderators')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For moderators only!"