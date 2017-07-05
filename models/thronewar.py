__all__ = [
    Player,
    ThroneWar,
]

from google.appengine.ext import ndb

STATES = ['gm_setup', 'player_setup', 'auctions', 'post_auction', 'play']

class ThroneWar(ndb.Model):
    """
    """
    # Owner's user object is stored as the key
    name = ndb.StringProperty()
    state = ndb.StringProperty(default='gm_setup')

    points = ndb.IntegerProperty(default=0)
    grudges = ndb.IntegerProperty(default=0)
    favors = ndb.IntegerProperty(default=0)


class Player(ndb.Model):
    """
    A throne war participant
    """
    # GM controlled attributes
    user = ndb.UserProperty()
    thronewar = ndb.KeyProperty(kind=ThroneWar, collection_name='rounds')
    is_gm = ndb.BooleanProperty(default=False)

    # Player controlled attributes
    name = ndb.StringProperty()


class Bid(ndb.Model):
    """
    The bids from a player in the auctions
    """
    auction = ndb.KeyProperty(kind=Auction, collection_name='bids')
    player = ndb.KeyProperty(kind=Player, collection_name='bids')

    min_bid = ndb.IntegerProperty(default=None)
    locked_bid = ndb.IntegerProperty(default=0)
    current_bid = ndb.IntegerProperty(default=0)
    max_bid = ndb.IntegerProperty(default=None)
