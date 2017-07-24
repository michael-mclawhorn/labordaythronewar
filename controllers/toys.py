from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json

import Models
import ajax

class Toys(ajax.AJAX):
    def post(self):
        user = users.get_current_user()
        all_data = self.json()
        logging.debug("Toys.post all_data %s" % repr(all_data))
        dirty = False
        if self.is_gm():
            character = Models.Characters.find(email = all_data['email'])
        else:
            character = Models.Characters.find(user = user)
        for (klass, target) in [(Models.Items, 'items'), (Models.Shadows, 'shadows')]:
            if target in all_data:
                for remove in klass.all():
                    if remove.owner.email() == character.email():
                        remove.delete()
            for data in all_data[target]:
                safe_data = dict([(str(k), str(v)) for (k,v) in data.iteritems()])
                del safe_data['owner']
                new = klass(owner = character)
                new.put()
                new.write(**safe_data)
