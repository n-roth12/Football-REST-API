from api import app, db, scheduler
from api.models import Update
from datetime import date
from scraper import scrape_week
from date_services import getNextWeek, findWeek
from update_database import build


@scheduler.task('interval', id='scrape_player_data', seconds=10000)
def scrape_player_data():
	"""
	Scrapes player data for the current week once every week
	Does nothing if if is the NFL offseason, postseason, or preseason
	Does nothing if it has not been seven days since the last update
	"""
	last_update = db.session.query(Update).order_by(Update.id.desc()).first()
	today_date = date.today()
	today_date = date(year=2022, month=1, day=14)
	if not last_update or (today_date - last_update.time.date()).days > 6:
		year, week = findWeek(today_date)
		if not year:
			print('Season is not active...')
			return
		scrape_week(year, week)
		build()
		t = Update(year=year, week=week)
		db.session.add(t)
		db.session.commit()
		print('added new update')
	else:
		print('not adding new update')
	return
