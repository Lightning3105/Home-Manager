import traceback

from lifxlan import LifxLAN
from lifxlan.light import Light as LifxLight
from lifxlan.errors import WorkflowException
import flux_led
import colorsys
from json import load
from time import sleep
from threading import Timer
from data import log, data_file

class Light:
	def __init__(self, controller):
		self.controller = controller
		self.lifx = type(controller) == LifxLight
		self.led = type(controller) == flux_led.WifiLedBulb

	def turn_on(self, duration=600):
		if self.lifx:
			try:
				self.controller.set_power(1, duration=duration)
			except WorkflowException as e:
				log(e)
				print(e)
		if self.led:
			self.controller.turnOn()
			if not self.is_on():
				log("Led Strip unresponsive turn on")
				connect_lights()
				self.turn_on()

		timer = Timer(1, self.set_colour)
		timer.start()

	def turn_off(self, duration=900):
		if self.lifx:
			try:
				self.controller.set_power(0, duration=duration)
			except WorkflowException as e:
				log(e)
				print(e)
		if self.led:
			self.controller.turnOff()
			if self.is_on():
				log("Led Strip unresponsive turn off")
				connect_lights()
				self.turn_off()

	def is_on(self):
		if self.lifx:
			return self.controller.get_power() == 65535
		if self.led:
			return self.controller.is_on

	def set_colour(self, colour=None, duration=500):
		if self.is_on():
			if self.lifx:
				if colour is None:
					colour = get_palette()[data_file.get('mode')]['main']
				colour = lifx_convert_colour(colour)
				self.controller.set_color(colour, duration=duration)
			elif self.led:
				if colour is None:
					colour = get_palette()[data_file.get('mode')]['led']
				colour = led_convert_colour(colour)
				self.controller.setRgb(*colour)

	def get_colour(self):
		if self.lifx:
			return self.controller.get_color()
		if self.led:
			return self.controller.getRgb()


def get_palette():
	with open('config.json') as f:
		return load(f)['palette']


def get_lifx():
	#lan = LifxLAN(1)
	#lights = lan.get_lights()
	return LifxLight("D0:73:D5:13:F3:BC", "192.168.1.12") #lights[0]


def get_led():
	#scanner = flux_led.BulbScanner()
	#lights = scanner.scan(timeout=1)
	return flux_led.WifiLedBulb('192.168.1.11')

def connect_lights():
	global main_light
	global led_light
	try:
		main_light = Light(get_lifx())
		led_light = Light(get_led())
	except Exception as e:
		log(e)
		print(e)

connect_lights()

def set(command):
	try:
		return _set(command)
	except Exception as e:
		log(traceback.format_exc())
		print(traceback.format_exc())
		return "Failed"

def _set(command):
	command = command.split('/')
	if len(command) == 2:
		if command[1] == 'get':
			if command[0] == 'mode':
				return data_file.get('mode')
			if command[0] == 'on':
				return get_on()
	if len(command) == 3:
		if command[2] == 'get':
			colours = get_palette()[command[1]]
			hexed = {}
			for key, value in colours.items():
				print(key, [hex(int(c * 255)) for c in value])
				h = "".join([hex(int(c * 255)).replace('0x', '').zfill(2) for c in value])
				hexed[key] = '#' + h
			return hexed
	if command[0] == 'mode':
		mode = command[1]
		data_file.set('mode', mode)
		if len(command) < 3:
			command = ['auto']
		else:
			command = command[2:]
	if command[0] == 'toggle':
		if get_on() == 2:
			command[0] = 'off'
		if get_on() < 2:
			command[0] = 'on'
	if command[0] == 'on':
		main_light.turn_on()
		led_light.turn_on()
	if command[0] == 'off':
		main_light.turn_off()
		led_light.turn_off()
	if command[0] == 'auto':
		main_light.set_colour()
		led_light.set_colour()
	if command[0] == 'silent':
		pass # Don't update
	if command[0] == 'reconnect':
		connect_lights()

	return "Done"


def lifx_convert_colour(colour):
	out = colorsys.rgb_to_hsv(colour[0], colour[1], colour[2])  # + ('2500')
	return (out[0] * 65535, out[1] * 65535, out[2] * 65535, 2500)


def led_convert_colour(colour):
	return (colour[0] * 255, colour[1] * 255, colour[2] * 255)


def get_colours():
	mc = main_light.get_colour()
	mc = colorsys.hsv_to_rgb(mc[0] / 65535, mc[1] / 65535, mc[2] / 65535)
	mc = [round(c, 2) for c in mc]

	lc = led_light.get_colour()
	lc = [round(c/255, 2) for c in lc]

	print(""""main": {},\n"led": {}""".format(mc, lc))

def test_mode(mode, state):
	led_light.turn_off()
	main_light.turn_off()
	sleep(3)
	set(mode + '/' + state)
	sleep(1)
	led_light.turn_on()
	main_light.turn_on()
	sleep(3)

def get_on():
	return main_light.is_on() + led_light.is_on()

"""
led strip preset patterns:
(speed - heigher is faster)
0x25    7 colour fade
0x26    Red fade on/off
0x27    Green fade on/off
0x28    Blue fade on/off
0x29    Yellow fade on/off
0x30    7 colour strobe/flash
0x31-7  Red/Green/Blue/Yellow/Cyan/Magenta/white flash
0x38    7 colour switch
"""


if __name__ == "__main__":
	if False:
		test_mode('mode/day', 'auto')
		test_mode('mode/evening', 'auto')
		test_mode('mode/night', 'auto')
		test_mode('mode/dark', 'auto')
	if False:
		while True:
			main_light.turn_off()
			led_light.turn_off()
			sleep(2)
			main_light.turn_on()
			led_light.turn_on()
			sleep(2)
	if False:
		set('off')
		sleep(2)
		set('mode/day/auto')
		sleep(2)
		set('on')
	if True:
		print(set('on/get'))
	#led_light.controller.setPresetPattern(0x25, 80)
	#main_light.turn_on()
	#set('mode/night')