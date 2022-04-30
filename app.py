from api import app, scheduler
import scheduled_tasks

if __name__ == '__main__':
	scheduler.start()
	# app.run(host='0.0.0.0', port=5000, use_reloader=False)
	app.run()
