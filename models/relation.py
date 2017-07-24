from google.appengine.ext import ndb
from google.appengine.api import users
import logging

from mixins import ReadMixin, WriteMixin

class Relation(ReadMixin, WriteMixin, ndb.Model):
    """
    This represents the relationship between two players -- be it a
    favor or a grudge.
    """
    source = ndb.UserProperty()
    relation = ndb.StringProperty(choices=set(['favors', 'grudges']))
    target = ndb.UserProperty()
    reason = ndb.StringProperty(default='')

    @staticmethod
    def find(key=None):
        return Relation.get(key)

    def read(self):
        return {
            'key': self.key.urlsafe(),
            'source': self.source.email(),
            'target': self.target.email(),
            'relation': self.relation,
            'reason': self.reason,
        }

    def visible(self, user):
        return user in [self.source, self.target]
