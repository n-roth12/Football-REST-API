from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import config

app = Flask(__name__)

app = Flask(__name__, static_folder=os.path.abspath('Users/NolanRoth/Desktop/FFBRestApi'))
app.config['SECRET_KEY'] = config.app_secret_key
DEV_ENV = True

if DEV_ENV:
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = config.dev_database_uri
else:
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

from api import routes
