from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

ENV = 'dev'
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if ENV == 'dev':
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
else:
	app.debug = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Models
class PlayerGameStats(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	game = db.Column(db.String(10))
	passing_attempts = db.Column(db.Integer())
	passing_completions = db.Column(db.Integer())
	passing_yards = db.Column(db.Integer())
	passing_touchdowns = db.Column(db.Integer())
	passing_interceptions = db.Column(db.Integer())
	passing_2point_conversions = db.Column(db.Integer())
	rushing_attempts = db.Column(db.Integer())
	rushing_yards = db.Column(db.Integer())
	rushing_touchdowns = db.Column(db.Integer())
	rushing_2point_conversions = db.Column(db.Integer())
	receptions = db.Column(db.Integer())
	recieving_yards = db.Column(db.Integer())
	recieving_touchdowns = db.Column(db.Integer())
	recieving_2point_conversions = db.Column(db.Integer())
	fumbles_lost = db.Column(db.Integer())

class Week(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	week_number = db.Column(db.Integer())
	#player_game_stats = db.List however you do this

class Year(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	year_number = db.Column(db.Integer())
	#weeks = db.List however you do this

if __name__ == '__main__':
	app.run()