import os
COV = None
if os.environ.get('FLASK_CONFIG'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db


app = create_app(os.getenv('FLASK_ENV') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_CONFIG'):
        import sys
        os.environ['FLASK_CONFIG'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()

@manager.command
def coverage():
    if not os.environ.get('FLASK_CONFIG'):
        import sys
        os.environ['FLASK_CONFIG'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()

if __name__ == '__main__':
    from app.models import *
    manager.run()
