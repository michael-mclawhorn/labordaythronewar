from google.appengine.ext import db
from google.appengine.api import users
import logging

from Characters import Characters

class Shadows(db.Model):
	"""
	An shadow paid for at character creation
	"""
	name = db.StringProperty(default="unnamed")
	owner = db.ReferenceProperty(Characters)
	description = db.TextProperty(default="no description")

	primality = db.IntegerProperty(default=1, choices=set([1, 2, 4]))
	control = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
	barriers = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

	notes = db.TextProperty(default="none")

	@staticmethod
	def read_all(user = None, is_gm = False):
		return [shadow.read() for shadow in Shadows.all() if shadow.owner.user() == user or is_gm]

	def read(self):
		return {
			'name': self.name,
			'owner': self.owner.email(),
			'description': self.description,
			'primality': self.primality,
			'control': self.control,
			'barriers': self.barriers,
			'notes': self.notes,
		}

	def write(self, **kwargs):
		try:
			for (prop, value) in kwargs.iteritems():
				if prop not in ['name', 'description', 'notes']:
					value = int(value)
				setattr(self, prop, value)
			self.put()
			return True
		except ValueError:
			return False
