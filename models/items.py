from google.appengine.ext import db
from google.appengine.api import users
import logging

from characters import Characters

class Items(db.Model):
    """
    An item paid for at character creation
    """
    name = db.StringProperty(default="unnamed")
    owner = db.ReferenceProperty(Characters)
    description = db.TextProperty(default="no description")

    vitality = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    aggression = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    intelligence = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

    movement = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    psychic_sensitivity = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    psychic_defense = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

    shadow_movement = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    shadow_control = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    shapeshifting = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    trump_images = db.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    power_words = db.IntegerProperty(default=0, choices=set([0, 1, 2]))

    quantity = db.IntegerProperty(default=1, choices=set([0, 1, 2, 3]))

    notes = db.TextProperty(default="none")

    @staticmethod
    def read_all(user=None, is_gm=False):
        return [item.read() for item in Items.all() if item.owner.user() == user or is_gm]

    def read(self):
        return {
            'name': self.name,
            'owner': self.owner.email(),
            'description': self.description,
            'vitality': self.vitality,
            'aggression': self.aggression,
            'intelligence': self.intelligence,
            'movement': self.movement,
            'psychic_sensitivity': self.psychic_sensitivity,
            'psychic_defense': self.psychic_defense,
            'shadow_movement': self.shadow_movement,
            'shadow_control': self.shadow_control,
            'shapeshifting': self.shapeshifting,
            'trump_images': self.trump_images,
            'power_words': self.power_words,
            'quantity': self.quantity,
            'notes': self.notes,
        }

    def write(self, **kwargs):
        logging.debug("kwargs %s" % repr(kwargs))
        try:
            for (prop, value) in kwargs.iteritems():
                logging.debug("Trying to set %s to %s" % (prop, value))
                if prop not in ['name', 'description', 'notes']:
                    value = int(value)
                setattr(self, prop, value)
            self.put()
            logging.debug("I am now %s" % repr(self.read()))
            return True
        except ValueError:
            return False
