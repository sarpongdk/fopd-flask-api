from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
#from flask_migrate import Migrate

from fopd.config import Config

# use same object with different apps
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
#migrate = Migrate()

def create_app(config_object = Config):
    app = Flask(__name__)
    app.config.from_object(config_object) # flask app configuration in config.py

    # initialize object
    db.init_app(app)
    #migrate.init_app(app, db)
    cors.init_app(app, resources={r"*": {"origins": "*"}})
    bcrypt.init_app(app)

    from fopd.students.routes import students
    from fopd.teachers.routes import teachers
    from fopd.experiments.routes import experiments
    from fopd.courses.routes import courses
    from fopd.assignments.routes import assignments
    from fopd.assignment_responses.routes import assignment_responses

    app.register_blueprint(students)
    app.register_blueprint(teachers)
    app.register_blueprint(experiments)
    app.register_blueprint(courses)
    app.register_blueprint(assignments)
    app.register_blueprint(assignment_responses)

    return app

