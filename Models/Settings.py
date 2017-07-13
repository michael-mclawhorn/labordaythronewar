from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users
import logging, random

import Rules

# Static properties
STATES = ['addPlayers', 'nameAndRelations', 'attributes', 'powers', 'finalTouches', 'play']
AUCTIONS = [i.name for i in Rules.auctions]

class Settings(db.Model):
	"""
	Class to represent a thronewar itself.
	
	Assumptions:
	* GMs are all set as application admins
	* There is only one throne war object
	"""
	points = db.IntegerProperty(default=0)					# Base build-points given for free
	grudges = db.IntegerProperty(default=0)					# Maximum number of grudges allowed
	favors = db.IntegerProperty(default=0)					# Maximum number of favors allowed
	state = db.StringProperty(default='addPlayers')	# The current state of the throne war
	strikes = db.ListProperty(int, default=[0]*10)	# Number of strikes against each auction
	last_update = db.DateTimeProperty(auto_now=True)	# last time we got updated

	
	# A static variable which is the key for the single settings object
	THRONEWAR = "labordaythronewarvii"


	@staticmethod
	def find(key = THRONEWAR):
		return Settings.get_or_insert(key)


	@staticmethod
	def auctions():
		return AUCTIONS


	def bidding(self):
		if self.state == 'attributes':
			return ['endurance', 'psyche', 'strength', 'warfare']
		elif self.state == 'powers':
			return ['logrus', 'pattern', 'shapeshifting', 'trump']


	def read(self, user = None, is_gm = False):
		reply = {
			'points': self.points,
			'grudges': self.grudges,
			'favors': self.favors,
			'state': self.state,
			'states': STATES,
			'bidding': self.bidding(),
			'strikes': [{'name': auction, 'strikes': strikes} for (auction, strikes) in zip(AUCTIONS, self.strikes)],
		}
		return reply

		
	def write(self, **kwargs):
		logging.debug("Settings.write on %s" % repr(kwargs))
		updated = False
		for ints in ['points', 'grudges', 'favors']:
			if ints in kwargs:
				updated = True
				setattr(self, ints, int(kwargs[ints]))
		if 'state' in kwargs:
			updated = True
			self.state = kwargs['state']
		if 'strikes' in kwargs:
			updated = True
			self.strikes = [int(x) for x in kwargs['strikes']]
		if updated:
			self.put()
			return self
