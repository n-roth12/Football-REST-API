from api import app, scheduler
import scheduled_tasks

if __name__ == '__main__':
	scheduler.start()
	app.run()
