from json import load
from requests import get

with open('endpoints.json', 'r') as f:
	CONFIG = load(f)

ids = CONFIG['enabled_app_ids']

with open('enabled_app_ids', 'w'):
	pass

for app in ids:
	r = get("https://clients3.google.com/cast/chromecast/device/app?a={}".format(app))
	with open('enabled_app_ids', 'a') as f:
		f.write('\n')
		f.write(r.text)