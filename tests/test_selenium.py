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
            cls.client = webdriver.Firefox()
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
            time.sleep(1)

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
        self.assertTrue(re.search('Hello,\s+annonymous user!',
                                  self.client.page_source))