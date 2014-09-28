import webapp2
import json
import urllib
import logging
import re
import datetime

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
		if not cUser.query(cUser.username == "admin").get():
			LoginUser.createAdminUser()
		if not user:
			admin = cUser.query(cUser.username == "admin").get()
			globalReportRate = 5
			if admin:
				globalReportRate = admin.reportRate
			newUser = cUser(username = username, reportRate = globalReportRate)
			newUser.put()
			statusCode=1

		self.response.write(json.dumps({'status_code': statusCode}))

	@staticmethod
	def createAdminUser():
		admin = cUser(username = "admin", reportRate = 5, lastMessage = 0)
		logging.info("admin created")
		admin.put()


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
				returnStream.append({'streamId': stream.streamId,
					'streamName': stream.streamName,
					'lastUpload': stream.lastUpload,
					'streamSize': len(stream.imageURLs),
					'totalViews': stream.totalViews})
		logging.info(returnStream)
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
		streamTags = streamTagsUnparsed.split(",")
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
				message.body = message.body + """
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
		streamId = int(self.request.get('stream_id'))
		startPage = int(self.request.get('start_page'))
		endPage = int(self.request.get('end_page'))
		urlList = []
		result = cStream.query(cStream.streamId == int(streamId))
		stream = result.get()
		logging.info("in viewstream")
		streamsize = 0
		if stream:
			i = 0
			cStream.addViewToStream(streamId)
			for url in stream.imageURLs:
				logging.info(url)
				logging.info(url.__class__)
				if i >= startPage and i < endPage:
					urlList.append(images.get_serving_url(url))
					logging.info(images.get_serving_url(url))
				i = i + 1
			streamsize = len(stream.imageURLs)
		self.response.write(json.dumps({'url_list': urlList, 'start_page': startPage, 'end_page': endPage, 'stream_size': streamsize}))


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
		'''logging.info("Uploading Image")
		logging.info(self.request.body.__class__)
		logging.info(json.dumps(self.request.body))
		logging.info(json.loads(self.request.body))
		json_body = json.loads(self.request.body)
		logging.info(json_body['stream_id'])
		logging.info(json_body['file'].__class__)'''
		logging.info(self.request.POST.items())
		for name, fieldStorage in self.request.POST.items():
		#fieldStorage = re.split(': |\r\n|; ', json_body['file'])
			logging.info(fieldStorage)
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
		#end of for loop
		logging.info(self.request.arguments())
		logging.info("Before file")
		logging.info(self.request.get('file').__class__)
		logging.info("After file")
		streamId = self.request.get('stream_id')
		comment = self.request.get('comment') # what am I supposed to do with this? There is no comment displayed in the mockups
		queryResult = cStream.query(cStream.streamId == int(streamId))
		stream = queryResult.get()
		logging.info("Printing results %s", stream.streamName)
		for result in results:
			logging.info(result)
		if stream:
			for blobKey in blob_keys:
				stream.imageURLs.append(blobKey)
			if len(blob_keys) > 0:
				stream.lastUpload = str(datetime.date.today())
				logging.info(stream.lastUpload)
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
		queryString = queryString.lower()
		streamInfo = []
		for stream in cStream.query():
			#logging.info(stream.streamTags)
			#logging.info(any(queryString in tag for tag in stream.streamTags))
			if len(streamInfo) < 5 and queryString in stream.streamName.lower() or any(queryString in tag.lower() for tag in stream.streamTags):
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
		searchStreams = sorted(searchStreams, key=lambda x: -x[1])
		topStreams = searchStreams[:3]
		topStreams[0][0] = str(topStreams[0][0]) + " views in past " + ReportRequest.getDisplayRate(True)
		topStreams[1][0] = str(topStreams[1][0]) + " views in past " + ReportRequest.getDisplayRate(True)
		topStreams[2][0] = str(topStreams[2][0]) + " views in past " + ReportRequest.getDisplayRate(True)
		return topStreams

class ReportRequest(webapp2.RequestHandler):

	def get(self):
		reportRate = ReportRequest.getReportRate(True)
		rate = ReportRequest.getReportRate()
		logging.info("last %d", ReportRequest.getLastMessage())
		logging.info(rate)
		ReportRequest.setLastMessage(ReportRequest.getLastMessage() + 5)
		if ReportRequest.getLastMessage() >= rate and rate != 0:
			logging.info("This is a report provided every %s", reportRate)
			cStream.updateStreamViews()
			topStreams = MostViewedStreams.getTopStreams()
			message = mail.EmailMessage(sender="Erik Schilling <erik.schilling@gmail.com>",
	                            subject="Most Viewed Streams")

			message.body = """
			Dear Connexus User:
			Here are the most viewed streams of the last {0}.
			
			{1} : {2}
			{3} : {4}
			{5} : {6}
			
			Please let us know if you have any questions.
			The Connexus Team
			""".format(reportRate, topStreams[0][0], topStreams[0][1], topStreams[1][0], topStreams[1][1], topStreams[2][0], topStreams[2][1])
			recipients = ["Erik Schilling <schilling.90@osu.edu>"]
			for recipient in recipients:
				message.to = recipient
				#message.send()
			ReportRequest.setLastMessage(0)

	def post(self):
		rate = int(self.request.get('report_rate'))
		test = rate
		if rate == 1:
			ReportRequest.setReportRate(60)
		elif rate == 24:
			ReportRequest.setReportRate(1440)
		elif rate == 5:
			ReportRequest.setReportRate(5)
		else:
			ReportRequest.setReportRate(0)
		logging.info(ReportRequest.getReportRate())

	@staticmethod
	def getReportRate(display=False):
		user = cUser.query(cUser.username == "admin").get()
		if user:
			rate = user.reportRate
			if display:
				if rate == 5:
					return "5 minutes"
				if rate == 60:
					return "1 hour"
				if rate == 1440:
					return "24 hours"
				return rate
			else:
				return rate
		if display:
			return "5 minutes"
		return 5

	@staticmethod
	def getDisplayRate(display=False):
		rate = ReportRequest.getReportRate(display)
		if rate == 0:
			if display:
				return "5 minutes"
			return 5
		return rate

	@staticmethod
	def setReportRate(rate):
		admin = cUser.query(cUser.username == "admin").get()
		admin.reportRate = rate
		admin.put()

	@staticmethod
	def getLastMessage():
		admin = cUser.query(cUser.username == "admin").get()
		return admin.lastMessage

	@staticmethod
	def setLastMessage(time):
		admin = cUser.query(cUser.username == "admin").get()
		admin.lastMessage = time
		admin.put()

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