from api import db, ma
from datetime import datetime


class Update(db.Model):
	__tablename__ = 'update'
	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.DateTime, server_default=str(datetime.now()))
	week = db.Column(db.Integer)
	year = db.Column(db.Integer)


class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(50), unique=True)
	username = db.Column(db.String(50))
	password = db.Column(db.String(256))
	admin = db.Column(db.Boolean)


class UserSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('public_id', 'username', 'admin')


class PlayerGameStats(db.Model):
	__tablename__ = 'player_game_stats'
	id = db.Column(db.Integer, primary_key=True)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
	week = db.Column(db.Integer())
	year = db.Column(db.Integer())
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

	def __init__(self, week: int, year: int, team: str, game: str, passing_attempts: int, passing_completions: int, passing_yards: int,
		passing_touchdowns: int, passing_interceptions: int,
		passing_2point_conversions: int, rushing_attempts: int, rushing_yards: int, rushing_touchdowns: int,
		rushing_2point_conversions: int, receptions: int, recieving_yards: int, recieving_touchdowns: int,
		recieving_2point_conversions: int, fumbles_lost: int, fantasy_points: float) -> None:

		self.week = week
		self.year = year
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


class PlayerGameStatsSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('id', 'week', 'year', 'team', 'game', 'passing_attempts', 'passing_completions',
			'passing_yards', 'passing_touchdowns', 'passing_interceptions', 'passing_2point_conversions',
			'rushing_attempts', 'rushing_yards', 'rushing_touchdowns', 'rushing_2point_conversions',
			'receptions', 'recieving_yards', 'recieving_touchdowns', 'recieving_2point_conversions', 
			'fumbles_lost', 'fantasy_points', 'player_id')


class Player(db.Model):
	__tablename__ = 'player'
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(100))
	position = db.Column(db.String(3))
	games = db.relationship('PlayerGameStats', backref='player')

	def __init__(self, name: str, position: str) -> None:
		self.name = name
		self.position = position


class PlayerSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('id', 'name', 'position')


class TopPlayerSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('rank', 'name', 'position', 'stats')

	stats = ma.Nested(PlayerGameStatsSchema)


class DST(db.Model):
	__tablename__ = 'dst'

	id = db.Column(db.Integer, primary_key=True)
	team = db.Column(db.String(5))
	name = db.Column(db.String(30))
	city = db.Column(db.String(50))


class DSTGameStats(db.Model):
	__tablename__ = 'dst_game_stats'
	id = db.Column(db.Integer, primary_key=True)
	dst_id = db.Column(db.Integer, db.ForeignKey('dst.id'))
	dst = db.relationship('DST', foreign_keys=[dst_id])
	year = db.Column(db.Integer)
	week = db.Column(db.Integer)
	game = db.Column(db.String(10))
	sacks = db.Column(db.Float)
	interceptions = db.Column(db.Integer)
	safeties = db.Column(db.Integer)
	fumble_recoveries = db.Column(db.Integer)
	blocks = db.Column(db.Integer)
	touchdowns = db.Column(db.Integer)
	points_against = db.Column(db.Integer)
	passing_yards_against = db.Column(db.Integer)
	rushing_yards_against = db.Column(db.Integer)

class DSTGameStatsSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('id', 'dst_id', 'year', 'week', 'game', 'sacks', 'interceptions', 'safeties', 'blocks', 'touchdowns', 
			'points_against', 'passing_yards_against', 'rushing_yards_against', 'fumble_recoveries')


class DSTSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('id', 'team', 'name', 'city')


class TopDSTSchema(ma.SQLAlchemySchema):
	class Meta:
		fields = ('rank', 'team', 'name', 'city', 'position', 'stats')

	stats = ma.Nested(DSTGameStatsSchema)







