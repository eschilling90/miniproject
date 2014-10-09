import webapp2
import json
import urllib
import logging
import time
import datetime

from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

from ConnexusUser import User as cUser
from ConnexusStream import Stream as cStream
from ConnexusTopStreams import topStream as tStream


class LoginUser(webapp2.RequestHandler):
	def get(self):
		self.response.write('LoginUser')

	def post(self):
		statusCode=0
		username = self.request.get('username')
		user = cUser.query(cUser.username == username).get()
		if not user:
			newUser = cUser(username = username,emailPreference=0)
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
				if len(stream.viewTimes) !=0:
					returnStream.append({'streamId': stream.streamId, 'streamName': stream.streamName,'lastPicture': str(stream.viewTimes[0]),'numberOfPictures':len(stream.imageURLs),'totalViews':stream.totalViews})
				else:
					returnStream.append({'streamId': stream.streamId, 'streamName': stream.streamName,'lastPicture':"Empty",'numberOfPictures':len(stream.imageURLs),'totalViews':stream.totalViews})
		return returnStream


class CreateStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('CreateStream')

	def post(self):
		#which takes a stream definition and returns a status code
		statusCode = 0
		username = self.request.get('username')
		streamName = self.request.get('stream_name')
		sId = cStream.getStreamId(streamName)
		newSubscribers = self.request.get('new_subscriber_list')
		comment = self.request.get('message')
		newSubscribers = newSubscribers.split(',')
		urlCoverImage = self.request.get('url_cover_image')
		streamTags = self.request.get('stream_tags')
		streamTagsList = streamTags.split('#')
		streamTagsList.pop(0)

		streamList = []
		for stream in cStream.query():
			if stream.streamId == sId:
				statusCode = 1
			if stream.streamName == streamName:
				statusCode = 2
			streamList.append((stream.streamName, stream.creatorName))
		if statusCode == 0:
			streamKey = cStream.addNewStream(sId, streamName, username,urlCoverImage,streamTagsList)
			cUser.addUserStream(username, streamKey)
			CreateStream.addNewSubscribers(newSubscribers, streamKey)
			CreateStream.sendSubscriptionEmail(newSubscribers, streamName, username, comment)

		self.response.write(json.dumps({'status_code': statusCode, 'streams': streamList,}))

	@staticmethod
	def addNewSubscribers(subList, streamKey):
		for i in range(len(subList)):
			user = cUser.query(cUser.username == subList[i]).get()
			if user:
				user.subbedStreams.append(streamKey)
				user.put()

	@staticmethod
	def sendSubscriptionEmail(subList, streamname, creatorname, comment):
		for sub in subList:
			logging.error(sub)
			if (mail.is_email_valid(sub)):
				message = mail.EmailMessage(sender="erik.schilling@gmail.com",subject="Subscription Notice")
				logging.info('in if')
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
				message.send()


class DeleteStream(webapp2.RequestHandler):

	def get(self):
		self.response.write('Delete')

	def post(self):
		params = self.request.arguments()
		streamsIds = []
		for i in range(len(params)):
			streamsIds.append(self.request.get(params[i]))

		for i in range(len(streamsIds)):

			streamToDelete = cStream.query(cStream.streamId == int(streamsIds[i])).get()
			streamKeyToDelete = streamToDelete.key
			for user in cUser.query():
				if (streamKeyToDelete in user.subbedStreams):
					user.subbedStreams.remove(streamKeyToDelete)
					user.put()

			owner = cUser.query(cUser.username == streamToDelete.creatorName).get()
			owner.userStreams.remove(streamKeyToDelete)
			owner.put()
			cStream.deleteStream(int(streamsIds[i]))

			top_stream = tStream.query(tStream.streamId == int(streamsIds[i])).get()
			top_stream.key.delete()


class UnSubscribeStream(webapp2.RequestHandler):
	def post(self):
		username = self.request.get('username')
		streamsIds=[]

		params = self.request.arguments()
		for i in range(len(params)):
			if (params[i].find('stream') != -1):
				streamsIds.append(str(self.request.get(params[i])))

		self.response.write(streamsIds[0])

		for i in range(len(streamsIds)):
			streamToUnsubscribe = cStream.query(cStream.streamId ==int(streamsIds[i])).get()
			if streamToUnsubscribe:
				streamKey = streamToUnsubscribe.key
				user = cUser.query(cUser.username == username).get()
				if user:
					user.subbedStreams.remove(streamKey)
					user.put()


class ViewStream(webapp2.RequestHandler):
	def get(self):
		self.response.write('ViewStream')

	def post(self):
		#which takes a stream id and a page range and returns a
		#list of URLs to images, and a page range
		streamId = self.request.get('streamId')
		startPage = int(self.request.get('start_page'))
		endPage = int(self.request.get('end_page'))
		BlobKeyList = []
		result = cStream.query(cStream.streamId == int(streamId))
		stream = result.get()
		logging.info("in viewstream")

		if stream:
			i = 0
			cStream.addViewToStream(int(streamId))
			for x in range(0,len(stream.imageURLs)):
				if i >= startPage and i < endPage:
					BlobKeyList.append((str(stream.imageURLs[x])))
					logging.info(images.get_serving_url(stream.imageURLs[x]))
				i = i + 1
		self.response.write(json.dumps({'blob_key_list': BlobKeyList, 'start_page': startPage, 'end_page': endPage, 'stream_size': len(stream.imageURLs)}))

class UploadImage(webapp2.RequestHandler):
	def post(self):
		streamId = self.request.get('streamId')
		BlobKey = blobstore.BlobKey(str(self.request.get('BlobKey')))

		stream = cStream.query(cStream.streamId == int(streamId)).get()
		if stream:
			stream.imageURLs.insert(0,BlobKey)
			stream.put()

