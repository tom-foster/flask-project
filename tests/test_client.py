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
        