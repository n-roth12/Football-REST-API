from api import app, scheduler
import scheduled_tasks

if __name__ == '__main__':
	scheduler.start()
	app.run(host='127.0.0.1', port=8000, use_reloader=False)
	app.run()
