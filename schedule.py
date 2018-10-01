from threading import  Thread
import time
from json import load
from dateutil.parser import parse
from dateutil.tz import tzlocal
from datetime import datetime
from requests import get
from suntime import Sun

latitude = 50.9397733
longitude = -1.4016822

sun = Sun(latitude, longitude)

def get_schedules():
	with open('config.json') as f:
		return load(f)['schedule']

def _schedule():
	while True:
		cur_time = datetime.now()
		for trigger in get_schedules():
			days = trigger["day"]
			if "all" in days or cur_time.strftime("%a") in days:
				if trigger["time"] == "sunset":
					t = sun.get_sunset_time().astimezone(tz=tzlocal()).replace(tzinfo=None)
					print("sunset", t)
				else:
					t = parse(trigger["time"])
				#print("{} triggers at {} in {} seconds".format(trigger["command"], t, (t - cur_time).seconds))
				if abs((t - cur_time).seconds) < 10:
					get("http://localhost/api/" + trigger["command"])
		time.sleep(5)

def start_scheduler():
	#schedule.every().day.at("22:30").do(goodnight).tag()
	t = Thread(target=_schedule)
	t.start()

if __name__ == "__main__":
	start_scheduler()