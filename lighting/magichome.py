import socket
import flux_led
from data import log
from lighting.baselight import BaseLight


class MagicLight(BaseLight):
	def __init__(self, ipaddr):
		super().__init__()
		self.__ipaddr = ipaddr
		self.controller = None
		self.connect()

	def connect(self):
		try:
			self.controller = flux_led.WifiLedBulb(self.__ipaddr)
		except socket.timeout as e:
			log("MagicLight connection", e)

	def test_connected(self):
		if self.controller is None:
			self.connect()

		if self.controller is None:
			return False
		else:
			return True

	def _turn_on(self, duration=600):
		self.test_connected()
		self.controller.turnOn()

	def _turn_off(self, duration=900):
		self.test_connected()
		self.controller.turnOff()

	def is_on(self):
		self.controller.update_state()
		return self.controller.is_on

	def _set_colour(self, colour=None, duration=500):
		self.test_connected()
		pre = self.get_colour()
		colour = self.convert_from_hex(colour)
		self.controller.setRgb(*colour)
		#print("is changing", self.get_colour() != pre, "is on", self.is_on())
		return self.get_colour() != pre

	def get_colour(self):
		if not self.test_connected():
			return None
		self.controller.update_state()
		return self.convert_to_hex(self.controller.getRgb())

	def convert_from_hex(self, hex):
		hex = hex.strip('#')
		return tuple(int(hex[i:i+2], 16) for i in (0, 2 ,4))

	def convert_to_hex(self, rgb):
		return "#{:02x}{:02x}{:02x}".format(*rgb)
