from lifxlan import LifxLAN
from lifxlan.light import Light as LifxLightType
import flux_led
import colorsys
from json import load
from time import sleep

class Light:
	def __init__(self, controller):
		self.controller = controller
		self.lifx = type(controller) == LifxLightType
		self.led = type(controller) == flux_led.WifiLedBulb

	def turn_on(self):
		if self.lifx:
			self.controller.set_power(1)
		if self.led:
			self.controller.turnOn()

	def turn_off(self):
		if self.lifx:
			self.controller.set_power(0)
		if self.led:
			self.controller.turnOff()

	def set_colour(self, colour):
		if self.lifx:
			colour = lifx_convert_colour(colour)
			self.controller.set_color(colour)
		if self.led:
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
	lan = LifxLAN(1)
	lights = lan.get_lights()
	return lights[0]


def get_led():
	#scanner = flux_led.BulbScanner()
	#lights = scanner.scan(timeout=1)
	light = flux_led.WifiLedBulb('192.168.1.11')
	return light

main_light = Light(get_lifx())
led_light = Light(get_led())

def set(command):
	command = command.split('/')
	if command[0] == 'mode':
		mode = command[1]
		if mode == "off":
			main_light.turn_off()
			led_light.turn_off()
		else:
			main_light.turn_on()
			main_light.set_colour(get_palette()[mode]['main'])

			led_light.turn_on()
			led_light.set_colour(get_palette()[mode]['led'])


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


if __name__ == "__main__":
	set('mode/day')
	sleep(3)
	set('mode/evening')
	sleep(3)
	set('mode/night')
	sleep(3)
	set('mode/dark')
	#get_colours()