from google.appengine.ext import db
from google.appengine.api import users
import logging

class Relation(db.Model):
    """
    This represents the relationship between two players -- be it a
    favor or a grudge.
    """
    source = db.UserProperty()
    relation = db.StringProperty(choices=set(['favors', 'grudges']))
    target = db.UserProperty()
    reason = db.StringProperty(default='')

    @staticmethod
    def find(key=None):
        return Relation.get(key)

    def read(self):
        return {
            'key': str(self.key()),
            'source': self.source.email(),
            'target': self.target.email(),
            'relation': self.relation,
            'reason': self.reason,
        }

    @staticmethod
    def read_all(user=None, is_gm=False):
        return [rel.read() for rel in Relation.all() if is_gm or rel.source == user or rel.target == user]

    def write(self, reason=None):
        self.reason = reason
        self.put()
        return True
