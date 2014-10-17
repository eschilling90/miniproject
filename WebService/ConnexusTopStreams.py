from google.appengine.ext import ndb
from ConnexusUser import User
import time
import datetime


import logging

class topStream (ndb.Model):
	streamId = ndb.IntegerProperty()
	streamName = ndb.StringProperty()
	totalViews = ndb.IntegerProperty()
	coverImageURL = ndb.StringProperty()

	@staticmethod
	def addTopStream(Sid, sName,cover, total):
		newstream = topStream(streamId= Sid, streamName = sName, coverImageURL = cover, totalViews=total)
		return newstream.put()