import datetime
from dateutil.parser import parse
import pytz
from googleapiclient.discovery import build
import googleapiclient.errors
from httplib2 import Http
from oauth2client import file, client, tools
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
from data import log


def main():
	"""Shows basic usage of the Google Calendar API.
	Prints the start and name of the next 10 events on the user's calendar.
	"""
	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('calendar', 'v3', http=creds.authorize(Http()))

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
	print('Getting the upcoming 10 events')
	# print(service.calendarList().list().execute()['items'])
	events_result = service.events().list(calendarId='vdq8dbokpfdq2ad0grkh5396pn01mo86@import.calendar.google.com',
	                                      timeMin=now,
	                                      maxResults=10, singleEvents=True,
	                                      orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
		print('No upcoming events found.')
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		print(start, event['summary'])


def get_events():
	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('calendar', 'v3', http=creds.authorize(Http()))

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

	all_events = []

	for calendar in ['jameswaters3105@gmail.com', '6lebjqih32rfepv9qodda85gok@group.calendar.google.com',
	                 'vdq8dbokpfdq2ad0grkh5396pn01mo86@import.calendar.google.com']:
		events_result = service.events().list(calendarId=calendar,
		                                      timeMin=now,
		                                      maxResults=10, singleEvents=True,
		                                      orderBy='startTime').execute()
		events = events_result.get('items', [])

		for event in events:
			all_events.append(event)
	return all_events


def first_event_time() -> datetime.datetime:
	try:
		events = get_events()
	except googleapiclient.errors.HttpError:
		log("Error getting calendar events")
		return None
	for event in events:
		if 'dateTime' in event['start'].keys():
			event['start']['dateTime'] = parse(event['start']['dateTime'])
		else:
			event['start']['dateTime'] = parse(event['start']['date'] + "T00:00:00Z")
	events.sort(key=lambda event: event['start']['dateTime'])

	firstTime = None

	if datetime.datetime.now().hour <= 5:
		day = datetime.datetime.now().date()
	else:
		day = datetime.datetime.now().date() + datetime.timedelta(days=1)

	for event in events:
		time = event['start']['dateTime']
		if day == time.date():
			firstTime = time
			break

	return firstTime

def wakeup_time():
	first = first_event_time() + datetime.timedelta(hours=-1.5)
	base = first.replace(hour=9, minute=0)

	if first.time() > base.time():
		return base
	else:
		return first

if __name__ == '__main__':
	first_event_time()
