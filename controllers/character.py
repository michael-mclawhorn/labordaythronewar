from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json

import models
import rules
import broadcast, ajax

class Character(ajax.AJAX):
    def post(self):
        settings = models.Settings.find()
        user = users.get_current_user()
        data = self.json()
        # Get the character to be updated
        if self.is_gm():
            character = models.Characters.find(email = data['email'])
        else:
            character = models.Characters.find(user = user)
        # Do the update
        character.write(settings, user, self.is_gm(), **data)
        # Broadcast any needed changes out
        (ranked, spent) = rules.rankings(settings, models.Characters.all())
        message = { 'spent': spent }
        for token in broadcast.get():
            (buser, expires) = token
            if user == buser:
                message['characters'] = models.Characters.read_all(user=buser, is_gm=self.is_gm(buser))
            else:
                message['characters'] = models.Characters.read_all()
            broadcast.send(token, json.dumps(message))
