# Declare our django version so it doesn't whine about it.
#from google.appengine.dist import use_library
#use_library('django', '1.2')

# Needed by the main code here
import logging
import webapp2

# Bring in the controllers
import Controllers

logging.getLogger().setLevel(logging.DEBUG)
application = webapp2.WSGIApplication([
    ('/root/.*', Controllers.Root),
    ('/character/.*', Controllers.Character),
    ('/next/.*', Controllers.Next),
    ('/relations/.*', Controllers.Relations),
    ('/toys/.*', Controllers.Toys),
], debug=True)
