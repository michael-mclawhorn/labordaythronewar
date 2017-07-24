from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import users
import logging, random

import rules

# Static properties
STATES = ['addPlayers', 'nameAndRelations', 'attributes', 'powers', 'finalTouches', 'play']
AUCTIONS = [i.name for i in rules.auctions]

class Settings(ndb.Model):
    """
    Class to represent a thronewar itself.

    Assumptions:
    * GMs are all set as application admins
    * There is only one throne war object
    """
    points = ndb.IntegerProperty(default=0) # Base build-points given for free
    grudges = ndb.IntegerProperty(default=0) # Maximum number of grudges allowed
    favors = ndb.IntegerProperty(default=0) # Maximum number of favors allowed
    state = ndb.StringProperty(default='addPlayers') # The current state of the throne war
    strikes = ndb.IntegerProperty(repeated=True) # Number of strikes against each auction
    last_update = ndb.DateTimeProperty(auto_now=True) # last time we got updated

    # A static variable which is the key for the single settings object
    THRONEWAR = "labordaythronewarvii"

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(
            *args,
            strikes=[0]*len(rules.auctions),
            **kwargs
        )

    @staticmethod
    def find(key=THRONEWAR):
        return Settings.get_or_insert(key)

    @staticmethod
    def auctions():
        return AUCTIONS

    def bidding(self):
        if self.state == 'attributes':
            return ['endurance', 'psyche', 'strength', 'warfare']
        elif self.state == 'powers':
            return ['logrus', 'pattern', 'shapeshifting', 'trump']

    def read(self, user=None, is_gm=False):
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
