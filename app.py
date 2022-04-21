from api import app, db, scheduler
from api.models import Update
from datetime import date
from scraper import scrape_week

@scheduler.task('interval', id='test_job_1', seconds=10)
def job1():
	last_update = db.session.query(Update).order_by(Update.id.desc()).first()
	today_date = date.today()
	if not last_update or (today_date - last_update.time.date()).days > 6:
		scrape_week(date(year=2021, month=10, day=14))
		t = Update()
		db.session.add(t)
		db.session.commit()
		print('added new update')
	else:
		print('not adding new update')
	return

if __name__ == '__main__':
	# scheduler.start()
	app.run()
