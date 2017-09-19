# tf 14/07/17
import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission, Follow

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

    def test_invalid_email_change_token(self):
        u1 = User(email='tom@example.com', password='hello')
        u2 = User(email='bob@example.com', password='zoo')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('keith@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'bob@example.com')

    def test_duplicate_email_change_token(self):
        """
        A test to ensure you can't have two of the same email.
        """
        u1 = User(email='tom@example.com', password='hello')
        u2 = User(email='bob@example.com', password='zoo')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('tom@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'bob@example.com')

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='tom@example.com', password='hello')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        
    def test_timestamps(self):
        """
            Tests to make sure that the timestamps have updated correctly.
        """
        u = User(password='hello')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        """
            Ensure that the ping function part of the user model is working.
        """
        u = User(password='hello')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='tom@example.com', password='hello')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = u.gravatar()
        self.assertTrue('http://www.gravatar.com/avatar/' +
                        'e4f7cd8905e896b04425b1d08411e9fb' in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'e4f7cd8905e896b04425b1d08411e9fb' in gravatar_ssl)
    
    def test_follows(self):
        u1 = User(email='tom@example.com', password='hello')
        u2 = User(email='keith@example.com', password='goodbye')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        ## first assumptions no one is following anyone yet
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        ## second assumptions u1 is now following u2
        ## but u2 is not following u1, and that u2 is followed by u1
        ##  and the counts are correct for followed and followers
        ## of u1 and u2
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        ## third assumption, u1's last followed, is u2
        ## and that the date stamp is accurate with the commit of the follow
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        ## fourth assumption, u2's last follower was u1
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        ## fifth set of assumptions that once u1 unfollows u2,
        ## the counts are all 0, including no rows in the association table
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        ## final assumptions - if u2 follows u1, but then deletes account
        ## no relationship should exist in the association table
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
