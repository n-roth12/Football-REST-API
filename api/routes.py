from api import app
from flask import Flask, request, jsonify, render_template
from sqlalchemy.sql import func
from sqlalchemy import desc
from api import db, ma
import json
from api.models import PlayerGameStats, Week, Year, Player
from api.models import PlayerGameStatsSchema, WeekSchema, YearSchema, PlayerSchema, PlayerYearStatsSchema, TopPlayerSchema

stat_categories = ['passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns',
			'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost', 'fantasy_points']
positions = ['QB', 'RB', 'WR','TE']

player_game_stat_schema = PlayerGameStatsSchema()
player_game_stats_schema = PlayerGameStatsSchema(many=True)
player_year_stats_schema = PlayerYearStatsSchema()
players_year_stats_schema = PlayerYearStatsSchema(many=True)
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

# Route to return all players in the database
@app.route('/api/players', methods=['GET'])
def get_players():
	all_players = db.session.query(Player).all()
	result = players_schema.dump(all_players)
	return jsonify(result)

# Route to return all players of a specific position
@app.route('/api/players/<pos>', methods=['GET'])
def get_pos_players(pos):
	pos_players = db.session.query(Player).filter(Player.position == pos).all()
	result = players_schema.dump(pos_players)
	return jsonify(result)

# Route to return the stats of a specific player from a specific week
@app.route('/api/stats/<name>/<year>', defaults={'week': None}, methods=['GET'])
@app.route('/api/stats/<name>/<year>/<week>', methods=['GET'])
def get_week(name, year, week):
	names = name.split("_")
	name = ' '.join(names)
	p1 = db.session.query(Player).filter(Player.name == name).first()
	if p1:
		y1 = db.session.query(Year).filter(Year.player_id == p1.id, Year.year_number == year).first()
		if y1:

			if week:
				w1 = db.session.query(Week).filter(Week.year_id == y1.id, Week.week_number == week).first()
				if w1:
					stats = db.session.query(PlayerGameStats).filter(PlayerGameStats.week_id == w1.id).first()
					result = player_game_stat_schema.dump(stats)
				else:
					return jsonify({"Error": "No data found for this player during specified week."}), 404

			else:
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
			return jsonify({"Error": "No data found for this player during the specified season."}), 404
	else:
		return jsonify({"Error": "Player not found in database."}), 404

# Route to return the top fantasy performers of a specific position from a specific week
@app.route('/api/top/<year>', defaults={'week': None, 'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>', defaults={'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>/<pos>', methods=['GET'])
def get_pos_top(year, week, pos):
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
		top_players = db.session.query(Player, Week, Year, func.sum(PlayerGameStats.passing_attempts),
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
			func.sum(PlayerGameStats.fantasy_points)).filter(
			PlayerGameStats.week_id == Week.id,
			Week.year_id == Year.id,
			Year.year_number == year,
			Year.player_id == Player.id).group_by(Player.id).order_by(desc(func.sum(PlayerGameStats.fantasy_points))).all()
		if not len(top_players):
			return jsonify({"Error": "No data for the year requested."})
		result= []
		for i in range(len(top_players)):
			game_stats = PlayerGameStats(top_players[i][3],
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
				top_players[i][16],
				top_players[i][17],
				top_players[i][18])
			result.append(top_player_schema.dump({"rank": i + 1, "name": top_players[i][0].name, "stats": game_stats}))
		return jsonify(result), 200








