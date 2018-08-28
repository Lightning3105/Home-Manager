import flask
import requests
import schedule
from subprocess import Popen

app = flask.Flask(__name__)

app.secret_key = "\x9d\x04/\xc6~\x9e\xea.\xe6\xfa\x89d\xf4M\xb4i\xf8\xf3\x12L\x89GuL"

@app.route('/api/manager/screen/<power>')
def screen(power):
	if power in ["on", True, 1]: power = '1'
	if power in ["off", False, 0]: power = '0'
	#vcgencmd display_power 0
	Popen(['vcgencmd', 'display_power', power])
	return 'Done'

schedule.every().day.at("22:30").do(screen, power='0')

@app.route('/')
def root():
	return 'Welcome'

@app.route('/api/server/<path:path>')
def server_proxy(path):
	return requests.get('http://192.168.1.5:5555/' + path)

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')