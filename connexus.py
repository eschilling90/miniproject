import os
import datetime

class User:

	def __init__ (self):
		self.userId = 0
		self.username = ""
		self.userStreams = []
		self.subbedStreams = []

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

class Stream:
	
	def __init__ (self):
		self.streamId = 0
		self.creatorId = 0
		self.streamName = ""
		self.coverImageURL = ""
		self.imageURLs = []
		self.viewTimes = []

	def setStreamName(self, streamName):
		self.streamName = streamName

	def setCreatorId (self, creatorId):
		self.creatorId = creatorId

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.streamName

userList = {}
streamList = {}

def getUserStreams (userId):
	userStreams = []
	subbedStreams = []
	if userList.has_key(userId):
		userStreams = userList[userId].userStreams
		subbedStreams = userList[userId].subbedStreams
	return userStreams, subbedStreams

def createStream (newStream):
	# look at create stream page for info on stream definition
	statusCode = 0
	for stream in streamList:
		if stream == newStream.streamId:
			statusCode = 1
		if streamList[stream].streamName == newStream.streamName:
			statusCode = 2
	if statusCode == 0:
		streamList[getNewStreamId()] = newStream
		userList[newStream.creatorId].addUserStream(newStream)
	return statusCode

def subscribeStream(userId, subStream):
	userList[userId].addSubStream(subStream)

def viewStream (streamId, oldStartPage, oldEndPage):
	URLlist = []

	URLlist = streamList[streamId].imageURLs

	newStartPage = 0
	newEndPage = 0
	return URLlist, newStartPage, newEndPage

def uploadImage (streamId, fileURL):
	if streamList.has_key(streamId):
		streamList[streamId].imageURLs.append(fileURL)

def viewAllStreams ():
	streamInfo = []
	for stream in streamList:
		streamInfo.append(streamList[stream].streamName)
	return streamInfo

def searchForStream (query):
	streamInfo = []
	for stream in streamList:
		if query in streamList[stream].streamName:
			streamInfo.append(streamList[stream].streamName)
	return streamInfo

def mostViewedStreams ():
	print "You called mostViewedStreams which does not do anything useful"
	sortedStreams = {}
	updateStreamViews()
	return topStreams

def sendReports ():
	print "Send reports through email"

def updateStreamViews ():
	for stream in streamList:
		for viewTime in stream.viewTimes:
			print viewTime

def getNewStreamId ():
	maxId = 0
	for streamId in streamList.keys():
		if streamId > maxId:
			maxId = streamId
	return maxId + 1

def getNewUserId ():
	maxId = 0
	for userId in userList.keys():
		if userId > maxId:
			maxId = userId
	return maxId + 1


def main():
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
	userList[1].addSubStream(stream2)
	subscribeStream(1, stream2)
	print getUserStreams(1)
	print viewAllStreams()


if __name__ == '__main__':
	main()