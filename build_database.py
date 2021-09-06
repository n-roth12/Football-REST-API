from api.models import PlayerGameStats, Player, Week, Year
from api import db, ma
import json
from collections import OrderedDict

def build():
	years = range(2012, 2021)
	weeks = range(1, 18)
	positions = ['QB', 'RB', 'WR', 'TE']

	f1 = open('QB_data.json')
	data = json.load(f1, object_pairs_hook=OrderedDict)

	for year in years:
		for week in weeks:
			for name in data[str(year)]["week_" + str(week)]:

				p1 = db.session.query(Player).filter(Player.name == name).first()
				if p1 == None:
					new_player = Player(name=name, position='QB')
					p1 = new_player
					db.session.add(p1)

				y1 = db.session.query(Year).filter(Year.year_number == year, Year.player == p1).first()
				if y1 == None:
					new_year = Year(year_number=year)
					new_year.player = p1
					y1 = new_year
					db.session.add(y1)

				new_week = Week(week_number=week)
				new_week.year = y1
				db.session.add(new_week)

				stat_data = data[str(year)]["week_" + str(week)][name]
				new_stats = PlayerGameStats(game=stat_data['game'],
					passing_attempts=stat_data['pass_atts'], 
					passing_completions = stat_data['pass_cmps'],
					passing_yards = stat_data['pass_yds'],
					passing_touchdowns = stat_data['pass_tds'],
					passing_interceptions = stat_data['pass_ints'],
					passing_2point_conversions = stat_data['pass_2pts'],
					rushing_attempts = stat_data['rush_atts'],
					rushing_yards = stat_data['rush_yds'],
					rushing_touchdowns = stat_data['rush_tds'],
					rushing_2point_conversions = stat_data['rush_2pts'],
					receptions = stat_data['recs'],
					recieving_yards = stat_data['rec_yds'],
					recieving_touchdowns = stat_data['rec_tds'],
					recieving_2point_conversions = stat_data['rec_2pts'],
					fumbles_lost = stat_data['fumbles_lost'])
				new_stats.week = new_week
				db.session.add(new_stats)

				db.session.commit()

if __name__ == '__main__':
	build()




