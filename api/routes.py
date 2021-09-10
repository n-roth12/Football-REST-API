from api import app
from flask import Flask, request, jsonify
from api import db, ma
import json
from api.models import PlayerGameStats, Week, Year, Player
from api.models import PlayerGameStatsSchema, WeekSchema, YearSchema, PlayerSchema, PlayerYearStatsSchema, TopPlayerSchema

stat_categories = ['passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns', 'passing_yards',
			'passing_touchdowns', 'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost', 'fantasy_points']
positions = ['QB', 'RB', 'WR','TE']

player_game_stat_schema = PlayerGameStatsSchema()
player_game_stats_schema = PlayerGameStatsSchema(many=True)
player_year_stats_schema = PlayerYearStatsSchema()
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
year_schema = YearSchema()
years_schema = YearSchema(many=True)
week_schema = WeekSchema()
weeks_schema = WeekSchema(many=True)
top_player_schema = TopPlayerSchema()

# Route to return all players in the database
@app.route('/players', methods=['GET'])
def get_players():
	all_players = Player.query.all()
	result = players_schema.dump(all_players)
	return jsonify(result)

# Route to return the stats of a specific player from a specific week
@app.route('/stats/<name>/<year>/<week>', methods=['GET'])
def get_week(name, year, week):
	name = name.replace("_", " ")
	p1 = db.session.query(Player).filter(Player.name == name).first()
	if p1:
		y1 = db.session.query(Year).filter(Year.player_id == p1.id, Year.year_number == year).first()
		if y1:
			w1 = db.session.query(Week).filter(Week.year_id == y1.id, Week.week_number == week).first()
			if w1:
				stats = db.session.query(PlayerGameStats).filter(PlayerGameStats.week_id == w1.id).first()
				result = player_game_stat_schema.dump(stats)
				return jsonify(result), 200
			else:
				return jsonify({"Error": "No data found for this player during specified week."}), 404
		else:
			return jsonify({"Error": "No data found for this player during the specified season."}), 404
	else:
		return jsonify({"Error": "Player not found in database."}), 404

# Route to return the season total stats of a specific player from a specific year
@app.route('/stats/<name>/<year>', methods=['GET'])
def get_year(name, year):
	name = name.replace("_", " ")
	p1 = db.session.query(Player).filter(Player.name == name).first()
	if p1:
		y1 = db.session.query(Year).filter(Year.player_id == p1.id, Year.year_number == year).first()
		if y1:
			weeks = db.session.query(Week).filter(Week.year_id == y1.id).all()
			season_stats = {}
			for week in weeks:
				week_stats = db.session.query(PlayerGameStats).filter(PlayerGameStats.week_id == week.id).first()
				for stat_category in stat_categories:
					if stat_category in season_stats:
						season_stats[stat_category] += getattr(week_stats, stat_category)
					else:
						season_stats[stat_category] = getattr(week_stats, stat_category)
			result = player_year_stats_schema.dump(season_stats)
			return jsonify(result), 200
		else:
			return jsonify({"Error": "No data found for this player during specified season."}), 404
	else:
		return jsonify({"Error": "Player not found in database."}), 404


# Route to return the top fantasy performers from a specific week
@app.route('/top/<year>/<week>', methods=['GET'])
def get_top(year, week):
	top1 = db.session.query(PlayerGameStats, Player, Week, Year).filter(
		PlayerGameStats.week_id == Week.id,
		Week.week_number == week,
		Week.year_id == Year.id,
		Year.year_number == year,
		Year.player_id == Player.id).order_by(PlayerGameStats.fantasy_points.desc()).all()
	if top1:
		#print(top1[0][0].fantasy_points)
		#print(top1[0][1].name)
		result = top_player_schema.dump({"name": top1[0][1].name, "fantasy_points": top1[0][0].fantasy_points})
		return jsonify(result), 200
	else:
		return jsonify({"Error": "Year or week requested is invalid."}), 404












