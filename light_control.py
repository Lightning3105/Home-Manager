from lifxlan import LifxLAN
from lifxlan.light import Light as LifxLightType
import flux_led
import colorsys
from json import load

with open('config.json') as f:
	palette = load(f)['palette']

def set(command):
	command = command.split('/')
	if command[0] == 'mode':
		mode = command[1]
		try:
			main_light = get_lifx()
			turn_on(main_light)
			set_colour(main_light, palette[mode]['main'])
		except:
			pass # do some scheduling here

		led_light = get_led()
		if mode == "off":
			turn_off(main_light)
			turn_off(led_light)
			return
		turn_on(led_light)
		set_colour(led_light, palette[mode]['led'])


def get_lifx():
	lan = LifxLAN(1)
	lights = lan.get_lights()
	return lights[0]


def get_led():
	scanner = flux_led.BulbScanner()
	lights = scanner.scan(timeout=1)
	light = flux_led.WifiLedBulb(lights[0]['ipaddr'])
	return light

def turn_on(light):
	if type(light) == LifxLightType:
		light.set_power(1)
	if type(light) == flux_led.WifiLedBulb:
		light.turnOn()

def turn_off(light):
	if type(light) == LifxLightType:
		light.set_power(0)
	if type(light) == flux_led.WifiLedBulb:
		light.turnOff()

def set_colour(light, colour):
	if type(light) == LifxLightType:
		colour = lifx_convert_colour(colour)
		light.set_color(colour)
	if type(light) == flux_led.WifiLedBulb:
		colour = led_convert_colour(colour)
		light.setRgb(*colour)

def lifx_convert_colour(colour):
	out = colorsys.rgb_to_hsv(colour[0], colour[1], colour[2])  # + ('2500')
	return (out[0] * 65535, out[1] * 65535, out[2] * 65535, 2500)

def led_convert_colour(colour):
	return (colour[0] * 255, colour[1] * 255, colour[2] * 255)

def get_lifx_colour():
	light = get_lifx()
	print(light.get_color())

if __name__ == "__main__":
	set('mode/night')