import os

from app import create_app, db
from app.models import *
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app('development')
migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Post=Post, Role=Role, Course=Course,
                Problem=Problem)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
