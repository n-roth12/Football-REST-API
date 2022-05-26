from api import app
from flask import Flask, request, jsonify, render_template, make_response, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.sql import func
from sqlalchemy import desc
from api import db, ma
import json
from api.models import PlayerGameStats, Player, User, DSTGameStats, DST
from api.models import PlayerGameStatsSchema, PlayerSchema, TopPlayerSchema, UserSchema, DSTGameStatsSchema, DSTSchema, TopDSTSchema
from api.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
from functools import wraps
import requests
import redis 
import random


# These are the stat categories used in the PlayerGameStats model 
STAT_CATEGORIES = ['passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns',
			'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost', 'fantasy_points']

# These are the four positions of Players in the database
POSITIONS = ['QB', 'RB', 'WR','TE']
YEARS = range(2012, 2021)
QUERY_MAP = {'players': 
				['pos', 'limit'], 
			'stats':
				['name', 'year', 'week'], 
			'top':
				['year', 'week', 'pos', 'limit'], 
			'performances':
				['year', 'pos', 'limit']
			}

# limiter = Limiter(app, key_func=get_remote_address, 
# 	default_limits=["100000000/day;100000000/hour;100000/minute"])


# def token_required(f):
# 	@wraps(f)
# 	def decorated(*args, **kwargs):
# 		""" Decorator for handling required x-access-tokens.

# 		Decoded token is used to find and return User in database. 
# 		"""
# 		token = None
# 		if 'x-access-token' in request.headers:
# 			token = request.headers['x-access-token']

# 		if not token:
# 			return jsonify({'Error' : 'Token is missing.'}), 401

# 		try:
# 			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
# 			current_user = db.session.query(User).filter(User.public_id == data['public_id']).first()
# 		except:
# 			return jsonify({'Error' : 'Token is invalid.'}), 401

# 		return f(current_user, *args, **kwargs)

# 	return decorated

def convertName(name: str):
	names = name.split("_")
	names = [name.capitalize() for name in names]
	return ' '.join(names)

##### Routes associated with fetching player data #####

# Route to retrieve PlayerGameStats database entry by id
@app.route('/api/playergamestats/<id>', methods=['GET'])
def get_playergamestats(id: int):

	playergamestat = db.session.query(PlayerGameStats).filter(PlayerGameStats.id == id).first()
	if playergamestat:
		return jsonify(PlayerGameStatsSchema().dump(playergamestat))

	return jsonify({ 'Error': 'No PlayerGameStat with the specified id!' })


@app.route('/api/dstgamestats/<id>', methods=['GET'])
def get_dstgamestats(id: int):
	
	dstgamestat = db.session.query(DSTGameStats).filter(DSTGameStats.id == id).first()
	if dstgamestat:
		return jsonify(DSTGameStatsSchema().dump(dstgamestat))

	return jsonify({ 'Error': 'No DSTGameStat with the specified id!' })


@app.route('/api/playergamestats', methods=['POST'])
def get_lineup_playergamestats():
	"""
		Route for fetching the stats and player info for an entire lineup given the
		ids of the playergamestats/dstgamestats of the player.
	"""
	lineup_data = request.data
	data = json.loads(lineup_data.decode('utf-8'))
	if not data:
		return jsonify({ 'Error': 'No PlayerGameStats requested!' })

	result = {}
	for key, value in data.items():
		if not (value == {} or key == 'points' or key == 'user_id' or key == 'week' 
			or key == 'year' or key == 'id' or key == 'dst'):
			player_data = db.session.query(PlayerGameStats, Player) \
				.filter(PlayerGameStats.id == value,
					Player.id == PlayerGameStats.player_id) \
				.first()

			if player_data:
				result[key] = TopPlayerSchema().dump(
					{ 
						'name': player_data[1].name, 
						'position': player_data[1].position, 
						'stats': player_data[0] 
					}
				)

	dst_data = db.session.query(DSTGameStats, DST) \
					.filter(DSTGameStats.id == value,
						DST.id == DSTGameStats.id) \
					.first()

	if dst_data:
		result['dst'] == TopDSTSchema().dump(
			{
				'name': dst_data[1].team,
				'stats': dst_data[0]
			}
		)

	return jsonify(result)


