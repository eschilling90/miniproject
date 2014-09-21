import webapp2
import json
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from ConnexusUser import User as cUser
from ConnexusStream import Stream as cStream

class Management(webapp2.RequestHandler):
	def get(self):
		self.response.write('Management')

	def post(self):
		#in which you take a user id and return two lists of streams
		uId = self.request.get('user_id')
		userStreams = []
		subbedStreams = []
		result = cUser.query(userId == uId)
		user = result.get()
		if user:
			userStreams = getStreamList(user.userStreams)
			subbedStreams = getStreamList(user.subbedStreams)
		returnList = {'user_stream_list': userStreams, 'subbed_stream_list': subbedStreams}
		self.response.write(json.dumps(retunList))

	def getStreamList(streamList):
		returnStream = []
		for streamKey in streamList:
			stream = streamKey.get()
			if stream:
				returnStream.append(stream)
		return returnStream

class CreateStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('CreateStream')

	def post(self):
		#which takes a stream definition and returns a status code
		statusCode = 0
		streamName = self.request.get('stream_name')
		streamId = self.request.get('stream_id') #may need to just generate this
		userId = self.request.get('creator_id') #may need to just generate this
		newSubscribers = self.request.get('new_subscriber_list')
		urlCoverImage = self.request.get('url_cover_image')
		streamTags = self.request.get('stream_tags')
		for stream in cStream.query():
			if stream.streamId == streamId:
				statusCode = 1
			if stream.streamName == streamName:
				statusCode = 2
		if statusCode == 0:
			newstream = cStream(streamId = streamId,
				streamName = streamName,
				creatorId = userId,
				coverImageURL = urlCoverImage)
			newstream.tags.append(streamTags)
			streamKey = stream.put()
			cUser.addUserStream(userId, streamKey)
			addNewSubscribers(newSubscribers, streamKey)
		self.response.write(json.dumps({'status_code': statusCode}))

	def addNewSubscribers(subList, streamKey):
		for user in cUser.query(username.IN(subList)):
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
		result = cStream.query(streamId == streamId)
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
		result = cStream.query(streamId == streamId)
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
			streamInfo.append({stream.streamName: stream.coverImageURL})
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
				streamInfo.append({stream.streamName: stream.coverImageURL})
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
		self.response.write(json.dumps({'sorted_streams': topStreams})))

class ReportRequest(webapp2.RequestHandler):
	def post(self):
		s = ""

class LoginUser(webapp2.RequestHandler):
	def post(self):
		userName = self.request.get('user_name')
		userId = cUser.getUserId(username)
		cUser.AddNewUser(userId, username)

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