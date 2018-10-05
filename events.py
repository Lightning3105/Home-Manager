import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


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


if __name__ == '__main__':
	print(get_events())
