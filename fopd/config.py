import os, dotenv, uuid

basedir = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(basedir, '.env')

print('Path to `.env` file:', ENV_PATH)

dotenv.load_dotenv(verbose = True, dotenv_path = ENV_PATH)

class Config:
    DEBUG = os.getenv('DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', str(uuid.uuid1()))
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://localhost/flasktestdb2')