@app.route('/api/players', defaults={'id': None}, methods=['GET'])
@app.route('/api/players/<id>', methods=['GET'])
def get_players(id: str):
	""" 
		Route for retrieving players. A single player can be retrieved by 
		specifying an id, or multiple players can be return by filtering by 
		position. A limit to the number of returned players can also be 
		specified.
	"""
	if id:
		player = db.session.query(Player).filter(Player.id == id).first()
		if not player:
			return jsonify({ 'Error': 'No player with specified id.' })
			
		return jsonify(PlayerSchema().dump(player)), 200

	pos = request.args.get('pos')
	limit = request.args.get('limit')
	players = db.session.query(Player)

	if pos:
		if pos.upper() not in POSITIONS:
			return jsonify({ 'Error': 'Specified position is invalid.' })

		players = players.filter(Player.position == pos.upper())

	if limit:
		players = players.limit(int(limit))

	return jsonify(PlayerSchema(many=True).dump(players.all())), 200


@app.route('/api/stats', methods=['GET'])
def get_week():
	""" Function to return the stats of Players via the /stats api endpoint.

	Stats can be filtered by Player name, year, and week. If week is not specified,
	the yearly stats are returned for the Player. If the year is not specified, the 
	career stats are returned for the Player.

	User must provide valid x-access-token to access this endpoint.
	"""
	name = request.args.get('name')
	year = request.args.get('year')
	week = request.args.get('week')

	if not name:
		return jsonify({ 'Error': 'Player name must be specified.' })

	if week and not year:
		return jsonify({ 'Error': 'Year must be specified if week is specified.' })

	name = convertName(name)
	player = db.session.query(Player).filter(Player.name == name).first()
	if not player:
		return jsonify({ 'Error': 'Player not found in database.' })

	if year:
		if week:
			week_stats = db.session.query(PlayerGameStats) \
				.filter(PlayerGameStats.week == week,
					PlayerGameStats.year == year,
					PlayerGameStats.player_id == player.id).first()

			if not week_stats:
				return ({ 'Error': 'No data found for this player for the specified week.' }), 404

			result = {}
			result['name'] = player.name
			result['stats'] = PlayerGameStatsSchema().dump(week_stats)
			return jsonify(result)

		year_stats = db.session.query(PlayerGameStats) \
			.filter(PlayerGameStats.player_id == player.id, 
				PlayerGameStats.year == year).all()

		if not year_stats:
			return jsonify({ 'Error': 'No data found for this player for specified year.' }), 404

		season_stats = {}
		# Summing the weekly stats for each week of the specified year for each 
		# stat category
		for game_stats in year_stats:

			for stat_category in STAT_CATEGORIES:
				if stat_category in season_stats:
					season_stats[stat_category] += getattr(game_stats, stat_category)
				else:
					season_stats[stat_category] = getattr(game_stats, stat_category)

		result = TopPlayerSchema().dump(
			{
				'position': player.position,
				'name': player.name,
				'stats': season_stats
			}
		)

		return jsonify(result), 200

	else:
		career_stats = db.session.query(PlayerGameStats) \
			.filter(PlayerGameStats.player_id == player.id).all()

		career_totals = {}
		for game_stats in career_stats:
			for stat_category in STAT_CATEGORIES:
				if stat_category in career_totals:
					career_totals[stat_category] += getattr(game_stats, stat_category)
				else:
					career_totals[stat_category] = getattr(game_stats, stat_category)

		result = TopPlayerSchema().dump(
			{
				'position': player.position,
				'name': player.name,
				'stats': career_totals
			}
		)

		return jsonify(result), 200


