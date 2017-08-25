from google.appengine.ext import db
from google.appengine.api import users
import logging

from settings import Settings
import rules

QUESTIONS = [
    "The first time you walked the Pattern, where did you have it send you? Why?",
    "Describe the circumstances under which your actions resulted in someone's death. If there are many deaths, pick a particularly memorable one. Do you regret it?",
    "Why do you wish to rule Amber? (``I don't,`` or any of its variations, is not an acceptable answer.)",
    "Where were you during the rebellion against Oberon? How would you characterize the defenders of Amber during that conflict? Do you regret your actions (or inactions) now?",
]

class Characters(db.Model):
    """
    A character in a throne war. This holds pretty much everything you would expect
    on a character sheet.
    """
    # Player editable properties
    name = db.StringProperty() # The character's name
    grudges = db.IntegerProperty(default=0) # How many grudges they took
    favors = db.IntegerProperty(default=0) # How many favors they took
    questions = db.StringListProperty(default=['']*len(QUESTIONS)) # Character questions answers

    # Bids
    bids_paid = db.ListProperty(int, default=[0]*len(rules.auctions)) # Comitted to these bids
    bids_pending = db.ListProperty(int, default=[0]*len(rules.auctions)) # These are what they are bidding now

    # GM-only properties
    approved = db.UserProperty() # Which gm approved this character
    notes = db.StringProperty() # GM's notes
    delays = db.IntegerProperty(default=0) # How many delays have they had
    queue = db.DateTimeProperty() # Set to a valid value if they are waiting on the GM

    # System properties
    last_update = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def find(key=None, user=None, email=None, create=False):
        if create:
            f = Characters.get_or_insert
        else:
            f = Characters.get_by_key_name
        if key:
            return f(key)
        elif user:
            return f(str(user.email()))
        elif email:
            return f(email)

    @staticmethod
    def read_all(user=None, is_gm=False):
        return [char.read(user=user, is_gm=is_gm) for char in Characters.all()]

    def email(self):
        return self.key().name()

    def user(self):
        return users.User(self.email())

    def read(self, user=None, is_gm=False):
        settings = Settings.find()
        public = {
            'key': str(self.key()),
            'email': self.email(),
            'name': self.name,
            'updated': self.last_update > settings.last_update,
        }
        if (user and user.email() == self.email()) or is_gm:
            public.update({
                'questions': [{ 'question': q, 'answer': a } for (q, a) in zip(QUESTIONS, self.questions)],
                'approved': self.approved,
                'grudges': self.grudges,
                'favors': self.favors,
            })
            for (i, auction) in enumerate(settings.auctions()):
                public[auction + '_paid'] = self.bids_paid[i]
                public[auction] = self.bids_pending[i]
        if is_gm:
            public.update(notes=self.notes, delays=self.delays, queue=self.queue)
        return public


    def write(self, settings=None, user=None, is_gm=False, **kwargs):
        #logging.debug("Character.write(%s)" % repr(kwargs))
        state = settings.state
        dirty = False
        if state == 'addPlayers':
            # Nothing to do here at all
            pass
        elif state == 'nameAndRelations':
            # Can update the name and number of grudges/favors
            for (prop, converter) in [('name', str), ('grudges', int), ('favors', int)]:
                if prop in kwargs:
                    try:
                        var = converter(kwargs[prop])
                        if prop == 'grudges' and (var < 0 or var > settings.grudges):
                            pass
                        elif prop == 'favors' and (var < 0 or var > settings.favors):
                            pass
                        else:
                            setattr(self, prop, var)
                            dirty = True
                    except ValueError:
                        pass
        elif state == 'attributes' or state == 'powers':
            bidding = settings.bidding()
            for (i, auction) in enumerate(rules.auctions):
                # Updates to closed auctions are silently ignored
                if settings.strikes[i] < 3:
                    if auction.name in bidding and auction.name in kwargs:
                        old = self.bids_paid[i]
                        try:
                            new = int(kwargs[auction.name])
                            rungs = rules.rungs(Characters.all())[i]
                            #logging.debug("Calling %s's valid on old=%s, new=%s, rungs=%s" % (auction.name, old, new, repr(rungs)))
                            if auction.valid(rungs, old, new):
                                self.bids_pending[i] = new
                                dirty = True
                            else:
                                return True
                                #raise Exception("invalid bid of %s on %s" % (new, auction.name))
                        except ValueError:
                            pass
        elif state == 'mystery':
            bidding = settings.bidding()
            new = {}
            valid = []
            bidded = []
            for i, auction in enumerate(rules.auctions):
                if auction.name in bidding:
                    old = self.bids_paid[i]
                    try:
                        new[auction.name] = int(kwargs[auction.name])
                        rungs = rules.rungs(Characters.all())[i]
                        valid.append(auction.valid(rungs, old, new[auction.name]))
                        bidded.append(new[auction.name] > 0)
                    except ValueError:
                        return True

            # To be legal bids, all mystery boxes must be valid bids and
            # only one may be non-zero.
            one_bid = iter(bidded)
            if all(valid) and (not any(bidded) or (any(one_bid) and not any(one_bid))):
                for i, auction in enumerate(rules.auctions):
                    if auction.name in new:
                        self.bids_pending[i] = new[auction.name]
                        dirty = True
        elif state == 'finalTouches':
            maxBuyup = 0
            valid = True
            for (i, auction) in enumerate(rules.auctions):
                rungs = rules.rungs(Characters.all())[i]
                if auction.name in kwargs:
                    old = self.bids_paid[i]
                    try:
                        new = int(kwargs[auction.name])
                        if new >= old and new in rungs:
                            # Buying up to a run
                            self.bids_pending[i] = new
                            dirty = True
                        elif auction.name in ['endurance', 'psyche', 'strength', 'warfare'] and old == 0 and new in [-10, -25]:
                            # Selling down to chaos or human
                            self.bids_pending[i] = new
                            dirty = True
                        elif auction.name == 'conjuration' and new in [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
                            self.bids_pending[i] = new
                        elif auction.name == 'power_words' and new in [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
                            self.bids_pending[i] = new
                    except ValueError:
                        pass
                if auction.name == 'psyche':
                    maxBuyup = int(auction.reward(rungs, self.bids_pending[i]))
                # Validate that they can buy things up that far -- psyche has already happened so we can trust maxBuyup
                if auction.name in ['logrus', 'pattern', 'shapeshifting', 'trump']:
                    oldrank = rungs.index(self.bids_paid[i])
                    newrank = rungs.index(self.bids_pending[i])
                    logging.debug("Validating %s, rungs %s oldrank %s newrank %s maxBuyup %s" % (auction.name, repr(rungs), oldrank, newrank, maxBuyup))
                    if newrank < (oldrank - maxBuyup):
                        valid = False
                        logging.debug("%s failed to validate buyups within psyche's allowed range" % self.name)
            # If we received something invalid, undo all their attempts to buy-up
            if not valid:
                self.bids_pending = self.bids_paid
                dirty = True
            else:
                # Save the answers to the questions
                if 'questions' in kwargs:
                    logging.debug("questions are %s" % kwargs['questions'])
                    qs = dict()
                    for i in kwargs['questions']:
                        qs[i['question']] = i['answer']
                    self.questions = [qs[q] for q in QUESTIONS]
                    dirty = True
        else:
            raise Exception("unimplemented character.write() state %s!" % state)
        if dirty:
            #logging.debug("Put character")
            self.put()
            return True
