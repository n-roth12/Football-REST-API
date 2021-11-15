from api import app
from flask import Flask, request, jsonify, render_template, make_response, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.sql import func
from sqlalchemy import desc
from api import db, ma
import json
from api.models import PlayerGameStats, Week, Year, Player, User
from api.models import PlayerGameStatsSchema, WeekSchema, YearSchema, PlayerSchema, TopPlayerSchema
from api.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import uuid
from functools import wraps
import requests

# These are the stat categories used in the PlayerGameStats model 
stat_categories = ['passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns',
			'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost', 'fantasy_points']

# These are the four positions of Players in the database
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

limiter = Limiter(app, key_func=get_remote_address, default_limits=["1000/day;100/hour;10/minute"])

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		""" Decorator for handling required x-access-tokens.

		Decoded token is used to find and return User in database. 
		"""
		token = None
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'Error' : 'Token is missing.'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
			current_user = db.session.query(User).filter(User.public_id == data['public_id']).first()
		except:
			return jsonify({'Error' : 'Token is invalid.'}), 401

		return f(current_user, *args, **kwargs)

	return decorated

def convertName(name):
	names = name.split("_")
	names = [name.capitalize() for name in names]
	return ' '.join(names)


##### Routes associated with fetching player data #####

@app.route('/api/players', defaults={'id': None}, methods=['GET'])
@app.route('/api/players/<id>', methods=['GET'])
@token_required
def get_players(current_user, id: str) -> list[dict]:
	""" Funciton to return the list of Players via the /players api endpoint.

	Passing an id will return the player with the corresponding id.

	Players can be filtered by position. If position is not specified, all players
	in the database will be returned. Only Player name, id, position are returned.

	User must provide a valid x-access-token to access this endpoint.
	"""
	if id:
		player = db.session.query(Player).filter(Player.id == id).first()
		return jsonify(player_schema.dump(player)), 200
	
	position = request.args.get('pos').upper()
	if position:
		players = db.session.query(Player).filter(Player.position == position).all()
	else:
		players = db.session.query(Player).all()
	return jsonify(players_schema.dump(players)), 200


@app.route('/api/stats', defaults={'id': None}, methods=['GET'])
@app.route('/api/stats/<id>', methods=['GET'])
@token_required
def get_week(current_user, id: str) -> dict:
	""" Function to return the stats of Players via the /stats api endpoint.

	Stats can be filtered by Player name, year, and week. If week is not specified,
	the yearly stats are returned for the Player. If the year is not specified, the 
	career stats are returned for the Player.

	User must provide valid x-access-token to access this endpoint.
	"""

	if id:
		stat = db.session.query(PlayerGameStats).filter(PlayerGameStats.id == id).first()
		return jsonify(player_game_stat_schema.dump(stat)), 200

	name = request.args.get('name')
	year = request.args.get('year')
	week = request.args.get('week')

	if week and not year:
		return jsonify({ "Error": "Year must be specified if week is specified." })

	if name:
		name = convertName(name)
		player = db.session.query(Player).filter(Player.name == name).first()
		if not player:
			return jsonify({ "Error": "Player not found in database." })

		if year:
			year_stats = db.session.query(Year).filter(
				Year.player_id == player.id, 
				Year.year_number == year).first()

			if not year_stats:
				return jsonify({ "Error": "No data found for this player for specified year." }), 404

			if week:
				week_stats = db.session.query(Week, PlayerGameStats).filter(
					Week.year_id == year_stats.id,
					Week.week_number == week,
					PlayerGameStats.week_id == Week.id).first()

				if not week_stats:
					return ({ "Error": "No data found for this player for the specified week." }), 404

				return jsonify(player_game_stat_schema.dump(week_stats[1])), 200

			else:
				weeks = db.session.query(Week).filter(Week.year_id == year_stats.id).all()
				season_stats = {}
				# Summing the weekly stats for each week of the specified year for each 
				# stat category
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

	else:
		stats = db.session.query(PlayerGameStats).all()
		return jsonify(player_game_stats_schema.dump(stats)), 200



