#switch to a larger file structure
#tf 04/07/17
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thispassworldshouldbeanenvironmentvariable'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASK_MAIL_SUBJECT_PREFIX = '[TF FLASK PROJECT - BOOP!]'
    FLASK_MAIL_SENDER = 'TF FLASK APP <tom@example.com>'
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')

    @staticmethod
    def init_app(app):
        pass



