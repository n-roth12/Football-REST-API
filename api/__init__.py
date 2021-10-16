from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import config

app = Flask(__name__, static_folder=os.path.abspath('/Users/NolanRoth/Desktop/FFBRestApi'))

#try:
#	import config
#except ModuleNotFoundError:
app.debug = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('PROD_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['TEST_ACCESS_TOKEN'] = os.environ.get('TEST_ACCESS_TOKEN')	
#else:
#	app.debug = True
#	app.config['SQLALCHEMY_DATABASE_URI'] = config.dev_database_uri
#	app.config['SECRET_KEY'] = config.app_secret_key
#	app.config['TEST_ACCESS_TOKEN'] = config.test_access_token

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

from api import routes
