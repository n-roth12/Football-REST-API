from api import app
from flask import Flask, request, jsonify
from api import db, ma
import json
from api.models import PlayerGameStats, Week, Year, Player
from api.models import PlayerGameStatsSchema, WeekSchema, YearSchema, PlayerSchema

player_game_stat_schema = PlayerGameStatsSchema()
player_game_stats_schema = PlayerGameStatsSchema(many=True)
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
year_schema = YearSchema()
years_schema = YearSchema(many=True)
week_schema = WeekSchema()
weeks_schema = WeekSchema(many=True)


# Route to return all players in the database
@app.route('/player', methods=['GET'])
def get_players():
	all_players = Player.query.all()
	result = players_schema.dump(all_players)
	return jsonify(result)

# Route to return the player with the given id
@app.route('/player/<id>', methods=['GET'])
def get_player(id):
	player = Player.query.get(id)
	return player_schema.jsonify(player)

@app.route('/stats/<name>/<year>/<week>', methods=['GET'])
def get_week(name, year, week):
	name = name.replace("_", " ")
	p1 = db.session.query(Player).filter(Player.name == name).first()
	y1 = db.session.query(Year).filter(Year.player_id == p1.id, Year.year_number == year).first()
	w1 = db.session.query(Week).filter(Week.year_id == y1.id).first()
	stats = db.session.query(PlayerGameStats).filter(PlayerGameStats.week_id == w1.id).first()
	result = player_game_stat_schema.dump(stats)
	return jsonify(result)

# Route to add a new player to the database
#@app.route('/player', methods=['POST'])
#def add_player():
#	name = request.json['name']
#
#	new_player = Player(name)
#	db.session.add(new_player)
#	db.session.commit()

#	return player_schema.jsonify(new_player)

#@app.route('/player/<id>', methods=['PUT'])
#def update_player(id):
#	player = Player.query.get(id)
#	name = request.json['name']
#
#	player.name = name
#
#	db.session.commit()
#	return player_schema.jsonify(player)

#@app.route('/player/<id>', methods=['DELETE'])
#def delete_player(id):
#	player = Player.query.get(id)
#	db.session.delete(player)
#	db.session.commit()
#
#	return player_schema.jsonify(player)




