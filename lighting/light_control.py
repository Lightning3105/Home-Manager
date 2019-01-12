import traceback
import colorsys
from json import load
from time import sleep, time
from data import log, data_file

from lighting.lifx import Lifx
from lighting.magichome import MagicLight


class Light:
	def __init__(self, controller, name):
		self.controller = controller
		self.name = name

	def turn_on(self, duration=600):
		self.controller.turn_on(duration)
		self.set_colour()

	def turn_off(self, duration=900):
		self.controller.turn_off(duration)

	def is_on(self):
		return self.controller.is_on()

	def set_colour(self, colour=None, duration=500):
		if colour is None:
			colour = get_palette()[data_file.get('mode')][self.name]
		self.controller.set_colour(colour, duration=duration)

	def get_colour(self):
		return self.controller.get_colour()


def get_palette():
	with open('config.json') as f:
		return load(f)['palette']


def connect_lights():
	main_light = Light(Lifx("D0:73:D5:13:F3:BC", "192.168.1.12"), 'main')
	led_light = Light(MagicLight('192.168.1.11'), 'led')

	return main_light, led_light


def set(command):
	try:
		return _set(command)
	except Exception as e:
		log("General light set error:\n", traceback.format_exc())
		return "Failed"

def _set(command):
	main_light, led_light = connect_lights()
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
	else:
		log("Lights: ", command)

	return "Done"

def get_colours():
	mc = main_light.get_colour()
	mc = colorsys.hsv_to_rgb(mc[0] / 65535, mc[1] / 65535, mc[2] / 65535)
	mc = [round(c, 2) for c in mc]

	lc = led_light.get_colour()
	lc = [round(c/255, 2) for c in lc]

	out = "\"main\": {},\n\"led\": {}".format(mc, lc)
	print(out)
	return out

def test_mode(mode, state):
	print("=== {} ===".format(mode))
	main_light, led_light = connect_lights()
	led_light.turn_off()
	main_light.turn_off()
	sleep(1)
	set(mode + '/' + state)
	sleep(1)
	led_light.turn_on()
	main_light.turn_on()
	input()


def get_on():
	return main_light.is_on() + led_light.is_on()

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))

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
	main_light, led_light = connect_lights()
	if False:
		#print(main_light.get_colour())
		#main_light.turn_off()
		#sleep(2)
		led_light.turn_on()
		while True:
			led_light.set_colour('#ff0000')
			sleep(1)
			led_light.set_colour('#ffff00')
			sleep(1)
			led_light.set_colour('#00ff00')
			sleep(1)
			led_light.set_colour('#00ffff')
			sleep(1)
			led_light.set_colour('#0000ff')
			sleep(1)
			led_light.set_colour('#ff00ff')
			sleep(1)
	if True:
		test_mode('mode/day', 'auto')
		test_mode('mode/evening', 'auto')
		test_mode('mode/night', 'auto')
		test_mode('mode/dark', 'auto')
	if False:
		led_light.turn_on()
		led_light.controller._set_colour('#00ffff', 50000)
		while True:
			print(led_light.get_colour())
			sleep(1)
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
	if False:
		while True:
			print(set('on/get'), main_light.is_on(), led_light.is_on())
			sleep(1)
	if False:
		p = get_palette()
		for key, value in p.items():
			print('###', key, '###')
			for key, value in value.items():
				print(key, "#{:02x}{:02x}{:02x}".format(int(value[0] * 255), int(value[1] * 255), int(value[2] * 255)))
	#led_light.controller.setPresetPattern(0x25, 80)
	#main_light.turn_on()
	#set('mode/night')