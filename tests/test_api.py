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
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertTrue(response.status_code == 404)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['error'] == 'not found')

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 200)
    
    def test_bad_auth(self):
        """ check if a user can log in with incorrect details"""
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='tom@example.com', password='hello', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # try with a bad password
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('tom@example.com', 'goodbye'))
        self.assertTrue(response.status_code == 401)

