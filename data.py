from pickle import load, dump
from datetime import datetime
import os

class File():
	def __init__(self, file):
		self.file = file
		self.open = False

	def load(self):
		if not os.path.exists(self.file):
			return {}
		with open(self.file, 'rb') as f:
			return load(f)

	def get(self, key):
		data = self.load()
		return data[key]

	def set(self, key, value):
		data = self.load()
		data[key] = value
		self.save(data)

	def save(self, data):
		with open(self.file, 'wb') as f:
			dump(data, f)


data_file = File('storage.dat')
log_file = 'log.txt'


def log(*args):
	out = " ".join([str(a) for a in args])
	now = datetime.now()
	logstr = now.strftime('[%Y/%m/%d %H:%M:%S]') + " " + out + "\n"
	if not os.path.exists(log_file):
		with open(log_file, 'w') as f:
			pass
	with open(log_file, 'a') as f:
		f.write(logstr)