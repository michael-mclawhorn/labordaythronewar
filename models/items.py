from google.appengine.ext import ndb
from google.appengine.api import users
import logging

from characters import Characters
from mixins import ReadMixin, WriteMixin

class Items(ReadMixin, WriteMixin, ndb.Model):
    """
    An item paid for at character creation
    """
    name = ndb.StringProperty(default="unnamed")
    owner = ndb.KeyProperty(kind=Characters)
    description = ndb.TextProperty(default="no description")

    vitality = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    aggression = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    intelligence = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

    movement = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    psychic_sensitivity = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    psychic_defense = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

    shadow_movement = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    shadow_control = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    shapeshifting = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    trump_images = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    power_words = ndb.IntegerProperty(default=0, choices=set([0, 1, 2]))

    quantity = ndb.IntegerProperty(default=1, choices=set([0, 1, 2, 3]))

    notes = ndb.TextProperty(default="none")

    def visible(serlf, user):
        return self.owner.user() == user

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
