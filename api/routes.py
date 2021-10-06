from api import app
from flask import Flask, request, jsonify, render_template, make_response
from sqlalchemy.sql import func
from sqlalchemy import desc
from api import db, ma
import json
from api.models import PlayerGameStats, Week, Year, Player
from api.models import PlayerGameStatsSchema, WeekSchema, YearSchema, PlayerSchema, TopPlayerSchema
from werkzeug.security import generate_password_hash, check_password_hash

stat_categories = ['passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns',
			'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost', 'fantasy_points']
positions = ['QB', 'RB', 'WR','TE']

player_game_stat_schema = PlayerGameStatsSchema()
player_game_stats_schema = PlayerGameStatsSchema(many=True)
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
year_schema = YearSchema()
years_schema = YearSchema(many=True)
week_schema = WeekSchema()
weeks_schema = WeekSchema(many=True)
top_player_schema = TopPlayerSchema()

# Route to the index page
@app.route('/')
@app.route('/home')
def home_page():
	return render_template('index.html')

# Route to return players in the database
@app.route('/api/players', defaults={'pos': None}, methods=['GET'])
@app.route('/api/players/<pos>', methods=['GET'])
def get_players(pos: str) -> list[dict]:
	if not pos:
		players = db.session.query(Player).all()
	else:
		players = db.session.query(Player).filter(Player.position == pos.upper()).all()
	return jsonify(players_schema.dump(players)), 200

# Route to return the stats of a specific player from a specific week
@app.route('/api/stats/<name>', defaults={'year': None, 'week': None}, methods=['GET'])
@app.route('/api/stats/<name>/<year>', defaults={'week': None}, methods=['GET'])
@app.route('/api/stats/<name>/<year>/<week>', methods=['GET'])
def get_week(name: str, year: int, week: int) -> dict:
	names = name.split("_")
	name = ' '.join(names)
	player = db.session.query(Player).filter(Player.name == name).first()
	if not player:
		return jsonify({"Error": "Player not found in database."})
	if year:
		year_stats = db.session.query(Year).filter(Year.player_id == player.id, 
			Year.year_number == year).first()
		if not year_stats:
			return jsonify({"Error": "No data found for this player for specified year."}), 404
		if week:
			week_stats = db.session.query(Week, PlayerGameStats).filter(
				Week.year_id == year_stats.id,
				Week.week_number == week,
				PlayerGameStats.week_id == Week.id).first()
			if not week_stats:
				return ({"Error": "No data found for this player for the specified week."}), 404
			return jsonify(player_game_stat_schema.dump(week_stats[1])), 200
		else:
			weeks = db.session.query(Week).filter(Week.year_id == year_stats.id).all()
			season_stats = {}
			for week in weeks:
				game_stats = db.session.query(PlayerGameStats).filter(PlayerGameStats.week_id == week.id).first()
				for stat_category in stat_categories:
					if stat_category in season_stats:
						season_stats[stat_category] += getattr(game_stats, stat_category)
					else:
						season_stats[stat_category] = getattr(game_stats, stat_category)
			return jsonify(player_game_stat_schema.dump(season_stats)), 200
	else:
		# Query to sum the weekly stats for a player across all years played
		career_stats = db.session.query(Player, func.sum(PlayerGameStats.passing_attempts),
			func.sum(PlayerGameStats.passing_completions),
			func.sum(PlayerGameStats.passing_yards),
			func.sum(PlayerGameStats.passing_touchdowns),
			func.sum(PlayerGameStats.passing_interceptions),
			func.sum(PlayerGameStats.passing_2point_conversions),
			func.sum(PlayerGameStats.rushing_attempts),
			func.sum(PlayerGameStats.rushing_yards),
			func.sum(PlayerGameStats.rushing_touchdowns),
			func.sum(PlayerGameStats.rushing_2point_conversions),
			func.sum(PlayerGameStats.receptions),
			func.sum(PlayerGameStats.recieving_yards),
			func.sum(PlayerGameStats.recieving_touchdowns),
			func.sum(PlayerGameStats.recieving_2point_conversions),
			func.sum(PlayerGameStats.fumbles_lost),
			func.sum(PlayerGameStats.fantasy_points)).join(Week, Year).filter(
			PlayerGameStats.week_id == Week.id,
			Week.year_id == Year.id,
			Year.player_id == Player.id,
			Player.name == name).group_by(Player.id).first()
		# Feeding the results of the query back into PlayerGameStats object
		result = PlayerGameStats(None,
			career_stats[1],
			career_stats[2],
			career_stats[3],
			career_stats[4],
			career_stats[5],
			career_stats[6],
			career_stats[7],
			career_stats[8],
			career_stats[9],
			career_stats[10],
			career_stats[11],
			career_stats[12],
			career_stats[13],
			career_stats[14],
			career_stats[15],
			career_stats[16])
		return jsonify(player_game_stat_schema.dump(result)), 200

