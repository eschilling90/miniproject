from google.appengine.ext import ndb
import datetime
import logging

class Stream (ndb.Model):
	
	streamId = ndb.IntegerProperty()
	creatorName = ndb.StringProperty()
	streamName = ndb.StringProperty()
	coverImageURL = ndb.StringProperty()
	totalViews = ndb.IntegerProperty()
	lastUpload = ndb.StringProperty()
	creationTime = ndb.DateTimeProperty(auto_now_add=True)
	#repeated=True means that we can have multiple entries for
	# imageURLs or viewTimes. Essentially, it acts as a list
	imageURLs = ndb.BlobKeyProperty(repeated=True)
	viewTimes = ndb.DateTimeProperty(repeated=True)
	streamTags = ndb.StringProperty(repeated=True)

	def setStreamName(self, streamName):
		self.streamName = streamName

	def setCreatorId (self, creatorName):
		self.creatorName = creatorName

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.streamName

	@staticmethod
	def addNewStream(sId, sName, cName, urlCover, tags):
		newstream = Stream(streamId = sId, streamName = sName, creatorName = cName, coverImageURL = urlCover, totalViews = 0)
		logging.info("streamname %s", sName)
		newstream.streamTags.extend(tags)
		newstream.totalViews = 0
		return newstream.put()

	@staticmethod
	def addViewToStream (streamId):
		stream = Stream.query(Stream.streamId == streamId).get()
		if stream:
			if not stream.totalViews:
				stream.totalViews = 0
			stream.totalViews = stream.totalViews + 1
			stream.viewTimes.append(datetime.datetime.now())
			stream.put()

	@staticmethod
	def updateStreamViews ():
		for stream in Stream.query():
			for viewTime in stream.viewTimes:
				if viewTime > datetime.datetime.now()-datetime.timedelta(hours=1):
					del viewTime
			stream.put()

	@staticmethod
	def getStreamId (sName):
		result = Stream.query(Stream.streamName == sName)
		stream = result.get()
		streamId = -1
		if stream:
			streamId = stream.streamId
		else:
			streamId = Stream.getNewStreamId()
		return streamId

	@staticmethod
	def getNewStreamId():
		maxId = 0
		for stream in Stream.query():
			if stream.streamId > maxId:
				maxId = stream.streamId
		return maxId + 1