import colorsys
from lifxlan.light import Light as LifxLight
from lifxlan.errors import WorkflowException
from data import log
from lighting.baselight import BaseLight


class Lifx(BaseLight):
	def __init__(self, mac_addr, ip_addr):
		super().__init__()
		self.__mac_addr = mac_addr
		self.__ip_addr = ip_addr
		self.connect()

	def connect(self):
		self.controller = LifxLight(self.__mac_addr, self.__ip_addr)

	def _turn_on(self, duration):
		try:
			self.controller.set_power(1, duration=duration)
			return True
		except WorkflowException as e:
			log("Lifx on error", e)
			return False

	def _turn_off(self, duration):
		try:
			self.controller.set_power(0, duration=duration)
			return True
		except WorkflowException as e:
			log("Lifx off error", e)
			return False

	def _set_colour(self, colour, duration):
		try:
			colour = self.convert_from_hex(colour)
			self.controller.set_color(colour, duration=duration)
			return True
		except WorkflowException as e:
			log("Lifx colour {} error".format(colour), e)
			return False

	def is_on(self):
		try:
			return self.controller.get_power() == 65535
		except WorkflowException as e:
			log(e)
			return None

	def get_colour(self):
		try:
			return self.convert_to_hex(self.controller.get_color())
		except WorkflowException as e:
			log(e)
			return None

	@staticmethod
	def convert_from_hex(hexstring):
		hexstring = hexstring.strip('#')
		rgb = tuple(int(hexstring[i:i+2], 16) for i in (0, 2 ,4))
		hsv = colorsys.rgb_to_hsv(*rgb)
		print(hsv)
		return hsv[0] * 65535, hsv[1] * 65535, hsv[2] * 257, 2500

	@staticmethod
	def convert_to_hex(hsv):
		rgb = colorsys.hsv_to_rgb(hsv[0]/65535, hsv[1]/65535, hsv[2]/65535)
		return "#{:02x}{:02x}{:02x}".format(*(int(round(d * 255)) for d in rgb))
