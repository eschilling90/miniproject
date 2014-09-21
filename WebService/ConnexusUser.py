from google.appengine.ext import ndb

class User(ndb.Model):

	userId = ndb.IntegerProperty()
	username = ndb.StringProperty()
	userStreams = ndb.KeyProperty(repeated=True)
	subbedStreams = ndb.KeyProperty(repeated=True)

	def setUsername(self, username):
		self.username = username

	def setUserId(self, userId):
		self.userId = userId

	def addUserStream(self, userId, streamKey):
		result = user.query(User.userId == userId)
		user = result.get()
		if user:
			user.userStreams.append(streamKey)

	def addSubStream(self, userId, streamKey):
		result = user.query(User.userId == userId)
		user = result.get()
		if user:
			user.subbedStreams.append(streamKey)

	def getSubbedStreams(self, userId):
		result = user.query(User.userId == userId)
		user = result.get()
		if user:
			return user.subbedStreams
		return []

	def getUserStreams (userId):
		#pdb.set_trace()
		userStreams = []
		subbedStreams = []
		result = User.query(User.username == userId)
		user = result.get()
		if user:
			userStreams = getStreamList(user.userStreams)
			subbedStreams = getStreamList(user.subbedStreams)
		return userStreams, subbedStreams

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.username

	def getAllUserStreams (userId):
		#pdb.set_trace()
		userStreams = []
		subbedStreams = []
		result = User.query(User.username == userId)
		user = result.get()
		if user:
			userStreams = getStreamList(user.userStreams)
			subbedStreams = getStreamList(user.subbedStreams)
		return userStreams, subbedStreams

	def addNewUser (newUserId, newUsername):
		#pdb.set_trace()
		user = User(userId = newUserId, username = newUsername)
		return user.put()

	def getUserId (uname):
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
		return maxId + 1
