from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
import logging, json


GMS = [
    'svirpridon@gmail.com',
    'kilroy@gmail.com',
    'aaron.g.brakke@gmail.com',
    'test@example.com',
]

class AJAX(webapp.RequestHandler):
    def json(self):
        """ Get the post arguments we got as JSON """
        # FIXME:
        # https://webapp2.readthedocs.io/en/latest/guide/request.html#post-data
        # switch to request.params
        return dict([(str(key), value) for (key, value) in json.loads(self.request.body).iteritems()])


    def is_gm(self, user = None):
        """ is the user who was passed (or the current user) a gm? """
        if not user:
            user = users.get_current_user()
        return user.email().lower() in GMS


    def reply(self, **kwargs):
        """ send a reply to the caller as json """
        self.response.set_status(200)
        self.response.headers.add_header('Cache-Control', 'no-cache')
        self.response.out.write(json.dumps(kwargs))