@app.route('/api/top', methods=['GET'])
def get_pos_top():
	""" Function to return the top weekly performances via the /top api endpoint.

		Performances can be filtered by year, week, and position. If week is not specified,
		the yearly stats of Players will be returned. Results are ordered by fantasy points
		scored. 

		User must provide valid x-access-token to access this endpoint.
	"""
	year = request.args.get('year')
	week = request.args.get('week')
	pos = request.args.get('pos')
	limit = request.args.get('limit')

	if week and not year:
		return jsonify({ 'Error': 'Year must be specified if week is specified.' })

	if year:
		if week:
			# Get dst stats seperately
			if pos and pos == 'dst':
				top_defenses = db.session.query(DSTGameStats, DST) \
					.filter(DSTGameStats.week == week,
							DSTGameStats.year == year,
							DST.id == DSTGameStats.dst_id) \
					.order_by(DSTGameStats.points_against.desc()) \
					.limit(int(limit) if limit else None) \
					.all()

				if top_defenses:
					result = []
					for i in range(len(top_defenses)):
						result.append(TopDSTSchema().dump(
							{
								'rank': i + 1,
								'team': top_defenses[i][1].team,
								'city': top_defenses[i][1].city,
								'name': top_defenses[i][1].name,
								'position': 'DST',
								'stats': top_defenses[i][0]
							}
						))
					return jsonify(result)
				else:
					return jsonify({ 'Error': 'No results for the specified week and year.' }), 404

			# Query to get the weekly stats of all players for the specified week and year
			top_players = db.session \
				.query(PlayerGameStats, Player) \
				.filter(
					PlayerGameStats.week == week,
					PlayerGameStats.year == year,
					Player.id == PlayerGameStats.player_id,
					Player.position == pos.upper() if pos else True) \
				.order_by(
					PlayerGameStats.fantasy_points.desc()) \
				.limit(int(limit) if limit else None) \
				.all()

			if top_players:
				result = []
				for i in range(len(top_players)):
					result.append(TopPlayerSchema().dump(
						{ 
							'rank': i + 1, 
							'name': top_players[i][1].name, 
							'position': top_players[i][1].position, 
							'stats': top_players[i][0] 
						}
					))
				return jsonify(result), 200

			else:
				return jsonify({ 'Error': 'No results for specified week and year.' }), 404

		else:
			# Query to sum the weekly stats for all players across the specified year
			top_players = db.session \
				.query(
					Player,
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
					func.sum(PlayerGameStats.fantasy_points)) \
				.filter(
					PlayerGameStats.year == year,
					PlayerGameStats.player_id == Player.id) \
				.group_by(Player.id) \
				.order_by(desc(func.sum(PlayerGameStats.fantasy_points)))

			if pos:
				top_players = top_players \
					.filter(Player.position == pos.upper()) \
					.limit(int(limit) if limit else None) \
					.all()
			else:
				top_players = top_players \
					.limit(int(limit) if limit else None) \
					.all()

			if not len(top_players):
				return jsonify({ 'Error': 'No data for the year requested.' }), 404

			result = []
			for i in range(len(top_players)):
				# Feeding the results of the query back into a PlayerGameStats object
				game_stats = PlayerGameStats(
					None,
					None,
					None,
					None,
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

				result.append(TopPlayerSchema().dump(
					{ 'rank': i + 1, 
					'name': top_players[i][0].name, 
					'position': top_players[i][0].position,
					'stats': game_stats }
				))
			return jsonify(result), 200
	else:
		return jsonify({ 'Error': 'Year must be specified.' })



@app.route('/api/performances', methods=['GET'])
def get_top_performances():
	""" Function to return the top perfomances for a given year via the 
		/top_performances api endpoint.

		A perfomance is defined as the weekly stats of a player, and top performances
		are ordered by fantasy points scored for the week, so the function returns
		the weekly stats of all players for a year ordered by fantasy points scored.

		User must provide valid x-access-token to access this endpoint.
	"""
	year = request.args.get('year')
	limit = request.args.get('limit')
	pos = request.args.get('pos')

	if year:
		# Query to get the weekly top_performances ordered by fantasy points scored
		top_players = db.session.query(Player, PlayerGameStats) \
			.filter(
				PlayerGameStats.year == year,
				PlayerGameStats.player_id == Player.id)
	else:
		top_players = db.session.query(Player, PlayerGameStats) \
			.filter(
				PlayerGameStats.player_id == Player.id)
	
	if pos:
		if pos.upper() not in POSITIONS:
			return jsonify({ 'Error': 'Specified position is invalid.' })

		top_players = top_players.filter(Player.position == pos.upper())

	top_players = top_players \
		.order_by(desc(PlayerGameStats.fantasy_points)) \
		.limit(int(limit) if limit else 100) \
		.all()

	if len(top_players):
		result = []
		for i in range(len(top_players)):
			result.append(TopPlayerSchema().dump(
				{ 'rank': i + 1, 
				'position': top_players[i][0].position,
				'name': top_players[i][0].name, 
				'stats': top_players[i][1] }
			))
		return jsonify(result), 200

	else:
		return jsonify({'Error': 'No data for the year requested.'}), 404


@app.route('/api/teamstats', methods=['GET'])
def get_team_stats():
	"""
		Route for retrieving all player stats for a team for a
		specific week. If no week is specified, returns the stats
		of all the players grouped by team.
	"""
	team = request.args.get('team')
	year = request.args.get('year')
	week = request.args.get('week')

	if not year or not week:
		return jsonify({ 'Error': 'Must specify week and year.' }), 400

	if team:
		team_result = []
		players = db.session.query(PlayerGameStats, Player) \
			.filter(PlayerGameStats.year == year,
					PlayerGameStats.week == week,
					PlayerGameStats.player_id == Player.id,
					PlayerGameStats.team == team) \
			.all()
		for player in players:
			team_result.append({
							'name': player[1].name,
							'position': player[1].position,
							'stats': PlayerGameStatsSchema().dump(player[0])
						})
		return jsonify({team: team_result}), 200
	else:
		result = {}
		teams = [result.team for result in db.session.query(PlayerGameStats.team).distinct()]
		for team in teams:
			team_result = []
			players = db.session.query(PlayerGameStats, Player) \
				.filter(PlayerGameStats.year == year,
						PlayerGameStats.week == week,
						PlayerGameStats.player_id == Player.id,
						PlayerGameStats.team == team) \
				.all()
			for player in players:
				team_result.append({
					'name': player[1].name,
					'position': player[1].position,
					'stats': PlayerGameStatsSchema().dump(player[0])
				})
			result[team] = team_result
		return jsonify(result), 200


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
	""" Function return the home page html template, including loading and
		handling register and login form submission. 

		If user submits login form successfully, they are provided their 
		x-access-token via a flash message. If user submits the register form 
		successfully, a new user with their credentials is created in the database
		and they are provided their x-access token via a flash message. 
	"""
	register_form = RegisterForm()
	login_form = LoginForm()
	query_result = None
	request_string = None

	if request.method == 'GET':
		if request.args and request.args.get('form-name') == 'request-form':
			endpoint = request.args.get('endpoint')
			if not endpoint or endpoint not in ['players', 'stats', 'top', 'performances']:
				flash(f'Invalid endpoint used for request. Please try a different endpoint.', category='danger')
			query_string = request.args.get('query-string')
			request_string = f'{app.config["BASE_URL"]}/api/{endpoint}?{query_string}'
			result = requests.get(request_string)
			query_result = result.json()


	if request.method == 'POST':
		if request.form['form-name'] == 'register-form':
			if register_form.validate_on_submit():

				hashed_password = generate_password_hash(register_form.password1.data, 
					method='sha256')

				new_user = User(public_id=str(uuid.uuid4()), 
					username=register_form.username.data, 
					password=hashed_password, admin=False)

				db.session.add(new_user)
				db.session.commit()

				token = jwt.encode({'public_id' : new_user.public_id}, 
					app.config['SECRET_KEY'], 
					algorithm='HS256')

				flash(f'You have been successfully registered! Your access token is:\n{token}.')

			elif register_form.errors != {}:
				for err_msg in register_form.errors.values():
					flash(f'There was an error with registering: {err_msg}', category='danger')

		if request.form['form-name'] == 'login-form':
			if login_form.validate_on_submit():
				user = db.session.query(User).filter(
					User.username == login_form.username.data).first()

				if user and check_password_hash(user.password, login_form.password.data):
					token = jwt.encode({'public_id' : user.public_id}, 
						app.config['SECRET_KEY'], algorithm='HS256')

					flash(f'You have been successfully logged in! Your access token is:\n{token}.', 
						category='success')

				else:
					flash('Unable to log in: incorrect username or password.', 
						category='danger')

			elif login_form.errors != {}:
				for err_msg in login_form.errors.values():
					flash(f'There was an error with logging in: {err_msg}', 
						category='danger')

	category = list(QUERY_MAP.keys())[random.randint(0, len(QUERY_MAP.keys()) - 1)]
	query = QUERY_MAP[category][random.randint(0, len(QUERY_MAP[category]) - 1)]

	return render_template('index.html', 
		register_form=register_form, login_form=login_form, 
		query_result=query_result, request_string=request_string)



# @app.route('/api/user', methods=['POST'])
# def create_user(current_user: User):
# 	""" Function to create a new User via the /user api endpoint.

# 		User must be an admin to successfully create a new User. The username and 
# 		password of the new User must be passed in the body of the request. Password
# 		is hashed and then stored. A public_id is randomly generated for the new User.
# 		If User creation is successful, the new User is added to the database.
# 		Returns only a message specifying if creation of new User was successful.
# 	"""
# 	if not current_user.admin:
# 		return jsonify({'Error' : 'Not authorized to perform that function.'})

# 	data = request.get_json()

# 	hashed_password = generate_password_hash(data['password'], method='sha256')

# 	new_user = User(public_id=str(uuid.uuid4()), username=data['name'], 
# 		password=hashed_password, admin=False)

# 	db.session.add(new_user)
# 	db.session.commit()

# 	return jsonify({'message': 'New user successfully created.'})


# @app.route('/api/promote_user/<public_id>', methods=['PUT'])
# @token_required
# def promote_user(current_user: User, public_id: str):
# 	""" Function to promote a User to admin via the /promote_user api endpoint.

# 		User must be an admin to successfully promote another User. User to promote 
# 		is specified by the Users publid_id. Function only returns a message specifying
# 		whether promotion was successful. 
# 	"""
# 	if not current_user.admin:
# 		return jsonify({'Error' : 'Not authorized to perform that function.'})

# 	user = db.session.query(User).filter(User.public_id == public_id).first()

# 	if not user:
# 		return jsonify({'Error' : 'User not found.'})

# 	user.admin = True
# 	db.session.commit()

# 	return jsonify({'Message' : 'User promoted to admin successfully.'})


# @app.route('/api/users', defaults={'public_id': None}, methods=['GET'])
# @app.route('/api/users/<public_id>', methods=['GET'])
# @token_required
# def get_users(current_user: User, public_id: str):
# 	""" Function to handle fetching the Users from the database via the /user
# 		api endpoint. 

# 		User must be an admin to successfully retrieve Users. If User is admin,
# 		the function returns the list of Users in the database.
# 	"""
# 	if not current_user.admin:
# 		return jsonify({'Error' : 'Not authorized to perform that function.'})

# 	if public_id:
# 		user = db.session.query(User).filter(User.public_id == public_id).first()

# 		if not user:
# 			return jsonify({'message' : 'No user found.'})

# 		schema = UserSchema()
# 		return jsonify({'user' : schema.dump(
# 			user_data['public_id'], user_data['name'], user_data['admin']) })

# 	users = db.session.query(User).all()
# 	schema = UserSchema(many=True)

# 	return jsonify({ 'users': schema.dump(users) })


# @app.route('/api/user/<public_id>', methods=['DELETE'])
# @token_required
# def delete_user(current_user: User, public_id: str):
# 	""" Function to handle the deletion of a user via the /user api endpoint.

# 		User must be an admin in order to successfully delete a user from the 
# 		database. 
# 	"""
# 	if not current_user.admin:
# 		return jsonify({'Error' : 'Not authorized to perform that function.'})

# 	user = db.session.query(User).filter(User.public_id == public_id).first()

# 	if not user:
# 		return jsonify({'message' : 'No user found.'})

# 	db.session.delete(user)
# 	db.session.commit()

# 	return jsonify({'message' : 'The user has been deleted.'})

# @app.route('/api/login')
# def login():
# 	""" Function to handle the logging in of a user via the /login api endpoint.

# 		User must pass their username and password as parameters of HTTP Basic Auth
# 		in their request to login. If login is successful, function returns the 
# 		user's x-access-token.
# 	"""
# 	auth = request.authorization

# 	if not auth or not auth.username or not auth.password:
# 		return make_response('Could not verify', 401, 
# 			{'WWW-Authenticate' : 'Basic realm-"Login required!"'})

# 	user = db.session.query(User).filter(User.username == auth.username).first()

# 	if not user:
# 		return make_response('Could not verify', 401, 
# 			{'WWW-Authenticate' : 'Basic realm-"Login required!"'})

# 	if check_password_hash(user.password, auth.password):
# 		token = jwt.encode({'public_id' : user.public_id}, 
# 			app.config['SECRET_KEY'], algorithm='HS256')

# 		return jsonify({'token' : token})

# 	return make_response('Could not verify', 401, 
# 		{'WWW-Authenticate' : 'Basic realm-"Login required!"'})