# Route to return the top fantasy performers of a specific position from a specific week
@app.route('/api/top/<year>', defaults={'week': None, 'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>', defaults={'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>/<pos>', methods=['GET'])
def get_pos_top(year: int, week: int, pos: str) -> list[dict]:
	if week:
		top_players = db.session.query(PlayerGameStats, Player, Week, Year).filter(
			PlayerGameStats.week_id == Week.id,
			Week.week_number == week,
			Week.year_id == Year.id,
			Year.year_number == year,
			Year.player_id == Player.id)
		if pos:
			top_players = top_players.filter(Player.position == pos.upper()).order_by(PlayerGameStats.fantasy_points.desc()).all()
		else:
			top_players = top_players.order_by(PlayerGameStats.fantasy_points.desc()).all()
		if top_players:
			result = []
			for i in range(len(top_players)):
				result.append(top_player_schema.dump({"rank": i + 1, "name": top_players[i][1].name, "stats": top_players[i][0]}))
			return jsonify(result), 200
		else:
			return jsonify({"Error": "Year or week requested is invalid."}), 404
	else:
		# Query to sum the weekly stats for all players across all years played
		# right now it actually finds the best performances of the year
		top_players = db.session.query(Player,
			func.sum(PlayerGameStats.passing_attempts),
			func.sum(PlayerGameStats.passing_completions),
			func.sum(PlayerGameStats.passing_yards),
			func.sum(PlayerGameStats.passing_touchdowns),
			func.sum(PlayerGameStats.passing_interceptions),
			func.sum(PlayerGameStats.passing_2point_conversions),
			func.sum(PlayerGameStats.rushing_attempts),
			func.sum(PlayerGameStats.rushing_yards),
			func.sum(PlayerGameStats.rushing_touchdowns),
			func.sum(PlayerGameStats.rushing_2point_conversions),
			func.sum(PlayerGameStats.receptions),
			func.sum(PlayerGameStats.recieving_yards),
			func.sum(PlayerGameStats.recieving_touchdowns),
			func.sum(PlayerGameStats.recieving_2point_conversions),
			func.sum(PlayerGameStats.fumbles_lost),
			func.sum(PlayerGameStats.fantasy_points)).join(Week, Year).filter(
			PlayerGameStats.week_id == Week.id,
			Week.year_id == Year.id,
			Year.year_number == year,
			Year.player_id == Player.id).group_by(Player.id).order_by(desc(func.sum(PlayerGameStats.fantasy_points))).all()
		if not len(top_players):
			return jsonify({"Error": "No data for the year requested."}), 404
		result= []
		for i in range(len(top_players)):
			# Feeding the results of the query back into a PlayerGameStats object
			game_stats = PlayerGameStats(None,
				top_players[i][1],
				top_players[i][2],
				top_players[i][3],
				top_players[i][4],
				top_players[i][5],
				top_players[i][6],
				top_players[i][7],
				top_players[i][8],
				top_players[i][9],
				top_players[i][10],
				top_players[i][11],
				top_players[i][12],
				top_players[i][13],
				top_players[i][14],
				top_players[i][15],
				top_players[i][16])
			result.append(top_player_schema.dump({"rank": i + 1, "name": top_players[i][0].name, "stats": game_stats}))
		return jsonify(result), 200

@app.route('/api/top_performances/<year>', methods=['GET'])
def get_top_performances(year: int) -> list[dict]:
	top_players = db.session.query(Player, PlayerGameStats, Week, Year).filter(
		PlayerGameStats.week_id == Week.id,
		Week.year_id == Year.id,
		Year.year_number == year,
		Year.player_id == Player.id).order_by(desc(PlayerGameStats.fantasy_points)).all()
	if len(top_players):
		result = []
		for i in range(len(top_players)):
			result.append(top_player_schema.dump({"rank": i + 1, "name": top_players[i][0].name, "stats": top_players[i][1]}))
		return jsonify(result), 200
	else:
		return jsonify({"Error": "No data for the year requested."}), 404











