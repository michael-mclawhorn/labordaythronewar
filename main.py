import logging
import webapp2
import controllers

logging.getLogger().setLevel(logging.DEBUG)
application = webapp2.WSGIApplication([
    ('/root/.*', controllers.Root),
    ('/character/.*', controllers.Character),
    ('/next/.*', controllers.Next),
    ('/relations/.*', controllers.Relations),
    ('/toys/.*', controllers.Toys),
], debug=True)
