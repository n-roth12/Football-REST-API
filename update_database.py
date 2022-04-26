from api.models import PlayerGameStats, Player, DSTGameStats, DST
from api import db, ma
import json
from collections import OrderedDict
import time
import os

"""
This script is responsible for constructing the database for use of the API
using the json files output by scrape_stats.py. All 4 json files must be present
in the directory in order for the database to be properly constructed.
"""

def build() -> None:
	positions = ['QB', 'RB', 'WR', 'TE', 'DST']
	for position in positions:
		try:
			f = open(f'{position}_update_data.json')
		except FileNotFoundError:
			print(f'Error: {position}_data file not found in directory. Please run scrape_stats.py to generate file.')
		else:
			data = json.load(f, object_pairs_hook=OrderedDict)
			print(f'Adding {position}s to database...')
			years = data.keys()
			for year in years:
				weeks = data[year].keys()
				for week in weeks:
					year = int(year)
					week = int(week.split('_')[1])
					if position != 'DST':
						for name in data[str(year)]["week_" + str(week)]:

							player_object = db.session.query(Player).filter(Player.name == name, Player.position == position).first()
							if player_object == None:
								new_player = Player(name=name, position=position)
								player_object = new_player
								db.session.add(player_object)
								db.session.commit()

							stat_data = data[str(year)]["week_" + str(week)][name]
							new_stats = PlayerGameStats(
								week=week,
								year=year,
								team=stat_data['team'], 
								game=stat_data['game'],
								passing_attempts=stat_data['pass_atts'], 
								passing_completions=stat_data['pass_cmps'],
								passing_yards=stat_data['pass_yds'],
								passing_touchdowns=stat_data['pass_tds'],
								passing_interceptions=stat_data['pass_ints'],
								passing_2point_conversions=stat_data['pass_2pts'],
								rushing_attempts=stat_data['rush_atts'],
								rushing_yards=stat_data['rush_yds'],
								rushing_touchdowns=stat_data['rush_tds'],
								rushing_2point_conversions=stat_data['rush_2pts'],
								receptions=stat_data['recs'],
								recieving_yards=stat_data['rec_yds'],
								recieving_touchdowns=stat_data['rec_tds'],
								recieving_2point_conversions=stat_data['rec_2pts'],
								fumbles_lost=stat_data['fumbles_lost'],
								fantasy_points=( (0.04 * stat_data['pass_yds']) + (4 * stat_data['pass_tds']) + (-2 * stat_data['pass_ints'])  + (2 * stat_data['pass_2pts']) + (0.1 * stat_data['rush_yds']) + (6 * stat_data['rush_tds']) + (2 * stat_data['rush_2pts']) + (stat_data['recs']) + (0.1 * stat_data['rec_yds']) + (6 * stat_data['rec_tds']) + (2 * stat_data['rec_2pts']) + (-2 * stat_data['fumbles_lost'])))
							new_stats.player = player_object

							db.session.add(new_stats)
							db.session.commit()

					else:
						for name in data[str(year)][f'week_{week}']:

							team_object = db.session.query(DST).filter(DST.name == name).first()
							if not team_object:
								new_team = DST(team=name)
								team_object = new_team
								db.session.add(team_object)
								db.session.commit()

							stat_data =  data[str(year)]["week_" + str(week)][name]
							new_stats = DSTGameStats(
								dst_id = team_object.id,
								year = year,
								week = week,
								game = stat_data['game'],
								fantasy_points = stat_data['points'],
								sacks = stat_data['sacks'],
								interceptions = stat_data['interceptions'],
								safeties = stat_data['safeties'],
								fumble_recoveries = stat_data['fumble_recoveries'],
								blocks = stat_data['blocks'],
								touchdowns = stat_data['touchdowns'],
								points_against = stat_data['points_against'],
								passing_yards_against = stat_data['passing_yards_against'],
								rushing_yards_against = stat_data['rushing_yards_against']						
							)

							db.session.add(new_stats)
							db.session.commit()

			print(f'Completed adding {position}s to database.')
			f.close()
			os.remove(f'{position}_update_data.json')

if __name__ == '__main__':
	start = time.perf_counter()
	print('Building database from json files...')
	build()
	finish = time.perf_counter()
	print(f'Finished building database in {round(finish - start, 2)} second(s).')