@app.route('/api/top/<year>', defaults={'week': None, 'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>', defaults={'pos': None}, methods=['GET'])
@app.route('/api/top/<year>/<week>/<pos>', methods=['GET'])
@token_required
def get_pos_top(current_user: User, year: int, week: int, pos: str) -> list[dict]:
	""" Function to return the top weekly performances via the /top api endpoint.

	Performances can be filtered by year, week, and position. If week is not specified,
	the yearly stats of Players will be returned. Results are ordered by fantasy points
	scored. 

	User must provide valid x-access-token to access this endpoint.
	"""
	if week:
		# Query to get the weekly stats of all players for the specified week and year
		top_players = db.session.query(PlayerGameStats, Player, Week, Year).filter(
			PlayerGameStats.week_id == Week.id,
			Week.week_number == week,
			Week.year_id == Year.id,
			Year.year_number == year,
			Year.player_id == Player.id)

		if pos:
			# Query to filter top_players by position and order by fantasy points scored
			top_players = top_players.filter(Player.position == pos.upper()).order_by(
				PlayerGameStats.fantasy_points.desc()).all()
		else:
			top_players = top_players.order_by(PlayerGameStats.fantasy_points.desc()).all()

		if top_players:
			result = []
			for i in range(len(top_players)):
				result.append(top_player_schema.dump({"rank": i + 1, 
					"name": top_players[i][1].name, "stats": top_players[i][0]}))
			return jsonify(result), 200

		else:
			return jsonify({"Error": "Year or week requested is invalid."}), 404

	else:
		# Query to sum the weekly stats for all players across all years played
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

		result = []
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

			result.append(top_player_schema.dump({"rank": i + 1, 
				"name": top_players[i][0].name, "stats": game_stats}))

		return jsonify(result), 200


@app.route('/api/top_performances/<year>', methods=['GET'])
@token_required
def get_top_performances(current_user: User, year: int) -> list[dict]:
	""" Function to return the top perfomances for a given year via the 
	/top_performances api endpoint.

	A perfomance is defined as the weekly stats of a player, and top performances
	are ordered by fantasy points scored for the week, so the function returns
	the weekly stats of all players for a year ordered by fantasy points scored.

	User must provide valid x-access-token to access this endpoint.
	"""
	# Query to get the weekly top_performances ordered by fantasy points scored
	top_players = db.session.query(Player, PlayerGameStats, Week, Year).filter(
		PlayerGameStats.week_id == Week.id,
		Week.year_id == Year.id,
		Year.year_number == year,
		Year.player_id == Player.id).order_by(desc(PlayerGameStats.fantasy_points)).all()

	if len(top_players):
		result = []
		for i in range(len(top_players)):
			result.append(top_player_schema.dump({"rank": i + 1, 
				"name": top_players[i][0].name, "stats": top_players[i][1]}))
		return jsonify(result), 200

	else:
		return jsonify({"Error": "No data for the year requested."}), 404


@app.route('/api/user', methods=['POST'])
@token_required
def create_user(current_user: User) -> str:
	""" Function to create a new User via the /user api endpoint.

	User must be an admin to successfully create a new User. The username and 
	password of the new User must be passed in the body of the request. Password
	is hashed and then stored. A public_id is randomly generated for the new User.
	If User creation is successful, the new User is added to the database.
	Returns only a message specifying if creation of new User was successful.
	"""
	if not current_user.admin:
		return jsonify({'Error' : 'Not authorized to perform that function.'})

	data = request.get_json()

	hashed_password = generate_password_hash(data['password'], method='sha256')

	new_user = User(public_id=str(uuid.uuid4()), username=data['name'], 
		password=hashed_password, admin=False)

	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message': 'New user successfully created.'})


@app.route('/api/promote_user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user: User, public_id: str) -> str:
	""" Function to promote a User to admin via the /promote_user api endpoint.

	User must be an admin to successfully promote another User. User to promote 
	is specified by the Users publid_id. Function only returns a message specifying
	whether promotion was successful. 
	"""
	if not current_user.admin:
		return jsonify({'Error' : 'Not authorized to perform that function.'})

	user = db.session.query(User).filter(User.public_id == public_id).first()

	if not user:
		return jsonify({'Error' : 'User not found.'})

	user.admin = True
	db.session.commit()

	return jsonify({'Message' : 'User promoted to admin successfully.'})


@app.route('/api/user', defaults={'public_id': None}, methods=['GET'])
@app.route('/api/user/<public_id>', methods=['GET'])
@token_required
def get_users(current_user: User, public_id: str) -> str:
	""" Function to handle fetching the Users from the database via the /user
	api endpoint. 

	User must be an admin to successfully retrieve Users. If User is admin,
	the function returns the list of Users in the database.
	"""
	if not current_user.admin:
		return jsonify({'Error' : 'Not authorized to perform that function.'})

	if public_id:
		user = db.session.query(User).filter(User.public_id == public_id).first()

		if not user:
			return jsonify({'message' : 'No user found.'})

		user_data = {}
		user_data['public_id'] = user.public_id
		user_data['name'] = user.username
		user_data['password'] = user.password
		user_data['admin'] = user.admin

		return jsonify({'user' : user_data})

	users = db.session.query(User).all()
	result = []
	for user in users:
		user_data = {}
		user_data['public_id'] = user.public_id
		user_data['name'] = user.username
		user_data['password'] = user.password
		user_data['admin'] = user.admin
		result.append(user_data)

	return jsonify({'users' : result})


@app.route('/api/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user: User, public_id: str) -> str:
	""" Function to handle the deletion of a user via the /user api endpoint.

	User must be an admin in order to successfully delete a user from the 
	database. 
	"""
	if not current_user.admin:
		return jsonify({'Error' : 'Not authorized to perform that function.'})

	user = db.session.query(User).filter(User.public_id == public_id).first()

	if not user:
		return jsonify({'message' : 'No user found.'})

	db.session.delete(user)
	db.session.commit()

	return jsonify({'message' : 'The user has been deleted.'})

@app.route('/api/login')
def login() -> str:
	""" Function to handle the logging in of a user via the /login api endpoint.

	User must pass their username and password as parameters of HTTP Basic Auth
	in their request to login. If login is successful, function returns the 
	user's x-access-token.
	"""
	auth = request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify', 401, 
			{'WWW-Authenticate' : 'Basic realm-"Login required!"'})

	user = db.session.query(User).filter(User.username == auth.username).first()

	if not user:
		return make_response('Could not verify', 401, 
			{'WWW-Authenticate' : 'Basic realm-"Login required!"'})

	if check_password_hash(user.password, auth.password):
		token = jwt.encode({'public_id' : user.public_id}, 
			app.config['SECRET_KEY'], algorithm='HS256')

		return jsonify({'token' : token})

	return make_response('Could not verify', 401, 
		{'WWW-Authenticate' : 'Basic realm-"Login required!"'})


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@limiter.exempt
def home_page() -> None:
	""" Function return the home page html template, including loading and
	handling register and login form submission. 

	If user submits login form successfully, they are provided their 
	x-access-token via a flash message. If user submits the register form 
	successfully, a new user with their credentials is created in the database
	and they are provided their x-access token via a flash message. """

	register_form = RegisterForm()
	login_form = LoginForm()

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

	return render_template('index.html', 
		register_form=register_form, login_form=login_form)


@app.route('/api/sample/players', methods=['GET'])
def test_players() -> str:
	""" Function to return sample output of /players endpoint. 
	Returns the first 5 players in the database. """

	token = app.config['TEST_ACCESS_TOKEN']
	result = requests.get(f'{app.config["BASE_URL"]}/api/players', 
		headers={'x-access-token': token})

	return jsonify(result.json()[:5])


@app.route('/api/sample/stats/Dalvin_Cook/2020/2', methods=['GET'])
def test_stats() -> str:
	""" Function to return the sample output of /stats endpoint.
	Returns the stats for Dalvin Cook, week 2, 2020.
	"""
	token = app.config['TEST_ACCESS_TOKEN']
	result = requests.get(f'{app.config["BASE_URL"]}/api/stats/Dalvin_Cook/2020/2', 
		headers={'x-access-token': token})

	return jsonify(result.json())


@app.route('/api/sample/top/2020/8/te', methods=['GET'])
def test_top() -> str:
	""" Function to return the sample output of /top endpoint.
	Returns the top 5 tight ends for week 8, 2020.
	"""
	token = app.config['TEST_ACCESS_TOKEN']
	result = requests.get(f'{app.config["BASE_URL"]}/api/top/2020/8/te', 
		headers={'x-access-token': token})

	return jsonify(result.json()[:5])


@app.route('/api/sample/top_performances/2019', methods=['GET'])
def test_top_performances() -> str:
	""" Function to return the sample output of /top_performances endpoint.
	Returns the top 5 performances from 2019.
	"""
	token = app.config['TEST_ACCESS_TOKEN']
	result = requests.get(f'{app.config["BASE_URL"]}/api/top_performances/2019', 
		headers={'x-access-token':token})

	return jsonify(result.json()[:5])





