from google.appengine.api import users
from google.appengine.ext import webapp
import logging, json

import Models
import Rules
import Broadcast, AJAX

class Character(AJAX.AJAX):
	def post(self):
		settings = Models.Settings.find()
		user = users.get_current_user()
		data = self.json()
		# Get the character to be updated
		if self.is_gm():
			character = Models.Characters.find(email = data['email'])
		else:
			character = Models.Characters.find(user = user)
		# Do the update
		character.write(settings, user, self.is_gm(), **data)
		# Broadcast any needed changes out
		(ranked, spent) = Rules.rankings(settings, Models.Characters.all())
		message = { 'spent': spent }
		for token in Broadcast.get():
			(buser, expires) = token
			if user == buser:
				message['characters'] = Models.Characters.read_all(user = buser, is_gm = self.is_gm(buser))
			else:
				message['characters'] = Models.Characters.read_all()
			Broadcast.send(token, json.dumps(message))
