from abc import abstractmethod
from threading import Timer


class BaseLight:
	def __init__(self):
		self._onTarget = None
		self._colourTarget = None
		self.__queue = []

	def update(self):
		#TODO: actually keep track using a file/database
		#print("""+++ {} +++\nTargets:\n\ton: {}\tcolour: {}\nPhsical:\n\ton: {}\tcolour: {}---------------""".format(type(self), self._onTarget, self._colourTarget, self.is_on(), self.get_colour()))
		syncTime = 0
		if self._onTarget is not None:
			if self._onTarget[0] != self.is_on():
				syncTime = self._onTarget[1]
				#print("ON:", type(self), self._onTarget, self.is_on())
				if self._onTarget[0] is True:
					if self._turn_on(self._onTarget[1]):
						self._onTarget = None
				else:
					if self._turn_off(self._onTarget[1]):
						self._onTarget = None
		if self._colourTarget is not None:
			if self._colourTarget[0] != self.get_colour():
				syncTime = max((syncTime, self._colourTarget[1]))
				#print("COLOUR:", type(self), self._colourTarget, self.get_colour())
				if self._set_colour(*self._colourTarget):
					self._colourTarget = None

		if syncTime == 0:
			self._onTarget = None
			self._colourTarget = None
		else:
			t = Timer(2, self.update)
			t.start()

	def turn_on(self, duration=600):
		#print(">>>>", type(self), "on")
		self._onTarget = (True, duration)
		self.update()

	@abstractmethod
	def _turn_on(self, duration):
		raise NotImplementedError()

	def turn_off(self, duration=900):
		#print(">>>>", type(self), "off")
		self._onTarget = (False, duration)
		self.update()

	@abstractmethod
	def _turn_off(self, duration):
		raise NotImplementedError()

	def set_colour(self, colour, duration=500):
		#print(">>>>", type(self), "colour", colour)
		self._colourTarget = (colour, duration)
		self.update()

	@abstractmethod
	def _set_colour(self, colour, duration):
		raise NotImplementedError()