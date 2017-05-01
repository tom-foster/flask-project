from flask import Flask, request, make_response, redirect, abort, render_template
from flask_script import Manager
app = Flask(__name__)

manager = Manager(app)

@app.route('/')
def index():
    return render_template('../index.html')

@app.route('/user/<name>')
def user(name):
    '''Dynamic app route also note I've added a response code as a second argument'''
    return render_template('../user.html', name=name)

@app.route('/redirect')
def the_redirect_function():
    '''Redirect example'''
    return redirect('http://maps.warwickshire.gov.uk/ias')

if __name__ == '__main__':
    manager.run()