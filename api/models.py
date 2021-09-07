from api import db, ma

class lastUpdate(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	last_year = db.Column(db.Integer())
	last_week = db.Column(db.Integer())

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
	week_id = db.Column(db.Integer(), db.ForeignKey('week.id'))

	def __init__(self, game, passing_attempts, passing_completions, passing_yards,
		passing_touchdowns, passing_interceptions,
		passing_2point_conversions, rushing_attempts, rushing_yards, rushing_touchdowns,
		rushing_2point_conversions, receptions, recieving_yards, recieving_touchdowns,
		recieving_2point_conversions, fumbles_lost):

		self.game = game
		self.passing_attempts = passing_attempts
		self.passing_completions = passing_completions
		self.passing_yards = passing_yards
		self.passing_touchdowns = passing_touchdowns
		self.passing_interceptions = passing_interceptions
		self.passing_2point_conversions = passing_2point_conversions
		self.rushing_attempts = rushing_attempts
		self.rushing_yards = rushing_yards
		self.rushing_touchdowns = rushing_touchdowns
		self.rushing_2point_conversions = rushing_2point_conversions
		self.receptions = receptions
		self.recieving_yards = recieving_yards
		self.recieving_touchdowns = recieving_touchdowns
		self.recieving_2point_conversions = recieving_2point_conversions
		self.fumbles_lost = fumbles_lost

# Player is the parent object
class Player(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100))
	position = db.Column(db.String(3))
	years = db.relationship('Year', backref='player')

	def __init__(self, name, position):
		self.name = name
		self.position = position

# Each Week is a child of a Year and has a single PlayerGameStats as a child
class Week(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	week_number = db.Column(db.Integer())
	player_game_stats = db.relationship('PlayerGameStats', backref='week')
	year_id = db.Column(db.Integer, db.ForeignKey('year.id'))

	def __init__(self, week_number):
		self.week_number = week_number

# Each Year is a child of a Player and has Weeks as children
class Year(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	year_number = db.Column(db.Integer())
	weeks = db.relationship('Week', backref='year')
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

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

class PlayerYearStatsSchema(ma.Schema):
	class Meta:
		fields = ('passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns', 'passing_yards',
			'passing_touchdowns', 'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 
			'rushing_2point_conversions', 'receptions', 'recieving_yards',
			'recieving_touchdowns', 'recieving_2point_conversions', 'fumbles_lost')

class PlayerSchema(ma.Schema):
	class Meta:
		fields = ('id', 'name', 'position', 'year')

class WeekSchema(ma.Schema):
	class Meta:
		fields = ('id', 'week_number', 'players')

class YearSchema(ma.Schema):
	class Meta:
		fields = ('id', 'year_number', 'weeks')
