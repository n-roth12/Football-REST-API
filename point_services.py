
fanduel_scoring = {
	"offense": {
		"rushing_yards": 0.1,
		"rushing_touchdowns": 6,
		"passing_yards": 0.04,
		"passing_touchdowns": 4,
		"passing_interceptions": -1,
		"recieving_yards": 0.1,
		"recieving_touchdowns": 6,
		"receptions": 0.5,
		"return_touchdowns": 6,
		"fumbles_lost": -2,
		"fumble_recovery_touchdown": 6,
		"rushing_2point_conversions": 2,
		"recieving_2point_conversions": 2,
		"passing_2point_conversions": 2,
		"field_goal_0_39": 3,
		"field_goal_40_49": 4,
		"field_goal_50_": 5,
		"extra_point": 1
	}, 
	"defense": {
		"sacks": 1,
		"fumble_recoveries": 2,
		"touchdowns": 6,
		"return_touchdowns": 6,
		"extra_point_return": 2,
		"safeties": 2,
		"blocks": 2,
		"interceptions": 2,
		"points_allowed_0": 10,
		"points_allowed_1_6": 7,
		"points_allowed_7_13": 4,
		"points_allowed_14_20": 1,
		"points_allowed_21_27": 0,
		"points_allowed_28_34": -1,
		"points_allowed_35_": -4
	}
}

draftkings_scoring = {
	"offense": {
		"passing_touchdowns": 4,
		"passing_yards": 0.04,
		"passing_yards_300_": 3,
		"passing_interceptions": -1,
		"rushing_touchdowns": 6,
		"rushing_yards": 0.01,
		"rushing_yards_100_": 3,
		"recieving_touchdowns": 6,
		"recieving_yards": 0.1,
		"recieving_yards_100_": 3,
		"receptions": 1,
		"return_touchdowns": 6,
		"fumbles_lost": -1,
		"passing_2point_conversions": 2,
		"rushing_2point_conversions": 2,
		"recieving_2point_conversions": 2,
		"fumble_recovery_touchdown": 6 
	},
	"defense": {
		"sacks": 1,
		"interceptions": 2,
		"fumble_recoveries": 2,
		"return_touchdowns": 6,
		"fumble_recovery_touchdown": 6,
		"safeties": 2,
		"blocks": 2,
		"extra_point_return": 2,
		"points_allowed_0": 10,
		"points_allowed_1_6": 7,
		"points_allowed_7_13": 4,
		"points_allowed_14_20": 1,
		"points_allowed_21_27": 0,
		"points_allowed_28_34": -1,
		"points_allowed_35_": -4
	}
}

def getOffenseFanduelPoints(stats):
	points = 0
	for key, value in fanduel_scoring["offense"].items():
		points += stats.get(key, default=0) * value

	return round(points, 2)

def getDefenseFanduelPoints(stats):
	points = 0
	for key, value in fanduel_scoring["defense"].items():
		points += stats.get(key, default=0) * value

	points_allowed = stats["points_allowed"]
	if points_allowed < 1:
		points += fanduel_scoring["defense"]["points_allowed_0"]
	elif points_allowed < 7:
		points += fanduel_scoring["defense"]["points_allowed_1_6"]
	elif points_allowed < 14:
		points += fanduel_scoring["defense"]["points_allowed_7_13"]
	elif points_allowed < 21:
		points += fanduel_scoring["defense"]["points_allowed_14_20"]
	elif points_allowed < 28:
		points += fanduel_scoring["defense"]["points_allowed_21_27"]
	elif points_allowed < 35:
		points += fanduel_scoring["defense"]["points_allowed_28_34"]
	else:
		points += fanduel_scoring["defense"]["points_allowed_35_"]

	return round(points, 2)

def getOffenseDraftkingsPoints(stats):
	points = 0
	for key, value in draftkings_scoring["offense"].items():
		points += stats.get(key, default=0) * value

	return round(points, 2)

def getDefenseDraftkingsPoints(stats):
	points = 0
	for key, value in draftkings_scoring["defense"].items():
		points += stats.get(key, default=0) * value

	points_allowed = stats["points_allowed"]
	if points_allowed < 1:
		points += draftkings_scoring["defense"]["points_allowed_0"]
	elif points_allowed < 7:
		points += draftkings_scoring["defense"]["points_allowed_1_6"]
	elif points_allowed < 14:
		points += draftkings_scoring["defense"]["points_allowed_7_13"]
	elif points_allowed < 21:
		points += draftkings_scoring["defense"]["points_allowed_14_20"]
	elif points_allowed < 28:
		points += draftkings_scoring["defense"]["points_allowed_21_27"]
	elif points_allowed < 35:
		points += draftkings_scoring["defense"]["points_allowed_28_34"]
	else:
		points += draftkings_scoring["defense"]["points_allowed_35_"]

	return round(points, 2)






