import webapp2
import json
import urllib
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from ConnexusUser import User as cUser
from ConnexusStream import Stream as cStream


class LoginUser(webapp2.RequestHandler):
	def get(self):
		self.response.write('LoginUser')

	def post(self):
		statusCode=0
		username = self.request.get('username')
		user = cUser.query(cUser.username == username).get()
		if not user:
			newUser = cUser(username = username)
			newUser.put()
			statusCode=1

		self.response.write(json.dumps({'status_code': statusCode}))


class Management(webapp2.RequestHandler):
	def get(self):
		self.response.write('Management')

	def post(self):
		#in which you take a user id and return two lists of streams
		logging.error("in management")
		uName = self.request.get('username')

		userStreams = []
		subbedStreams = []
		result = cUser.query(cUser.username == uName)
		user = result.get()
		if user:
			userStreams = Management.getStreamList(user.userStreams)
			subbedStreams = Management.getStreamList(user.subbedStreams)
		logging.info(userStreams)
		logging.info(subbedStreams)
		returnList = {'user_stream_list': userStreams, 'subbed_stream_list': subbedStreams}
		self.response.write(json.dumps(returnList))

	@staticmethod
	def getStreamList(streamList):
		returnStream = []
		logging.info("stream length %s", len(streamList))
		for streamKey in streamList:
			stream = streamKey.get()
			logging.info("stream %s", stream)
			if stream:
				returnStream.append({'streamId': stream.streamId, 'streamName': stream.streamName})
		return returnStream



class CreateStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('CreateStream')

	def post(self):
		#which takes a stream definition and returns a status code
		statusCode = 0
		streamName = self.request.get('stream_name')
		#streamId = self.request.get('stream_id') #may need to just generate this
		sId = 32;
		sId = cStream.getStreamId(streamName)
		userName = self.request.get('username') #may need to just generate this
		#newSubscribers = self.request.get('new_subscriber_list')
		#urlCoverImage = self.request.get('url_cover_image')
		#streamTags = self.request.get('stream_tags')
		streamList = []
		for stream in cStream.query():
			if stream.streamId == sId:
				statusCode = 1
			if stream.streamName == streamName:
				statusCode = 2
			streamList.append((stream.streamName, stream.creatorName))
		if statusCode == 0:
			streamKey = cStream.addNewStream(sId, streamName, userName)
			cUser.addUserStream(userName, streamKey)

			#CreateStream.addNewSubscribers(newSubscribers, streamKey)
		self.response.write(json.dumps({'status_code': statusCode, 'streams': streamList}))

	@staticmethod
	def addNewSubscribers(subList, streamKey):
		for user in cUser.query(cUser.username.IN(subList)):
			user.subbedStreams.append(streamKey)



application = webapp2.WSGIApplication([
	('/loginuser', LoginUser),
	('/management', Management),
	('/createStream',CreateStream)
], debug = True)