import webapp2
import json
import urllib
import logging
import re

from google.appengine.api import files, images, urlfetch, mail
from google.appengine.ext import blobstore, ndb
from google.appengine.ext.webapp import blobstore_handlers

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
		logging.info("in management")
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
		sId = cStream.getStreamId(streamName)
		userName = self.request.get('creator_name')
		newSubscribersUnparsed = self.request.get('new_subscriber_list')
		newSubscribers = newSubscribersUnparsed.split(",")
		urlCoverImage = self.request.get('url_cover_image')
		streamTagsUnparsed = self.request.get('stream_tags')
		streamTagsUnparsed = streamTags.split(",")
		comment = self.request.get('comment')
		streamList = []
		for sub in newSubscribers:
			logging.info(sub)
		for stream in cStream.query():
			if stream.streamId == sId:
				statusCode = 1
			if stream.streamName == streamName:
				statusCode = 2
			streamList.append((stream.streamName, stream.creatorName))
		if statusCode == 0:
			streamKey = cStream.addNewStream(sId, streamName, userName, urlCoverImage, streamTags)
			cUser.addUserStream(userName, streamKey)
			CreateStream.addNewSubscribers(newSubscribers, streamKey)
			CreateStream.sendSubscriptionEmail(newSubscribers, streamName, userName, comment)
		self.response.write(json.dumps({'status_code': statusCode, 'streams': streamList}))

	@staticmethod
	def addNewSubscribers(subList, streamKey):
		for user in subList:
			cUser.addSubStream(user, streamKey)

	@staticmethod
	def sendSubscriptionEmail(subList, streamname, creatorname, comment):
		for sub in subList:
			if (mail.is_email_valid(sub)):
				message = mail.EmailMessage(sender="Erik Schilling <erik.schilling@gmail.com>",
		                            subject="Subscription Notice")

				message.to = sub
				message.body = """
				Dear Connexus User:
				You are now subscribed to the following stream: {0}
				This stream was created by {1}
				""".format(streamname, creatorname)
				if comment:
					message.body = message.body + """
					{0} has this personal message to give:
					{1}
					""".format(creatorname, comment)
				message.boady = message.body + """
				Please let us know if you have any questions.
				The Connexus Team
				"""
				#message.send()

class ViewStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('ViewStream')

	def post(self):
		#which takes a stream id and a page range and returns a
		#list of URLs to images, and a page range
		streamId = self.request.get('stream_id')
		startPage = int(self.request.get('start_page'))
		endPage = int(self.request.get('end_page'))
		urlList = []
		result = cStream.query(cStream.streamId == int(streamId))
		stream = result.get()
		logging.info("in viewstream")
		if stream:
			i = 0
			cStream.addViewToStream(streamId)
			for url in stream.imageURLs:
				logging.info(startPage, i, endPage)
				if i >= startPage and i < endPage:
					urlList.append(images.get_serving_url(url))
					logging.info(images.get_serving_url(url))
				i = i + 1
		self.response.write(json.dumps({'url_list': urlList, 'start_page': startPage, 'end_page': endPage, 'stream_size': len(stream.imageURLs)}))


class UploadImage(webapp2.RequestHandler):
	def get(self):
		self.response.write('UploadImage')

	def post(self):
		#which takes a stream id and a file
		'''logging.info(self.request.POST.items())
		streamId = self.request.get('stream_id')
		image = self.request.get('image')
		result = cStream.query(cStream.streamId == int(streamId))
		stream = result.get()
		if stream:
			blobinfo = get_uploads(image)[0]
			stream.imageURLs.append(blobinfo.key())'''
		results = []
		blob_keys = []
		for name, fieldStorage in self.request.POST.items():
			if type(fieldStorage) is unicode:
				continue
			result = {}
			result['name'] = re.sub(r'^.*\\','',fieldStorage.filename)
			result['type'] = fieldStorage.type
			blob = files.blobstore.create(mime_type=result['type'],_blobinfo_uploaded_filename=result['name'])
			with files.open(blob, 'a') as f:
				f.write(fieldStorage.value)
			files.finalize(blob)
			blob_key = files.blobstore.get_blob_key(blob)
			blob_keys.append(blob_key)
			#use the images API to get a permanent serving URL if the file is an image
			results.append(result)
		streamId = self.request.get('stream_id')
		queryResult = cStream.query(cStream.streamId == int(streamId))
		stream = queryResult.get()
		for result in results:
			logging.info(result)
		if stream:
			for blobKey in blob_keys:
				stream.imageURLs.append(blobKey)
			stream.put()

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
			#logging.info(stream.streamTags)
			#logging.info(any(queryString in tag for tag in stream.streamTags))
			if queryString in stream.streamName or any(queryString in tag for tag in stream.streamTags):
				streamInfo.append({'stream_id': stream.streamId, stream.streamId: (stream.streamName, stream.coverImageURL)})
		self.response.write(json.dumps({'stream_list': streamInfo}))

class MostViewedStreams(webapp2.RequestHandler):
	def post(self):
		#which returns a list of streams sorted by recent access
		#frequency
		topStreams = getTopStreams()
		self.response.write(json.dumps({'sorted_streams': topStreams}))

	@staticmethod
	def getTopStreams():
		searchStreams = []
		topStreams = []
		for stream in cStream.query():
			searchStreams.append((stream.streamName, len(stream.viewTimes)))
		topStreams = sorted(searchStreams, key=lambda x: -x[1])
		return topStreams[:3]

class ReportRequest(webapp2.RequestHandler):
	reportRate = 5

	def get(self):
		logging.info("This is a report provided every %d minutes", ReportRequest.reportRate)
		cStream.updateStreamViews()
		topStreams = MostViewedStreams.getTopStreams()
		message = mail.EmailMessage(sender="Erik Schilling <erik.schilling@gmail.com>",
                            subject="Most Viewed Streams")

		message.to = "Erik Schilling <schilling.90@osu.edu>"
		message.body = """
		Dear Connexus User:
		Here are the most viewed streams of the last {0} minutes.
		
		{1}
		{2}
		{3}
		
		Please let us know if you have any questions.
		The Connexus Team
		""".format(ReportRequest.reportRate, topStreams[0][0], topStreams[1][0], topStreams[2][0])
		#message.send()

	def post(self):
		rate = int(self.request.get('report_rate'))
		logging.info(rate)
		if rate == 1:
			ReportRequest.reportRate = 60
		elif rate == 24:
			ReportRequest.reportRate = 1440
		else:
			ReportRequest.reportRate = 5
		logging.info(ReportRequest.reportRate)

'''class LoginUser(webapp2.RequestHandler):
	def post(self):
		userName = self.request.get('user_name')
		userId = cUser.getUserId(username)
		cUser.AddNewUser(userId, username)'''

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