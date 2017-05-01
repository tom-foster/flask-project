from flask import Flask, request, make_response
app = Flask(__name__)

@app.route('/')
def index():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    user_agent = request.headers.get('User-Agent')
    return response

@app.route('/user/<name>')
def user(name):
    '''Dynamic app route'''
    return "<h1>Hello, %s!</h1>" % name

if __name__ == '__main__':
    app.run(debug=True)