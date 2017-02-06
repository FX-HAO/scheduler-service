import os

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    from app.models import *
    manager.run()
