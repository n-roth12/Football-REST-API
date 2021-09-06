from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# configurations
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

# MODELS

# Each set of game stats belongs to a specific player
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
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

	#def __init__(self, game, passing_attempts, passing_completions, passing_yards,
	#	passing_touchdowns, passing_interceptions, passing_interceptions,
	#	passing_2point_conversions, rushing_attempts, rushing_yards, rushing_touchdowns,
	#	rushing_2point_conversions, receptions, recieving_yards, recieving_touchdowns,
	#	recieving_2point_conversions, fumbles_lost):

	#	self.game = game
	#	self.passing_attempts = passing_attempts
	#	self.passing_completions = passing_completions
	#	self.passing_yards = passing_yards
	#	self.passing_touchdowns = passing_touchdowns
	#	self.passing_interceptions = passing_interceptions
	#	self.passing_2point_conversions = passing_2point_conversions
	#	self.rushing_attempts = rushing_attempts
	#	self.rushing_yards = rushing_yards
	#	self.rushing_touchdowns = rushing_touchdowns
	#	self.rushing_2point_conversions = rushing_2point_conversions
	#	self.receptions = receptions
	#	self.recieving_yards = recieving_yards
	#	self.recieving_touchdowns = recieving_touchdowns
	#	self.recieving_2point_conversions = recieving_2point_conversions
	#	self.fumbles_lost = fumbles_lost

# Each player belongs to a specific week
class Player(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100))
	stats = db.relationship('PlayerGameStats', backref='player')
	week_id = db.Column(db.Integer(), db.ForeignKey('week.id'))

	def __init__(self, name):
		self.name = name

# Each week belongs to a specific year
class Week(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	week_number = db.Column(db.Integer())
	players = db.relationship('Player', backref='week')
	year_id = db.Column(db.Integer, db.ForeignKey('year.id'))

	def __init__(self, week_number):
		self.week_number = week_number

class Year(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	year_number = db.Column(db.Integer())
	weeks = db.relationship('Week', backref='year')

	def __init__(self, year_number):
		self.year_number = year_number

class PlayerGameStatsSchema(ma.Schema):
	class Meta:
		fields = ('id', 'game', 'passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns', 'passing_yards',
			'passing_touchdowns', 'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost')

class PlayerSchema(ma.Schema):
	class Meta:
		fields = ('id', 'name', 'stats')

class WeekSchema(ma.Schema):
	class Meta:
		fields = ('id', 'week_number', 'players')

class YearSchema(ma.Schema):
	class Meta:
		fields = ('id', 'year_number', 'weeks')

player_game_stat_schema = PlayerGameStatsSchema()
player_game_stats_schema = PlayerGameStatsSchema(many=True)
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
year_schema = YearSchema()
years_schema = YearSchema(many=True)
week_schema = WeekSchema()
weeks_schema = WeekSchema(many=True)

# Route to add a new player to the database
@app.route('/player', methods=['POST'])
def add_player():
	name = request.json['name']

	new_player = Player(name)
	db.session.add(new_player)
	db.session.commit()

	return player_schema.jsonify(new_player)

# Route to return all players in the database
@app.route('/player', methods=['GET'])
def get_players():
	all_players = Player.query.all()
	result = players_schema.dump(all_players)
	return jsonify(result)

@app.route('/player/<id>', methods=['GET'])
def get_player(id):
	player = Player.query.get(id)
	return player_schema.jsonify(player)

@app.route('/player/<id>', methods=['PUT'])
def update_player(id):
	player = Player.query.get(id)
	name = request.json['name']

	player.name = name

	db.session.commit()
	return player_schema.jsonify(player)

@app.route('/player/<id>', methods=['DELETE'])
def delete_player(id):
	player = Player.query.get(id)
	db.session.delete(player)
	db.session.commit()

	return player_schema.jsonify(player)

if __name__ == '__main__':
	app.run()



