import webapp2
import json
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from ConnexusUser import User as cUser
from ConnexusStream import Stream as cStream

import logging

class Management(webapp2.RequestHandler):
	def get(self):
		self.response.write('Management')

	def post(self):
		#in which you take a user id and return two lists of streams
		logging.info("in management")
		uName = self.request.get('user_name')
		userStreams = []
		subbedStreams = []
		result = cUser.query(cUser.username == uName)
		user = result.get()
		logging.info(user.username)
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
				returnStream.append(stream.streamId)
		return returnStream

class CreateStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('CreateStream')

	def post(self):
		#which takes a stream definition and returns a status code
		statusCode = 0
		streamName = self.request.get('stream_name')
		#streamId = self.request.get('stream_id') #may need to just generate this
		sId = cStream.getStreamId(streamName)
		userName = self.request.get('creator_name') #may need to just generate this
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

class ViewStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('ViewStream')

	def post(self):
		#which takes a stream id and a page range and returns a
		#list of URLs to images, and a page range
		streamId = self.request.get('stream_id')
		startPage = self.request.get('start_page')
		endPage = self.request.get('end_page')
		URLlist = []
		result = cStream.query(cStream.streamId == streamId)
		stream = result.get()
		if stream:
			i = 0
			for url in stream.imageURLs:
				if i >= startPage and i < endPage:
					URLList.append(url)
				i = i + 1
		self.response.write(json.dumps({'url_list': URLList, 'start_page': startPage, 'end_page': endPage}))


class UploadImage(webapp2.RequestHandler):
	def get(self):
		self.response.write('UploadImage')

	def post(self):
		#which takes a stream id and a file
		streamId = self.request.get('stream_id')
		image = self.request.get('image')
		result = cStream.query(cStream.streamId == streamId)
		stream = query.get()
		if stream:
			blobinfo = get_uploads(image)[0]
			stream.imageURLs.append(blobinfo.key())

class ViewStreams(webapp2.RequestHandler):
	def get(self):
		self.response.write('ViewStreams')

	def post(self):
		#which returns a list of names of streams and their
		#cover images
		streamInfo = []
		for stream in cStream.query():
			streamInfo.append({'stream_id': stream.streamId, stream.streamId: (stream.streamName, stream.coverImageURL)})
		self.response.write(json.dumps({'stream_list': streamInfo}))

class SearchStreams(webapp2.RequestHandler):
	def get(self):
		self.response.write('SearchStreams')

	def post(self):
		#which takes a query string and returns a list of streams 
		#(titles and cover image urls) that contain matching text
		queryString = self.request.get('query_string')
		streamInfo = []
		for stream in cStream.query():
			if query in stream.streamName:
				streamInfo.append({'stream_id': stream.streamId, stream.streamId: (stream.streamName, stream.coverImageURL)})
		self.response.write(json.dumps({'stream_list': streamInfo}))

class MostViewedStreams(webapp2.RequestHandler):
	def post(self):
		#which returns a list of streams sorted by recent access
		#frequency
		searchStreams = {}
		topStreams = []
		cStream.updateStreamViews()
		for stream in cStream.query():
			searchStreams.append((stream.streamName, len(stream.viewTimes)))
		topStreams = sorted(searchStreams, lambda: x, -x[1])
		self.response.write(json.dumps({'sorted_streams': topStreams}))

class ReportRequest(webapp2.RequestHandler):
	def post(self):
		s = ""

class LoginUser(webapp2.RequestHandler):
	def post(self):
		#ndb.delete_multi(cUser.query().fetch(keys_only=True))
		uName = self.request.get('user_name')
		#userId = cUser.getUserId(username)
		statusCode = 0
		if cUser.query(cUser.username == uName).get():
			statusCode = 1
		else:
			cUser.addNewUser(uName)
			statusCode = 2
		self.response.write(json.dumps({'status_code': statusCode}))

application = webapp2.WSGIApplication([
	('/management', Management),
	('/createstream', CreateStream),
	('/viewstream', ViewStream),
	('/uploadimage', UploadImage),
	('/viewstreams', ViewStreams),
	('/searchstreams', SearchStreams),
	('/mostviewedstreams', MostViewedStreams),
	('/reportrequest', ReportRequest),
	('/loginuser', LoginUser)
], debug = True)