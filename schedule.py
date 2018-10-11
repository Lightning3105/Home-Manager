from threading import  Thread
import time
from json import load
from dateutil.parser import parse
from dateutil.tz import tzlocal
from datetime import datetime, timedelta
from requests import get
from suntime import Sun
from data import log

latitude = 50.9397733
longitude = -1.4016822

sun = Sun(latitude, longitude)

def get_schedules():
	with open('config.json') as f:
		return load(f)['schedule']

def _schedule():
	while True:
		cur_time = datetime.now()
		for trigger in get_schedules(): # type: dict
			days = trigger["day"]
			if "all" in days or cur_time.strftime("%a") in days:
				if trigger["time"] == "sunset":
					t = sun.get_sunset_time().astimezone(tz=tzlocal()).replace(tzinfo=None)
					#print("sunset", t)
				elif trigger["time"][0] == "M":
					interval = int(trigger["time"][1:])
					t = cur_time
					while t.minute % interval != 0:
						t += timedelta(seconds=5)
				elif trigger["time"][0] == "H":
					interval = int(trigger["time"][1:])
					t = cur_time
					while t.hour % interval != 0:
						t += timedelta(seconds=5)
				else:
					t = parse(trigger["time"])
				t += timedelta(seconds=int(trigger.get('offset', 0)))
				#print(trigger, t)
				#print("{} triggers at {} in {} seconds".format(trigger["command"], t, (t - cur_time).seconds))
				if abs((t - cur_time).seconds) < 10:
					log(trigger, 'triggered at', t)
					try:
					    get("http://localhost/api/" + trigger["command"])
					except:
					    log("Failed to send command")
		time.sleep(5)

def start_scheduler():
	#schedule.every().day.at("22:30").do(goodnight).tag()
	t = Thread(target=_schedule)
	t.setDaemon(True)
	t.start()

if __name__ == "__main__":
	if True:
		start_scheduler()
		while True:
			pass
	if False:
		for trigger in get_schedules():
			print(trigger['command'])
			get("http://localhost:5000/api/" + trigger["command"])
			time.sleep(3)
		get("http://localhost:5000/api/lights/on")