# tf 14/07/17
import unittest
import time
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='lolhello')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='lolhello')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='lolhello')
        self.assertTrue(u.verify_password('lolhello'))
        self.assertFalse(u.verify_password('timetosaygoodbye'))

    def test_password_salts_are_random(self):
        u = User(password='matching')
        u2 = User(password='matching')
        self.assertTrue(u.password_hash != u2.password_hash)
        
    def test_valid_confirmation_token(self):
        u = User(password='lolhello')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmaiton_token(self):
        u1 = User(password='lolhello')
        u2 = User(password="goodbye")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password="hello")
        db.session.add(u)
        db.session.commit()
        # remember expiration can be passed into token
        # make it expire before the sleep ends
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='hello')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'goodbye'))
        self.assertTrue(u.verify_password('goodbye'))

    def test_invalid_reset_token(self):
        """
        Have a first user generate a reset token, then check 
        if second can enter a new password on reset with first users token
        """
        u1 = User(password='one')
        u2 = User(password='two')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'notwo'))
        self.assertTrue(u2.verify_password('two'))

    def test_valid_email_change_token(self):
        u = User(email='tom@example.com', password='hello')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('keith@example.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'keith@example.com')
