#!/usr/bin/env python3

# Test Client application.
#
# This program attempts to connect to all previously verified Flic buttons by this server.
# Once connected, it prints Down and Up when a button is pressed or released.
# It also monitors when new buttons are verified and connects to them as well. For example, run this program and at the same time the scan_wizard.py program.

from . import fliclib
from threading import Timer, Thread
from requests import get
from subprocess import Popen
from time import sleep
from json import load


def get_commands():
	with open('config.json') as f:
		return load(f)['flic']


Popen(['flic/armv6l/flicd', '-f', 'flic/flic.sqlite3'])
sleep(5)

client = fliclib.FlicClient("localhost")

timeout = 0.3

timer = None

def got_button(bd_addr):
	cc = fliclib.ButtonConnectionChannel(bd_addr)
	cc.on_button_up_or_down = \
		lambda channel, click_type, was_queued, time_diff: handle_click(channel, click_type, was_queued, time_diff) 
	cc.on_connection_status_changed = \
		lambda channel, connection_status, disconnect_reason: \
			print(channel.bd_addr + " " + str(connection_status) + (" " + str(disconnect_reason) if connection_status == fliclib.ConnectionStatus.Disconnected else ""))
	client.add_connection_channel(cc)

def got_info(items):
	print(items)
	for bd_addr in items["bd_addr_of_verified_buttons"]:
		got_button(bd_addr)

def handle_click(channel, click_type, was_queued, time_diff):
	global timer
	if click_type == fliclib.ClickType.ButtonDown:
		if timer is not None:
			timer.cancel()
			timer = None
			double_click_action()
		else:
			timer = Timer(timeout, hold_press_action)
			timer.start();
	if click_type == fliclib.ClickType.ButtonUp:
		if timer is not None:
			timer.cancel()
			timer = Timer(timeout, single_click_action)
			timer.start()

def single_click_action():
	global timer
	timer = None
	print("single")
	get("http://localhost/api/" + get_commands()['single'])

def double_click_action():
	global timer
	timer = None
	print("double")
	get("http://localhost/api/" + get_commands()['double'])

def hold_press_action():
	global timer
	timer = None
	print("hold")
	get("http://localhost/api/" + get_commands()['hold'])
		

client.get_info(got_info)

client.on_new_verified_button = got_button

t = Thread(target=client.handle_events)
t.start()
