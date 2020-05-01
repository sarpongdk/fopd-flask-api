from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from fopd import create_app, db

app = create_app()
app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

@manager.command
def run():
    app.run(debug = app.config['DEBUG'])

if __name__ == "__main__":
    manager.run()
    