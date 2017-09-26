#!/usr/bin/env python
import os

## this is for the package coverage
## find a os set variable if it isn't set, set it in the test command
## which will stop the test and restart and the second run will support
## coverage from the start.
## this if statement together twith the coverage if statement in the test
## make up that action.
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    ## the options cover branch coverage, and we only want to include the app
    ## folder.
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, Comment=Comment)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
