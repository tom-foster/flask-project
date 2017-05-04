from datetime import datetime
from flask import Flask, request, make_response, redirect, abort, render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
#a secret key should be set as an environmental variable
#through etc/environment on linux - other os's are available
app.config['SECRET_KEY'] = 'thispassworldshouldbeanenvironmentvariable'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('index.html', current_time=datetime.utcnow(),
                           form=form, name=name)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/redirect')
def the_redirect_function():
    '''Redirect example'''
    return redirect('http://maps.warwickshire.gov.uk/ias')

if __name__ == '__main__':
    manager.run()
