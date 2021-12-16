from api import db, ma

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(50), unique=True)
	username = db.Column(db.String(50))
	password = db.Column(db.String(256))
	admin = db.Column(db.Boolean)

class UserSchema(ma.SQLAlchemySchema):
	class Meta:
		model = User

	public_id = ma.auto_field()
	username = ma.auto_field()
	admin = ma.auto_field()

# This class stores the data about the last time the database was updated
class MetaData(db.Model):
	id = db.Column(db.Integer, primary_key=True) 
	week_of_update = db.Column(db.Integer())
	year_of_update = db.Column(db.Integer())

# Each set of game stats belongs to a specific player
class PlayerGameStats(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	team = db.Column(db.String(4))
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
	fantasy_points = db.Column(db.Float())
	week_id = db.Column(db.Integer(), db.ForeignKey('week.id'))

	def __init__(self, team: str, game: str, passing_attempts: int, passing_completions: int, passing_yards: int,
		passing_touchdowns: int, passing_interceptions: int,
		passing_2point_conversions: int, rushing_attempts: int, rushing_yards: int, rushing_touchdowns: int,
		rushing_2point_conversions: int, receptions: int, recieving_yards: int, recieving_touchdowns: int,
		recieving_2point_conversions: int, fumbles_lost: int, fantasy_points: float) -> None:

		self.team = team
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
		self.fantasy_points = fantasy_points

# Player is the parent object
class Player(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100))
	position = db.Column(db.String(3))
	years = db.relationship('Year', backref='player')

	def __init__(self, name: str, position: str) -> None:
		self.name = name
		self.position = position

# Each Week is a child of a Year and has a single PlayerGameStats as a child
class Week(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	week_number = db.Column(db.Integer())
	player_game_stats = db.relationship('PlayerGameStats', backref='week')
	year_id = db.Column(db.Integer, db.ForeignKey('year.id'))

	def __init__(self, week_number: int) -> None:
		self.week_number = week_number

# Each Year is a child of a Player and has Weeks as children
class Year(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	year_number = db.Column(db.Integer())
	weeks = db.relationship('Week', backref='year')
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

	def __init__(self, year_number: int) -> None:
		self.year_number = year_number

class PlayerGameStatsSchema(ma.SQLAlchemySchema):
	class Meta:
		model = PlayerGameStats

	team = ma.auto_field()
	game = ma.auto_field()
	passing_attempts = ma.auto_field()
	passing_completions = ma.auto_field()
	passing_yards = ma.auto_field()
	passing_touchdowns = ma.auto_field()
	passing_interceptions = ma.auto_field()
	passing_2point_conversions = ma.auto_field()
	rushing_attempts = ma.auto_field()
	rushing_yards = ma.auto_field()
	rushing_touchdowns = ma.auto_field()
	rushing_2point_conversions = ma.auto_field()
	receptions = ma.auto_field()
	recieving_yards = ma.auto_field()
	recieving_touchdowns = ma.auto_field()
	recieving_2point_conversions = ma.auto_field()
	fumbles_lost = ma.auto_field()
	fantasy_points = ma.auto_field()

class PlayerSchema(ma.SQLAlchemySchema):
	class Meta:
		model = Player

	id = ma.auto_field()
	name = ma.auto_field()
	position = ma.auto_field()

class TopPlayerSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('rank', 'name', 'stats')

	stats = ma.Nested(PlayerGameStatsSchema)

class WeekSchema(ma.SQLAlchemySchema):
	class Meta:
		model = Week

	id = ma.auto_field()
	week_number = ma.auto_field()
	player_game_stats = ma.auto_field()

class YearSchema(ma.SQLAlchemySchema):
	class Meta:
		model = Year

	id = ma.auto_field()
	year_number = ma.auto_field()
	weeks = ma.auto_field()




