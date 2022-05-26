from api.models import PlayerGameStats, Player, DSTGameStats, DST
from api.models import PlayerGameStatsSchema, PlayerSchema, TopPlayerSchema, UserSchema, DSTGameStatsSchema, DSTSchema, TopDSTSchema
from api import db, ma
import json
from collections import OrderedDict
import time
import point_services

def temp():
	players = db.session.query(PlayerGameStats).all()
	for player in players:
		player.fanduel_points = point_services.getOffenseFanduelPoints(PlayerGameStatsSchema().dump(player))
		player.draftkings_points = point_services.getOffenseDraftkingsPoints(PlayerGameStatsSchema().dump(player))
		db.session.commit()

if __name__ == "__main__":
	temp()