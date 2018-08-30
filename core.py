import flask
import requests
import schedule
from subprocess import Popen
import light_control
from threading import  Thread
import time

app = flask.Flask(__name__)

app.secret_key = "\x9d\x04/\xc6~\x9e\xea.\xe6\xfa\x89d\xf4M\xb4i\xf8\xf3\x12L\x89GuL"

@app.route('/api/manager/screen/<power>')
def screen(power):
	if power in ["on", True, 1]: power = '1'
	if power in ["off", False, 0]: power = '0'
	#vcgencmd display_power 0
	Popen(['vcgencmd', 'display_power', power])
	return 'Done'

@app.route('/')
def root():
	return 'Welcome'

@app.route('/api/server/<path:path>')
def server_proxy(path):
	try:
		return requests.get('http://192.168.1.5:5555/' + path).text
	except requests.exceptions.ConnectionError:
		return 'Server connection not established'

@app.route('/api/lights/<path:command>')
def lights(command):
	light_control.set(command)
	return "Done"

@app.route('/api/action/night')
def goodnight():
	screen(0)
	server_proxy('suspend')
	return "Done"

def start_scheduler():
	schedule.every().day.at("22:30").do(goodnight)

	def _schedule():
		while True:
			schedule.run_pending()
			time.sleep(1)

	t = Thread(target=_schedule)
	t.start()

start_scheduler()

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')