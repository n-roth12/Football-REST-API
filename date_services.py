import datetime

# Dictionary to store the start and end dates of each NFL regular season
# from 2012 to 2022
week_dict = {
	2012: {
		'start': {
			'day': 5,
			'month': 9
		},
		'stop': {
			'day': 30,
			'month': 12
		}
	},
	2013: {
		'start': {
			'day': 5,
			'month': 9
		},
		'stop': {
			'day': 29,
			'month': 12
		}
	},
	2014: {
		'start': {
			'day': 4,
			'month': 9
		},
		'stop': {
			'day': 28,
			'month': 12
		}
	},
	2015: {
		'start': {
			'day': 10,
			'month': 9
		},
		'stop': {
			'day': 3,
			'month': 1
		}
	},
	2016: {
		'start': {
			'day': 8,
			'month': 9
		},
		'stop': {
			'day': 1,
			'month': 1,
		}
	},
	2017: {
		'start': {
			'day': 7,
			'month': 9
		},
		'stop': {
			'day': 31,
			'month': 12
		}
	},
	2018: {
		'start': {
			'day': 6,
			'month': 9
		},
		'stop': {
			'day': 30,
			'month': 12
		}
	},
	2019: {
		'start': {
			'day': 5,
			'month': 9
		},
		'stop': {
			'day': 29,
			'month': 12
		}
	},
	2020: {
		'start': {
			'day': 10,
			'month': 9
		},
		'stop': {
			'day': 3,
			'month': 1
		}
	},
	2021: {
		'start': {
			'day': 8,
			'month': 9
		},
		'stop': {
			'day': 9,
			'month': 1
		}
	},
	2022: {
		'start': {
			'day': 8,
			'month': 9
		},
		'stop': {
			'day': 9,
			'month': 1
		}
	}
}

def findWeek(lineup_date):
	"""
	Returns the year and week of the NFL schedule given a date
	Returns (None, None) if the date is not part of the NFL
	regular season
	"""
	if lineup_date.year < 2012 or lineup_date.year > 2022:
		return None, None

	year = lineup_date.year
	month = lineup_date.month
	day = lineup_date.day

	year_adjusted = year - 1 if month < 3 else year

	start = week_dict[year_adjusted]['start']
	stop = week_dict[year_adjusted]['stop']
	start_date = datetime.date(year_adjusted, start['month'], start['day'])
	stop_date = datetime.date(year_adjusted, stop['month'], stop['day'])
	if lineup_date < start_date:
		return None, None

	day_count = lineup_date - start_date
	result = -(-day_count.days // 7)
	if result > 17 and year_adjusted < 2021 or result > 18 and year_adjusted > 2020:
		return None, None

	return year_adjusted, result


def getNextWeek(year, week):
	"""
	Returns the next sequential week of the NFL schedule given
	a current week of the NFL schedule
	"""
	if week < 17:
		return year, week + 1
	if year < 2021:
		return year + 1, 1
	if week >= 18:
		return year + 1, 1
	return year, week + 1








