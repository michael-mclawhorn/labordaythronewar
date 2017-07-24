from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json, random

import models
import broadcast, ajax

class Relations(ajax.AJAX):
    def get(self):
        user = users.get_current_user()
        q = models.Relation.all()
        if len(db.get(q)) == 0:
            # No relations defined, generate them
            for relation in ['favors', 'grudges']:
                sources = [character.user() for character in models.Characters.all() for i in range(getattr(character, relation))]
                targets = list(sources)
                random.shuffle(targets)
                # Build the inital pairings, which may have errors
                pairings = zip(sources, targets)
                success = filter(lambda x: x[0] != x[1], pairings)
                identity = filter(lambda x: x[0] == x[1], pairings)
                while len(identity) > 0:
                    first = identity.pop()
                    if len(identity) >= 1:
                        # We had at least two errors, make them a matched pair
                        second = identity.pop()
                    else:
                        for second in success:
                            if first[0] != second[0] and first[0] != second[1]:
                                success.remove(second)
                                break
                    success.extend([(first[0], second[1]), (second[0], first[1])])
                # success is now all valid pairings
                for (source, target) in success:
                    rel = models.Relation(source=source, relation=relation, target=target)
                    rel.put()
        self.reply(result='success')

    def post(self):
        user = users.get_current_user()
        all_data = self.json()
        dirty = False
        for data in all_data['relations']:
            # Try to find that relation, be sure that they own it
            relation = models.Relation.find(key = data['key'])
            # Make sure they can edit it
            if relation and (self.is_gm() or user == relation.source or user == relation.target):
                logging.debug("Data is %s" % repr(data))
                if relation.write(reason = data['reason']):
                    dirty = True
        if dirty:
            # This needs to filter to just users who are impacted by this update -- or just let it be a known bug
            for token in broadcast.get():
                (target, expires) = token
                if target == user or self.is_gm(target):
                    message = models.Relation.read_all(user=target, is_gm=self.is_gm(target))
                    broadcast.send(token, json.dumps({ 'relations': message }))
