from google.appengine.ext import db
from google.appengine.api import users
import logging

from Character import Character
from Shadow import Shadow

class Event(db.Model):
  """
	Record the GMs doing something to a particular player
  """
  player = db.ListProperty(db.Key)					# of Character.key() -- this is happening to who?
	location = db.ReferenceProperty(Shadow)		# where did this event happen
	time = db.DateTimeProperty(auto_now=true)	# real-life date/time of this event
	delays = db.IntegerProperty()							# the number of blocks they're out for
  event = db.StringProperty(choices=set(['arrived', 'resting', 'working']))
  finished = db.BooleanProperty()						# Did this complete without interruption
