import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db
from app.models import Role, User, Post

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start firefox
        try:
            cls.client = webdriver.Chrome('/usr/local/share/chromedriver')
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            #suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            #create the db and populate with some fake data
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            # add an admin user
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='tom@example.com',
                         username='tom', password='hello',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

            # give the server a second to ensure it is up
            time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            #stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            #destroy the db
            db.drop_all()
            db.session.remove()

            #remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')
        
    def tearDown(self):
        pass

    def test_admin_home_page(self):
        #navigate to homepage
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+anonymous user!',
                                  self.client.page_source))

        #navigate to the login page
        self.client.find_element_by_link_text('Login').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)
        
        #login
        self.client.find_element_by_name('email').\
            send_keys('tom@example.com')
        self.client.find_element_by_name('password').\
            send_keys('hello')
        self.client.find_element_by_name('submit').click()
        # should return main.index
        self.assertTrue(re.search('Hello,\s+tom', self.client.page_source))

        #navigate to the user's profile page
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>tom</h1>' in self.client.page_source)
                                  