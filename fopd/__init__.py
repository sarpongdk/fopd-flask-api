from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/flasktestdb2'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from fopd import routes