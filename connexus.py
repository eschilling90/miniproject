import os
import datetime

from google.appengine.api import app_identity
from google.appengine.ext import ndb

import sys, pdb
for attr in ('stdin', 'stderr'):
	setattr(sys, attr, getattr(sys, '__%s__' % attr))

class User(ndb.Model):

	userId = ndb.IntegerProperty()
	username = ndb.StringProperty()
	userStreams = ndb.KeyProperty(repeated=True)
	subbedStreams = ndb.KeyProperty(repeated=True)

	def createStream (self, newStream):
		# look at create stream page for info on stream definition
		statusCode = 0
		for stream in getAllStreams():
			if stream.streamId == newStream.streamId:
				statusCode = 1
			if stream.streamName == newStream.streamName:
				statusCode = 2
		statusCode = 0
		if statusCode == 0:
			streamKey = newStream.put()
			self.addUserStream(streamKey)
		return statusCode

	def setUsername(self, username):
		self.username = username

	def setUserId(self, userId):
		self.userId = userId

	def addUserStream(self, stream):
		self.userStreams.append(stream)

	def addSubStream(self, stream):
		self.subbedStreams.append(stream)

	def getSubbedStreams(self):
		return self.subbedStreams

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.username

class Stream (ndb.Model):
	
	streamId = ndb.IntegerProperty()
	creatorId = ndb.IntegerProperty()
	streamName = ndb.StringProperty()
	blobstoreURL = ndb.StringProperty()
	coverImageURL = ndb.BlobKeyProperty()
	#repeated=True means that we can have multiple entries for
	# imageURLs or viewTimes. Essentially, it acts as a list
	imageURLs = ndb.BlobKeyProperty(repeated=True)
	viewTimes = ndb.DateTimeProperty(repeated=True)

	def setStreamName(self, streamName):
		self.streamName = streamName

	def setCreatorId (self, creatorId):
		self.creatorId = creatorId

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.streamName

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

def getStreamList(streamList):
	returnStream = []
	for streamKey in streamList:
		stream = streamKey.get()
		if stream:
			returnStream.append(stream)
	return returnStream

def subscribeStream(userId, subStream):
	query = User.query(userId == userId)
	user = query.get()
	if user:
		user.addSubStream(subStream)

def viewStream (streamId, oldStartPage, oldEndPage):
	URLlist = []
	stream = Stream.query(streamId == streamId).get()
	for url in stream.imageURLs:
		URLList.append(url)
	newStartPage = oldStartPage
	newEndPage = oldEndPage
	return URLlist, newStartPage, newEndPage

def uploadImage (streamId, image):
	query = Stream.query(streamId == streamId)
	stream = query.get()
	if stream:
		blobInfo = get_uploads(image)[0]
		stream.imageURLs.append(blobInfo.key())

def viewAllStreams ():
	streamInfo = []
	for stream in Stream.query():
		streamInfo.append((stream.streamName, stream.coverImageURL))
	return streamInfo

def searchForStream (query):
	streamInfo = []
	for stream in Stream.query():
		if query in stream.streamName:
			streamInfo.append(stream.streamName)
	return streamInfo

def mostViewedStreams ():
	searchStreams = {}
	topStreams = []
	updateStreamViews()
	'''for stream in Stream.query():
		for views in searchStreams.keys():
			if len(stream.viewTimes) > views or len(searchStreams) < 3:
				if len(searchStreams) < 3:
					del searchStreams[views]
				searchStreams[len(stream.viewTimes)] = stream.streamId
	for stream in sorted(searchStreams, lambda: x, x):
		topStreams.append(searchStreams[stream])'''
	for stream in Stream.query():
		searchStreams.append((stream.streamId, len(stream.viewTimes)))
	topStreams = sorted(searchStreams, lambda: x, -x[1])
	return topStreams

def sendReports ():
	print "Send reports through email"

def addViewToStream (streamId):
	stream = Stream.query(streamId == streamId).get()
	if stream:
		stream.viewTimes.append(datetime.datetime.now())
		updateStreamViews()

def updateStreamViews ():
	for stream in Stream.query():
		for viewTime in stream.viewTimes:
			if viewTime > datetime.datetime.now()-datetime.timedelta(hours=1):
				del viewTime

def getUsers():
	#ndb.delete_multi(User.query().fetch(keys_only=True))
	#key = addNewUser(getNewUserId(), "user")
	return User.query().fetch(100) #key.get()
	
def userCount():
	return User.query().count()

def addNewUser (newUserId, newUsername):
	#pdb.set_trace()
	user = User(userId = newUserId, username = newUsername)
	stream = Stream(streamName = "stream2")
	streamKey = stream.put()
	user.subbedStreams = [streamKey]
	stream2 = Stream(streamName = "stream1")
	user.createStream(stream2)
	return user.put()

def getAllStreams():
	streamList = []
	for stream in Stream.query():
		streamList.append(stream)
	return streamList

'''def main():
	user1 = User()
	user1.setUsername("user1")
	user1.setUserId(1)
	userList[user1.userId] = user1

	user2 = User()
	user2.setUsername("user2")
	user2.setUserId(getNewUserId())
	userList[user2.userId] = user2

	stream1 = Stream()
	stream1.setCreatorId(1)
	stream1.setStreamName("Stream1")
	createStream(stream1)

	stream2 = Stream()
	stream2.setCreatorId(1)
	stream2.setStreamName("Stream2")
	createStream(stream2)

	print "main", userList[1].userStreams
	print "main", userList[1].userStreams
	print searchForStream("S")
	subscribeStream(1, stream2)
	print getUserStreams(1)
	print viewAllStreams()

if __name__ == '__main__':
	main()'''