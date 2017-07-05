__all__ = [
    AttributeAuction,
    RankedAuction,
    Round,
    WinnerTakesAllAuction,
]

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

from .thronewar import ThroneWar

class Round(ndb.Model):
    """
    An auction round in the throne war. A throne war may have multiple
    auction rounds, resulting in only some things being bidded on at a given
    time.
    """
    thronewar = ndb.KeyProperty(kind=ThroneWar, collection_name='rounds')
    order = ndb.IntegerProperty(default=0)


class Auction(polymodel.PolyModel):
    """
    An auction within a round
    """
    bid_round = ndb.KeyProperty(kind=Round, collection_name='auctions')
    name = ndb.StringProperty()
    description = ndb.TextProperty()

    default_bid = ndb.IntegerProperty(default=0)
    min_initial_bid = ndb.IntegerProperty(default=0)
    max_initial_bid = ndb.IntegerProperty(default=0)

    @property
    def ranked(self):
        """
        Return bids in ranked order.
        """
        return sorted(
            filter(
                lambda bid: bid.locked_bid > 0,
                self.bids
            ),
            key=operator.attrgetter('locked_bid'),
            reverse=True
        )

    @property
    def unranked(self):
        """
        Return all unranked bids.
        """
        return filter(
            lambda bid: bid.locked_bid == 0,
            self.bids
        )


class AttributeAuction(Auction):
    """
    An attribute auction -- ie this can be sold down
    """
    selldown_rungs = ndb.ListProperty(int, default=[-25, -10])
    selldown_names = ndb.StringListProperty(default=['human', 'chaos'])
    # TODO allow bidding down if the locked_bid is 0.

    @property
    def unranked(self):
        """
        Sell-downs are secret.
        """
        return filter(
            lambda bid: bid.locked_bid <= 0,
            self.bids
        )


class RankedAuction(Auction):
    """
    A power auction -- ie this can't be sold down
    """
    virtual_rungs = ndb.ListProperty(int)


class WinnerTakesAllAuction(Auction):
    """
    A winner-takes-all auction -- ie, auctioning off the captain of the
    castle guard position.
    """

    @property
    def ranked(self):
        """
        Only the highest bid counts.
        """
        return sorted(
            self.bids,
            key=operator.attrgetter('locked_bid'),
            reverse=True
        )[:1]

    @property
    def unranked(self):
        return sorted(
            self.bids,
            key=operator.attrgetter('locked_bid'),
            reverse=True
        )[1:]
