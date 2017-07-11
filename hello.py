# import os
# from datetime import datetime
# from threading import Thread
# from flask import Flask, request, make_response, redirect, \
#      render_template, url_for, session, flash
# from flask_script import Manager, Shell
# from flask_bootstrap import Bootstrap
# from flask_moment import Moment
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import Required
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate, MigrateCommand
# from flask_mail import Mail, Message

# basedir = os.path.abspath(os.path.dirname(__file__))

# app = Flask(__name__)
# #a secret key should be set as an environmental variable
# #through etc/environment on linux - other os's are available
# app.config['SECRET_KEY'] = 'thispassworldshouldbeanenvironmentvariable'
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['MAIL_SERVER']  = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# ## This need to be reset every time the virtual box is closed.
# ## MAIL_USERNAME, MAIL_PASSWORD, AND FLASK_ADMIN all need resetting.
# ## FLASK_ADMIN is where the email is going off to.
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# app.config['FLASK_ADMIN'] = os.environ.get('FLASK_ADMIN')
# app.config['FLASK_MAIL_SUBJECT_PREFIX'] = '[TF Flask - BOOP!]'
# app.config['FLASK_MAIL_SENDER'] = 'TF Flask App <tom@example.com>'


# manager = Manager(app)
# bootstrap = Bootstrap(app)
# moment = Moment(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# mail = Mail(app)

# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role', lazy='dynamic')

#     def __repr__(self):
#         return '<Role %r>' % self.name

# class User(db.Model):
#     __tableName__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

#     def __repr__(self):
#         return '<User %r>' % self.username

# def send_email(to, subject, template, **kwargs):
#     msg = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,
#                   sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     thr = Thread(target=send_async_email, args=[app, msg])
#     thr.start()
#     return thr

# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)

# class NameForm(FlaskForm):
#     name = StringField('What is your name?', validators=[Required()])
#     submit = SubmitField('Submit')

# def make_shell_context():
#     return dict(app=app, db=db, User=User, Role=Role)
# manager.add_command('shell', Shell(make_context=make_shell_context))
# manager.add_command('db', MigrateCommand)


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html'), 500

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             session['known'] = False
#             if app.config['FLASK_ADMIN']:
#                 send_email(app.config['FLASK_ADMIN'], 'New User', 'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         form.name.data = ''
#         return redirect(url_for('index'))
#     return render_template('index.html', current_time=datetime.utcnow(),
#                            form=form, name=session.get('name'), known=session.get('known', False))

# @app.route('/user/<name>')
# def user(name):
#     return render_template('user.html', name=name, current_time=datetime.utcnow())

# @app.route('/redirect')
# def the_redirect_function():
#     '''Redirect example'''
#     return redirect('http://maps.warwickshire.gov.uk/ias')

# if __name__ == '__main__':
#     manager.run()
