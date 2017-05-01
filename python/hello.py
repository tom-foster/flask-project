from flask import Flask, request, make_response, redirect, abort
from flask_script import Manager
app = Flask(__name__)

manager = Manager(app)

@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    user_agent = request.headers.get('User-Agent')
    return response

@app.route('/user/<name>')
def user(name):
    '''Dynamic app route also note I've added a response code as a second argument'''
    return "<h1>Hello, %s!</h1>" % name, 400

@app.route('/redirect')
def the_redirect_function():
    '''Redirect example'''
    return redirect('http://maps.warwickshire.gov.uk/ias')

if __name__ == '__main__':
    manager.run()