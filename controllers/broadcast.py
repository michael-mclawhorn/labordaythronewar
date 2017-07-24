from google.appengine.api import channel
from google.appengine.api import memcache
import logging, json, time

def get():
    mem = memcache.get('tokens')
    if mem:
        return mem
    else:
        return []

def add(user = None):
    if not user:
        user = users.get_current_user()
    # Compute some things
    now = time.time()
    newEntry = (user, now + 60*60*2)        # Tokens expire in 2hrs * 60min/hr * 60sec/min
    newToken = channel.create_channel(user.user_id())
    # Filter out any tokens that have expired or are old tokens for this user
    current_tokens = [(u,e) for (u,e) in get() if now < e and u != user]
    current_tokens.append(newEntry)
    memcache.set('tokens', current_tokens, 60*60*2)
    return newToken

def send(token, message):
    (user, expires) = token
    if time.time() < expires:
        #logging.debug("Broadcast.send to %s message %s" % (user.email(), repr(message)))
        channel.send_message(user.user_id(), message)
