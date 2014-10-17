from google.appengine.ext import ndb

import logging

class User(ndb.Model):

	username = ndb.StringProperty()
	emailPreference = ndb.IntegerProperty()
	userStreams = ndb.KeyProperty(repeated=True)
	subbedStreams = ndb.KeyProperty(repeated=True)

	def setUsername(self, username):
		self.username = username

	@staticmethod
	def addUserStream(username, streamKey):
		result = User.query(User.username == username)
		user = result.get()
		if user:
			logging.info("add user stream %s, %s", username, streamKey)
			user.userStreams.append(streamKey)
			user.put()
			logging.info("user stream length %s", len(user.userStreams))
	
	@staticmethod
	def addSubStream(username, streamKey):
		result = user.query(User.username == username)
		user = result.get()
		if user:
			user.subbedStreams.append(streamKey)
			user.put()

	@staticmethod
	def getSubbedStreams(username):
		result = user.query(User.username == username)
		user = result.get()
		if user:
			return user.subbedStreams
		return []

	@staticmethod
	def getUserStreams (username):
		#pdb.set_trace()
		userStreams = []
		subbedStreams = []
		result = User.query(User.username == username)
		user = result.get()
		if user:
			userStreams = getStreamList(user.userStreams)
			subbedStreams = getStreamList(user.subbedStreams)
		return userStreams, subbedStreams

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.username

	@staticmethod
	def getAllUserStreams (username):
		#pdb.set_trace()
		userStreams = []
		subbedStreams = []
		result = User.query(User.username == username)
		user = result.get()
		if user:
			userStreams = getStreamList(user.userStreams)
			subbedStreams = getStreamList(user.subbedStreams)
		return userStreams, subbedStreams

	@staticmethod
	def addNewUser (newUsername):
		#pdb.set_trace()
		user = User(username = newUsername)
		return user.put()

	'''def getUserId (uname):
		result = User.query(username == uname)
		user = result.get()
		userId = -1
		if user:
			userId = user.userId
		else:
			userId = getNewUserId()
		return userId

	def getNewUserId():
		maxId = 0
		for user in User.query():
			if user.userId > maxId:
				maxId = user.userId
		return maxId + 1'''
