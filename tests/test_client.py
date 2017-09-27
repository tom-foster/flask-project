import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """
        Test if a user isn't logged in it returns the anonymous user greeting.
        """
        response = self.client.get(url_for('main.index'))
        ## as text converts from byte array to unicode string
        self.assertTrue('anonymous user' in response.get_data(as_text=True))

    def test_register_and_login(self):
        """
        Test if a user registers for a new account, tries to login with new acccount
        without confirming, then confirms account, then logouts.
        """
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email' : 'tom@example.com',
            'username': 'userTom',
            'password': 'hello',
            'password2': 'hello'
        })
        self.assertTrue(response.status_code == 302)

        # login with the new account and get greeted with not confirmed"
        response = self.client.post(url_for('auth.login'), data={
            'email' : 'tom@example.com',
            'password' : 'hello',
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('Hello,\s+userTom', data))
        self.assertTrue('You have not confirmed your account yet.' in data)

        # send a confirmation token
        user = User.query.filter_by(email='tom@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You have confirmed your account. Thanks!' in data)

        #log out
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You have now been signed out.' in data)
