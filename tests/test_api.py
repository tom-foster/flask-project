import json
import re
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

    def get_api_headers(self, email_or_token, password):
        """
        Helper method that includes headers that will be needed will all
        requests.
        """
        return {
            'Authorization': 'Basic ' + b64encode(
                (email_or_token + ':' + password).encode('utf-8')).decode('utf-8'),
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

    def test_token_auth(self):
        """
        1. Attempt to login with a bad token.
        2. Then generate a token
        3. Then check to see if the token works.
        """
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='tom@example.com', password='hello', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # try a bad token
        ## remember a token leaves the password blank.
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # use the token to get posts
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_anonymous(self):
        """Make sure you can still get posts even if anon"""
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('', ''))
        self.assertTrue(response.status_code == 200)

    def test_unconfirmed_account(self):
        """ add an unconfirmed user, and make sure page is forbidden."""
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='tom@example.com', password='hello', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # get posts trying to with unconfirmed credentials
        response = self.client.get(
            url_for('api.get_posts'),
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 403)

    def test_posts(self):
        """
        1. Write an empty post, and expect 400
        2. Write a post
        3. Get the new post
        4. Get the post from the user
        5. Get the post from the user as a follower - still use same person,
           since they are a follower.
        """
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='tom@example.com', password='hello', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        #write an empty post
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('tom@example.com', 'hello'),
            data=json.dumps({'body': ''}))
        self.assertTrue(response.status_code == 400)

        # write a post
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('tom@example.com', 'hello'),
            data=json.dumps({'body': 'a *TEST* blog post'}))
        self.assertTrue(response.status_code == 201)
        ## this url will be used further down too in this test.
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the newly written post
        response = self.client.get(
            url,
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'a *TEST* blog post')
        self.assertTrue(json_response['body_html'] ==
                        '<p>a <em>TEST</em> blog post</p>')
        json_post = json_response

        # get the post from the user as a follower
        response = self.client.get(
            url_for('api.get_user_followed_posts', id=u.id),
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertTrue(json_response.get('count', 0) == 1)
        self.assertTrue(json_response['posts'][0] == json_post)

        # edit post
        response = self.client.put(
            url,
            headers=self.get_api_headers('tom@example.com', 'hello'),
            data=json.dumps({'body': 'updated body post put test'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'updated body post put test')
        self.assertTrue(json_response['body_html'] ==
                        '<p>updated body post put test</p>')

    def test_users(self):
        """
        Add multiple users, test api.get_user"
        """
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='tom@example.com', username='tom', password='hello',
                  confirmed=True, role=r)
        u2 = User(email='keith@example.com', username='keith',
                  password='goodbye', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        #get those users
        response = self.client.get(
            url_for('api.get_user', id=u1.id),
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'tom')
        response = self.client.get(
            url_for('api.get_user', id=u2.id),
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['username'] == 'keith')

    def test_comments(self):
        """
        1. Write a comment
        2. Get the new comment
        3. Add a second comment
        4. Get both comments
        5. Get ALL comments
        """
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='tom@example.com', username='tom',
                  password='hello', confirmed=True, role=r)
        u2 = User(email='keith@example.com', username='keith',
                  password='goodbye', confirmed=True, role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # add a post
        post = Post(body='body of the post', author=u1)
        db.session.add(post)
        db.session.commit()

        # write a comment
        response = self.client.post(
            url_for('api.new_post_comment', id=post.id),
            headers=self.get_api_headers('keith@example.com', 'goodbye'),
            data=json.dumps(
                {'body': 'Not as good as [this post](http://example.com).'}))
        print(response.status_code)
        self.assertTrue(response.status_code == 201)
        json_response = json.loads(response.data.decode('utf-8'))
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertTrue(json_response['body'] ==
                        'Not as good as [this post](http://example.com).')
        self.assertTrue(
            re.sub('<.*?>', '', json_response['body_html']) ==
            'Not as good as this post.')

        # get the new comment
        response = self.client.get(
            url,
            headers=self.get_api_headers('tom@example.com', 'hello'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] ==
                        'Not as good as [this post](http://example.com).')
        
        # add another comment
        comment = Comment(body='I guess I\ll try harder', author=u1, post=post)
        db.session.add(comment)
        db.session.commit()

        # get the comments from the post
        response = self.client.get(
            url_for('api.get_post_comments', id=post.id),
            headers=self.get_api_headers('keith@example.com', 'goodbye'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertTrue(json_response.get('count', 0) == 2)
