from os import path

import flask
import requests
from schedule import start_scheduler
from subprocess import Popen
import light_control
from data import log, get_logs
import re

try:
	from flic import flic_client
except OSError:
	pass
#killall flicd

app = flask.Flask(__name__)

app.secret_key = "\x9d\x04/\xc6~\x9e\xea.\xe6\xfa\x89d\xf4M\xb4i\xf8\xf3\x12L\x89GuL"

@app.route('/api/manager/screen/<power>')
def screen(power):
	if power in ["on", True, 1]: power = '1'
	if power in ["off", False, 0]: power = '0'
	#vcgencmd display_power 0
	Popen(['vcgencmd', 'display_power', power])
	return 'Done'


@app.route('/api/manager/restart')
def restart():
	Popen(['sudo', 'systemctl', 'restart', 'home_manager.service'])
	return "Done"


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

@app.route('/api/')
def app_end():
	return "Api"

@app.route('/logs')
def logs():
	out = """
	<head>
		<title>Logs</title>
	</head>
	
	<body>
		<table>
			<tr>
			    <th>Time</th>
			    <th>Message</th> 
			  </tr>
	"""
	lgs = get_logs()
	for l in lgs:
		regex = r"(\[\d*/\d*/\d*\s\d*\:\d*\:\d*\])\s(.*)"
		matches = list(re.finditer(regex, l))
		if len(matches) > 0:
			t, m = matches[0].groups()
		else:
			t = ""
			m = l
		out += """
		<tr>
			<td>{}</td>
			<td>{}</td>
		</tr>""".format(t, m)
	out += """</tr>
	</table>
	</body>"""

	return out

@app.route('/update')
def update():
	cur_dir = path.dirname(path.realpath(__file__))
	Popen(['git', 'pull'], cwd=cur_dir)
	return "Done"

start_scheduler()

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')