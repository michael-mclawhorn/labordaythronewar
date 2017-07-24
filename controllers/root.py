from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json, datetime

import models
import rules
import broadcast, ajax

class Root(ajax.AJAX):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        is_gm = self.is_gm()
        # Give the user the basic connection information
        response = {
            'token': broadcast.add(user),
            'is_gm': is_gm,
            'email': user.email(),
            'logout_url': users.create_logout_url('/'),
        }
        # The throne war settings update as root-level entities
        settings = models.Settings.find()
        response.update(settings.read())
        # The key/email/name for other characters
        characters = models.Characters.all()
        response.update(characters=models.Characters.read_all(user=user, is_gm=is_gm))
        # Add rankings for the auctions
        (ranked, spent) = rules.rankings(settings, characters)
        response.update(rankings=ranked, spent=spent)
        #logging.debug("rankings are %s" % repr(response['rankings']))
        # Add relations
        response.update(relations=models.Relation.read_all(user=user, is_gm=is_gm))
        # And items and shadows
        response.update(items=models.Items.read_all(user=user, is_gm=is_gm), shadows=models.Shadows.read_all(user=user, is_gm=is_gm))
        # Send that to the user
        self.reply(**response)

    def post(self):
        if self.is_gm():
            data = self.json()
            # Update the settings
            #logging.debug("About to write %s" % repr(data))
            settings = models.Settings.find()
            settings.write(**data)
            # The make sure the right players exist
            if 'characters' in data and len(data['characters']) > 0:
                emails = [d['email'] for d in data['characters']]
                for character in models.Characters.all():
                    if character.email() not in emails:
                        character.delete()
                    else:
                        emails.remove(character.email())
                for newbie in emails:
                    user = users.User(newbie)
                    victim = models.Characters.find(user=user, create=True)
                    victim.put()
            # Now build an update to send to everyone of the throne war settings and new character list
            message = models.Settings.find().read()
            # And the ranks in case we switched to one of those modes
            settings.last_update = datetime.datetime.now()
            (ranked, spent) = rules.rankings(settings, models.Characters.all())
            message.update(rankings=ranked, spent=spent)
            for token in broadcast.get():
                (user, expires) = token
                message.update(characters=models.Characters.read_all(user=user, is_gm=self.is_gm(user)))
                broadcast.send(token, json.dumps(message))
