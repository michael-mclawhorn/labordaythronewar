from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json, operator, datetime
from itertools import izip, count

import Models
import Rules
import broadcast, ajax

class Next(ajax.AJAX):
    def post(self):
        settings = Models.Settings.find()
        characters = Models.Characters.all()
        auctions = Rules.auctions

        # Compute the updates, then hold that thought
        updates_by_character = [map(operator.gt, character.bids_pending, character.bids_paid) for character in characters]
        updates_by_auction = zip(*updates_by_character)

        # Advance each character's bids
        for character in characters:
            character.bids_paid = character.bids_pending
            character.put()

        # Now evaluate what closed
        strikes = settings.strikes
        bidding = settings.bidding()
        for (i, auction, updates) in izip(count(), auctions, updates_by_auction):
            if auction.name in bidding:
                if not any(updates):
                    strikes[i] += 1
                else:
                    strikes[i] = 0
        settings.strikes = strikes
        # Finally write the throne war last so that everyone looks un-bid
        settings.put()
        settings.last_update = datetime.datetime.now()

        # The changes to the war and rankings are public knowledge
        message = settings.read()
        (ranked, spent) = Rules.rankings(settings, characters)
        message.update(rankings = ranked, spent = spent)
        #logging.debug("rankings are %s" % repr(response['rankings']))
        for token in broadcast.get():
            (user, expires) = token
            # Characters have to be added on a per-character basis
            message.update(characters = Models.Characters.read_all(user = user, is_gm = self.is_gm(user)))
            broadcast.send(token, json.dumps(message))

        # And send a reply of success
        self.reply(response = 'success')
