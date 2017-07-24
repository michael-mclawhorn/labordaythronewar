from google.appengine.ext import ndb
from google.appengine.api import users
import logging

from characters import Characters
from mixins import ReadMixin, WriteMixin

class Shadows(ReadMixin, WriteMixin, ndb.Model):
    """
    An shadow paid for at character creation
    """
    name = ndb.StringProperty(default="unnamed")
    owner = ndb.KeyProperty(kind=Characters)
    description = ndb.TextProperty(default="no description")

    primality = ndb.IntegerProperty(default=1, choices=set([1, 2, 4]))
    control = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))
    barriers = ndb.IntegerProperty(default=0, choices=set([0, 1, 2, 4]))

    notes = ndb.TextProperty(default="none")

    def visisble(self, user):
        return self.owner.user() == user

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
