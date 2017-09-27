import json
import unittest
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post, Comment

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        """
        Helper method that includes headers that will be needed will all
        requests.
        """
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'appliction/json',
            'Content-Type': 'application/json'
        }
