import time
import sys
from meross_iot.api import MerossHttpClient
from time import sleep
from passwords import *

if __name__=='__main__':
	httpHandler = MerossHttpClient(email=meross_email, password=meross_password)

	# Retrieves the list of supported devices
	devices = httpHandler.list_supported_devices()
	plug = devices[0]
	while True:
		print(plug.get_electricity()['electricity']['power'])
		sleep(1)
