# Declare our django version so it doesn't whine about it.
#from google.appengine.dist import use_library
#use_library('django', '1.2')

# Needed by the main code here
import logging
import webapp2

# Bring in the controllers
import controllers

logging.getLogger().setLevel(logging.DEBUG)
application = webapp2.WSGIApplication([
    ('/root/.*', controllers.Root),
    ('/character/.*', controllers.Character),
    ('/next/.*', controllers.Next),
    ('/relations/.*', controllers.Relations),
    ('/toys/.*', controllers.Toys),
], debug=True)
