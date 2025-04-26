from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from config import Config

api = Flask(__name__)
api.config.from_object(Config)
db = SQLAlchemy(api)
# Flask-SQLAlchemy must be initialized before Flask-Marshmallow.
# ma = Marshmallow(api)
migrate = Migrate(api, db)

# import api routes from routes.py, must be after api creation to avoid cyclic dependencies
from api import tasks, tokens, users