class getStream(webapp2.RequestHandler):
	def get(self):
		username="elieantoun@outlook.com"
		user = cUser.query(cUser.username == username).get()
		self.response.write(user.emailPreference)

class SubsribeStream(webapp2.RequestHandler):
	def post(self):
		streamId = self.request.get('streamId')
		username = self.request.get('username')

		stream = cStream.query(cStream.streamId == int(streamId)).get()
		if stream:
			user = cUser.query(cUser.username == username).get()
			if user:
				if stream.key not in user.subbedStreams:
					user.subbedStreams.append(stream.key)
					user.put()

class ViewStreams(webapp2.RequestHandler):
	def get(self):
		self.response.write('ViewStreams')

	def post(self):
		streamInfo = []
		for stream in cStream.query():
			streamInfo.append({'stream_id': int(stream.streamId), stream.streamId: (stream.streamName, stream.coverImageURL)})
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
			if len(streamInfo) < 5 and queryString.lower() in stream.streamName.lower() or any(queryString.lower() in tag.lower() for tag in stream.streamTags):
				streamInfo.append({'stream_id': stream.streamId, stream.streamId: (stream.streamName, stream.coverImageURL)})
		self.response.write(json.dumps({'stream_list': streamInfo}))

class TrendingStreams(webapp2.RequestHandler):
	def get(self):
		#which returns a list of streams sorted by recent access
		#frequency

		#Delete all topStreams
		for top in tStream.query():
			top.key.delete()

		#create new top Streams
		top_streams = TrendingStreams.getTopStreams()
		self.response.write(top_streams)
		for i in range(len(top_streams)):
			tStream.addTopStream(top_streams[i][2],top_streams[i][0],top_streams[i][3],top_streams[i][1])

	@staticmethod
	def getTopStreams():
		searchStreams = []
		top_streams = []
		cStream.updateStreamViews()
		for stream in cStream.query():
			searchStreams.append((stream.streamName, len(stream.viewTimes),stream.streamId,stream.coverImageURL))
		top_streams = sorted(searchStreams, key=lambda x: -x[1])
		return top_streams[:3]

class GetTrendingStreams(webapp2.RequestHandler):
	def get(self):
		self.response.write('test')
	def post(self):
		streamInfo = []
		for stream in tStream.query():
			streamInfo.append({'stream_id': stream.streamId, stream.streamId: (stream.streamName, stream.totalViews,stream.coverImageURL)})
		username = self.request.get('username')
		user = cUser.query(cUser.username == username).get()
		self.response.write(json.dumps({'stream_list': streamInfo, 'emailPreference': user.emailPreference}))

class UpdateEmailPreference(webapp2.RequestHandler):
	def post(self):

		time = self.request.get('time')
		username = self.request.get('username')
		user = cUser.query(cUser.username == username).get()
		if user:
			user.emailPreference = int(time)
			user.put()

class SendEmail5(webapp2.RequestHandler):
	def get(self):
		message_to_send = ""

		for stream in tStream.query():
			message_to_send = message_to_send + stream.streamName + " "
			

		for user in cUser.query(cUser.emailPreference ==5):
			if (mail.is_email_valid(user.username)):
				message = mail.EmailMessage(sender="erik.schilling@gmail.com",subject="Trending Streams")
				logging.info('in if')
				message.to = user.username
				message.body = """
				Dear Connexus User:
				The Following Streams are Trending: {0}
				""".format(message_to_send)
				message.body = message.body + """
				Please let us know if you have any questions.
				The Connexus Team
				"""
				message.send()

		instructorList = ["adnan.aziz@gmail.com", "ragha@utexas.edu", "natviv@cs.utexas.edu"]

class SendEmail1(webapp2.RequestHandler):
	def get(self):
		message_to_send = ""

		for stream in tStream.query():
			message_to_send = message_to_send + stream.streamName + " "
			

		for user in cUser.query(cUser.emailPreference ==1):
			if (mail.is_email_valid(user.username)):
				message = mail.EmailMessage(sender="erik.schilling@gmail.com",subject="Trending Streams")
				logging.info('in if')
				message.to = user.username
				message.body = """
				Dear Connexus User:
				The Following Streams are Trending: {0}
				""".format(message_to_send)
				message.body = message.body + """
				Please let us know if you have any questions.
				The Connexus Team
				"""
				message.send()

class SendEmail24(webapp2.RequestHandler):
	def get(self):
		message_to_send = ""

		for stream in tStream.query():
			message_to_send = message_to_send + stream.streamName + " "
			

		for user in cUser.query(cUser.emailPreference ==24):
			if (mail.is_email_valid(user.username)):
				message = mail.EmailMessage(sender="erik.schilling@gmail.com",subject="Trending Streams")
				logging.info('in if')
				message.to = user.username
				message.body = """
				Dear Connexus User:
				The Following Streams are Trending: {0}
				""".format(message_to_send)
				message.body = message.body + """
				Please let us know if you have any questions.
				The Connexus Team
				"""
				message.send()



application = webapp2.WSGIApplication([
	('/loginuser', LoginUser),
	('/management', Management),
	('/createStream',CreateStream),
	('/deleteStream',DeleteStream),
	('/uploadimage',UploadImage),
	('/getStream',getStream),
	('/subscribe',SubsribeStream),
	('/unsubscribe',UnSubscribeStream),
	('/viewstream', ViewStream),
	('/getTrending',GetTrendingStreams),
	('/storeTrending',TrendingStreams),
	('/viewAllStreams',ViewStreams),
	('/updateEmailPreference',UpdateEmailPreference),
	('/sendEmail5',SendEmail5),
	('/sendEmail1',SendEmail1),
	('/sendEmail24',SendEmail24),
	('/search',SearchStreams)
], debug = True)