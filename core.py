from os import path

import flask
from flask_cors import CORS

import requests
from schedule import start_scheduler
from subprocess import Popen, PIPE
from lighting import light_control
from data import log, get_logs, data_file
import re
import events
from notify import say
from datetime import datetime, timedelta

try:
	from flic import flic_client
except OSError:
	pass
#killall flicd

app = flask.Flask(__name__)

CORS(app)

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
#/sys/devices/platform/omap_i2c.2/i2c-2/2-002c/backlight/bowser/brightness

@app.route('/api/dashboard/screen/get')
def get_screen_brightness():
    current = Popen(['ssh', 'james@192.168.1.9', '-p 2222', "su -c \"cat /sys/devices/platform/omap_i2c.2/i2c-2/2-002c/backlight/bowser/brightness\""], stdout=PIPE)
    current = current.stdout.read().strip()
    return current

@app.route('/api/dashboard/screen/<power>')
def dashboard_screen(power):
	if power in ["on", True]: power = 255
	if power in ["off", False]: power = 1
	if power == "toggle":
		current = int(get_screen_brightness())
		if current > 100:
			power = 1
		else:
			power = 255
	power = str(power)
	Popen(['ssh', 'james@192.168.1.9', '-p 2222', "su -c \"echo {} > /sys/devices/platform/omap_i2c.2/i2c-2/2-002c/backlight/bowser/brightness\"".format(power)])

	return "Done"


@app.route('/')
def root():
	out= """
	<head>
		<title>Control Panel</title>
	</head>
	
	<body>
	"""
	commands = [
		'/api/lights/on',
		'/api/lights/off',
		'/api/lights/mode/day',
		'/api/lights/mode/evening',
		'/api/lights/mode/night',
		'/api/lights/mode/dark/silent',
		'/api/lights/get_config',
		'/api/dashboard/screen/on',
		'/api/dashboard/screen/off',
		'/api/manager/update',
		'/api/server/suspend',
		'/logs'
	]
	for command in commands:
		out += "<a href='{}'>{}</a></br>".format(command, command)

	out += "</body>"
	return out

@app.route('/dashboard')
def dashboard():
	return flask.send_file('frontend/index.html')

@app.route('/css/<path:path>')
def send_css(path):
	return flask.send_file('frontend/css/' + path)

@app.route('/js/<path:path>')
def send_js(path):
	return flask.send_file('frontend/js/' + path)

@app.route('/img/<path:path>')
def send_img(path):
	return flask.send_file('frontend/img/' + path)

@app.route('/fonts/<path:path>')
def send_font(path):
	return flask.send_file('frontend/fonts/' + path)

@app.route('/api/server/<path:path>')
def server_proxy(path):
	try:
		return requests.get('http://192.168.1.5:5555/' + path).text
	except requests.exceptions.ConnectionError:
		return 'Server connection not established'


@app.route('/api/lights/<path:command>')
def lights(command):
	return flask.jsonify(light_control.set(command))


@app.route('/api/lights/get_config')
def get_light_config():
	return light_control.get_colours().replace("\n", "</br>")
	

@app.route('/api/action/night')
def goodnight():
	screen(0)
	server_proxy('suspend')
	dashboard_screen(0)
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
	today = False
	for l in lgs:
		regex = r"(\[\d*/\d*/\d*\s\d*\:\d*\:\d*\])\s(.*)"
		matches = list(re.finditer(regex, l))
		if len(matches) > 0:
			t, m = matches[0].groups()
			if t[1:].split(" ")[0] == datetime.now().strftime("%Y/%m/%d"):
				today = True
			else:
				today = False
		else:
			t = ""
			m = l
		out += """
		<tr {}>
			<td>{}</td>
			<td>{}</td>
		</tr>""".format('style="color: red"' if today else '', t, m)
	out += """</tr>
	</table>
	</body>"""

	return out

@app.route('/api/manager/update')
def update(res=True):
	cur_dir = path.dirname(path.realpath(__file__))
	Popen(['git', 'pull'], cwd=cur_dir).wait()
	if res: restart()
	return "Done"


@app.route('/api/calendar/events')
def cal_events():
	return flask.jsonify(events.get_events())

@app.route('/api/calendar/first')
def first_event():
	return flask.jsonify(events.first_event_time())

@app.route('/api/calendar/first/say')
def first_event_say():
	say("your first event tomorrow is at {}".format(events.first_event_time().strftime("%-I:%M %P")))
	return first_event()

@app.route('/api/calendar/wakeup')
def wakeup_time():
	return flask.jsonify(events.wakeup_time())

@app.route('/api/calendar/wakeup/say')
def wakeup_time_say():
	say("you need to wakeup for {}".format(events.wakeup_time().strftime("%-I:%M %P")))
	return wakeup_time()


@app.route('/api/scheduler/<status>')
def scheduler_status(status):
	if status in ['suspend', 'off' 'false']: status = True
	if status in ['run', 'on', 'true']: status = False
	data_file.set('suspend_schedule', status)
	return "Done"

@app.route('/camera')
def camera_stream():
	req = requests.get('http://192.168.1.10/?action=stream', stream=True)
	return flask.Response(req.iter_content(chunk_size=1024), content_type=req.headers['content-type'])

@app.route('/api/say/<message>')
def broadcast(message):
	message = message.replace("_", " ")
	return message

#@app.route('/api/phone/battery/<percentage>')


log("========= STARTED =========")
start_scheduler()

if __name__ == "__main__":
	app.run(host='192.168.1.4', debug=True, port=4000)
	#Popen(['npm', 'run', 'start'], cwd=path.dirname(path.realpath(__file__)) + '/assistant-relay')
	#input()