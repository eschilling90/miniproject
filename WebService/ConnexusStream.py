from google.appengine.ext import ndb

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
	streamTags = ndb.StringProperty(repeated=True)

	def setStreamName(self, streamName):
		self.streamName = streamName

	def setCreatorId (self, creatorId):
		self.creatorId = creatorId

	def __repr__ (self):
		return str(self)

	def __str__ (self):
		return self.streamName

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