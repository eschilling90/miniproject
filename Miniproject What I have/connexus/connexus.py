
import os
import urllib
import json
import jinja2
import webapp2
import logging
import urllib
import urllib2
from google.appengine.api import urlfetch
import time

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images

Main_URl = "http://localhost:9080/"

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class LoginUser(webapp2.RequestHandler):
	def get(self):
		logging.error('Starting Main handler')
		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render())

	def post(self):
		username = self.request.get('username')
		url_to_fetch = Main_URl + "loginuser?username=" + username;
		result = urlfetch.fetch(url_to_fetch,method = urlfetch.POST)
		self.redirect('/manage?username=' + username)


class ManagePage(webapp2.RequestHandler):
	def get(self):

		username = self.request.get('username')
		template = JINJA_ENVIRONMENT.get_template('manage.html')
		self.response.write(template.render({'welcome':'Welcome, ' + username}))

		href_html = '<fieldset class = HeaderFieldset>'+ '<img src="assets/images/Connexus.png" width="200"/> <a class="header1"> Manage</a> <a href = "/create?username='+username +"\"" +' class="header2"> Create</a>'
		href_html = href_html + '<a href = "/viewAllStreams?username='+username +"\"" +' class="header3"> View</a>'
		href_html = href_html + '<a href = "/search?username='+username +"\"" +' class="header4"> Search</a>'
		href_html = href_html + '<a href = "/trending?username='+username +"\"" + 'class="header5"> Trending</a>'
		href_html = href_html + '<a href = "/social?username='+username +"\"" + 'class="header6"> Social</a></fieldset>'

		self.response.write(href_html)

		url_to_access =Main_URl + "management?username=" + username
		result = urlfetch.fetch(url_to_access,method = urlfetch.POST)

		userStreams  =[]
		userSubbedStreams =[]		

		if result:
			userStreams = json.loads(result.content)['user_stream_list']
			userSubbedStreams = json.loads(result.content)['subbed_stream_list']

		else:
			logging.error("Did not Fetch URl")
		

		userStreams_html = """\
		<form action="/delete" method = "GET">
		<input name="username" type="hidden" id = "username" value = \"""" + username +"\"</input>""" + """

		<fieldset class="StreamsIOwn">
		<label> Streams I Own </label>
		<table>
  		<tr>
    		<td>Name</td>
    		<td>Last New Picture</td> 
    		<td>Number of Pictures</td>
    		<td>Delete</td>
  		</tr>
		"""

		for i in range(len(userStreams)):
			userStreams_html = userStreams_html + "<tr>"+  "<td>"+ "<a href=\"/viewStream?username=" + username +"&start_page=0&end_page=3&streamId=" + str(userStreams[i]['streamId'])+"\"" + ">"+ userStreams[i]['streamName']+ "</a>" + "</td>"  + "<td>" + str(userStreams[i]['lastPicture']) + "</td>" + "<td>" + str(userStreams[i]['numberOfPictures']) + "</td>"  + "<td><input type=\"checkbox\" id = \"check" + str(userStreams[i]["streamId"]) +"\""+ "name=\"check" + str(userStreams[i]["streamId"]) +"\"" + ">" + "</td>" + "<td>" + "<input id=\"streamid" +str(userStreams[i]["streamId"]) +"\"" + "value=\"" + str(userStreams[i]["streamId"]) + "\"" + "type=\"hidden\">" + "</td>" + "<tr>" 

		userStreams_html = userStreams_html + """</table> <button id="delete">Delete Checked</button></fieldset></form>"""

		if (len(userStreams) == 0):
			userStreams_html = """
			<fieldset class="StreamsIOwn">
			<label> Streams I Own </label>
			<br>
			<br>
			<label> You don't Own any streams at this time </label></fieldset>"""

		self.response.write(userStreams_html)


		#Subsribed channels

		userSubbedStreams_html = """\
								<form action="/unsubscribe" method = "GET">
								<input name="username" type="hidden" id = "username" value = \"""" + username +"\"</input>""" + """<fieldset class="StreamsISubscribeTo">
									<label> Streams I Subscribe to </label>
									<table>
  									<tr>
    									<td>Name</td>
    									<td>Last New Picture</td> 
    									<td>Number of Pictures</td>
    									<td>Views</td>
    									<td>Unsubscribe</td>
  									</tr>"""

		for i in range (len(userSubbedStreams)):
			userSubbedStreams_html = userSubbedStreams_html + "<tr>"+  "<td>"+ "<a href=\"/viewStream?username=" + username +"&start_page=0&end_page=3&streamId=" + str(userSubbedStreams[i]['streamId'])+"\"" + ">"+ userSubbedStreams[i]['streamName']+ "</a>" + "</td>"  + "<td>" + str(userSubbedStreams[i]['lastPicture']) + "</td>" + "<td>" + str(userSubbedStreams[i]['numberOfPictures']) + "</td>" + "<td>" + str(userSubbedStreams[i]['totalViews']) + "</td>"  + "<td><input type=\"checkbox\" id = \"check" + str(userSubbedStreams[i]["streamId"]) +"\""+ "name=\"check" + str(userSubbedStreams[i]["streamId"]) +"\"" + ">" + "</td>" + "<td>" + "<input id=\"streamid" +str(userSubbedStreams[i]["streamId"]) +"\"" + "value=\"" + str(userSubbedStreams[i]["streamId"]) + "\"" + "type=\"hidden\">" + "</td>" + "<tr>" 

		userSubbedStreams_html = userSubbedStreams_html + """</table> <button id="unsubscribe">Unsubscribe Checked</button></fieldset>"""

		if (len(userSubbedStreams) ==0):
			userSubbedStreams_html = """ <fieldset class="StreamsISubscribeTo">
									<label> Streams I Subscribe to </label>
									<br>
									<br>
									<label> You are not Subscribed to any Streams at this time"""
		self.response.write(userSubbedStreams_html)



class CreateStream(webapp2.RequestHandler):
	def get(self):

		username = self.request.get('username')
		create_html = '<body bgcolor="#FFFFFF" onload="InsertUsername()">  <fieldset class = HeaderFieldset>'+ '<img src="assets/images/Connexus.png" width="200"/> <a href = "/manage?username='+username +"\"" +'class="header1"> Manage</a> <a class="header2"> Create</a>'
		create_html = create_html + '<a href = "/viewAllStreams?username='+username +"\"" +' class="header3"> View</a>'
		create_html = create_html + '<a href = "/search?username='+username +"\"" +' class="header4"> Search</a>'
		create_html = create_html + '<a href = "/trending?username='+username +"\"" + 'class="header5"> Trending</a>'
		create_html = create_html + '<a href = "/social?username='+username +"\"" + 'class="header6"> Social</a></fieldset>'
		self.response.write(create_html )
		template = JINJA_ENVIRONMENT.get_template('create.html')
		self.response.write(template.render())


	def post(self):

		username = self.request.get('username')
		stream_name = self.request.get('streamName')
		subscribers = self.request.get('subscribers')
		message = self.request.get('message')
		tags = self.request.get('tags')
		cover_image = self.request.get('coverImageUrl')

		url_to_fetch = Main_URl + "createStream?"
		query_params = {'stream_name': stream_name, 'username':username, 'new_subscriber_list': subscribers,'message':message, 'stream_tags':tags,'url_cover_image':cover_image}
		result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
		time.sleep(3)
		self.response.write(url_to_fetch + urllib.urlencode(query_params))
		self.redirect('/manage?username='+username)


class DeleteStream(webapp2.RequestHandler):
	def get(self):
		username = self.request.get('username');
		streamIds =[]
		params = self.request.arguments()
		

		for i in range (0,len(params)):
			parameter = params[i]
			if(parameter.find("check") != -1):
				streamId = parameter.replace("check","")
				streamIds.append(streamId)

		query_params = {}
		for i in range(len(streamIds)):
			query_params.update({'stream'+str(i+1) : streamIds[i]})

		self.response.write(streamIds[0])
		url_to_fetch = Main_URl + "deleteStream?"
		result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
		time.sleep(3)
		self.redirect('/manage?username='+username)


class ViewStream(webapp2.RequestHandler):
	def get(self):


		username = self.request.get('username')
		href_html = '<fieldset class = HeaderFieldset>'+ '<img src="assets/images/Connexus.png" width="200"/> <a href = "/manage?username='+username +"\"" +' class="header1"> Manage</a> <a href = "/create?username='+username +"\"" +' class="header2"> Create</a>'
		href_html = href_html + '<a href = "/viewAllStreams?username='+username +"\"" +' class="header3"> View</a>'
		href_html = href_html + '<a href = "/search?username='+username +"\"" +' class="header4"> Search</a>'
		href_html = href_html + '<a href = "/trending?username='+username +"\"" + 'class="header5"> Trending</a>'
		href_html = href_html + '<a href = "/social?username='+username +"\"" + 'class="header6"> Social</a></fieldset>'

		self.response.write(href_html)

				#Displaying the images
		template = JINJA_ENVIRONMENT.get_template('viewStream.html')
		self.response.write(template.render())
		streamId = self.request.get('streamId')
		
		startPage = int(self.request.get('start_page'))
		endPage = self.request.get('end_page')
		imageURLs=[]
		url_to_fetch = Main_URl + "viewstream?streamId=" + str(streamId) + "&start_page="+str(startPage) + "&end_page=" + str(endPage)
		result = urlfetch.fetch(url_to_fetch,method = urlfetch.POST)
		blobKeyList = json.loads(result.content)['blob_key_list']

		for i in range(0,len(blobKeyList)):
			imageURLs.append(images.get_serving_url(blobKeyList[i]))


		if (len(imageURLs)==0 and startPage!=0):
			self.redirect('/viewStream?username=' + username + '&streamId=' + streamId + '&start_page=0&end_page=3')

		#Display Images HTML
		view_stream_html = '<fieldset class = "ImagesDisplay">'

		for i in range(0,len(imageURLs)):
			view_stream_html = view_stream_html + " <img src=\"" + imageURLs[i] + "\"" +"""style="width:304px;height:228px">"""

		view_stream_html = view_stream_html + '</fieldset>'
		
		#check if Stream is empty
		if (len(imageURLs) ==0 and startPage==0):
			view_stream_html = '<label class="noImagesInfo"> The stream is currently empty. Please upload images to the Stream</label>'

		self.response.write(view_stream_html)
		#End of Display Images
		
		#More images functionality
		nextStartPage = str(int(startPage) + 3)
		nextEndPage = str(int(endPage) +3)
		more_images_html = '<input class="moreImages" type="submit" value="More Images" onClick=moreImages('+'\''+username+'\''+","+'\''+streamId+'\''+","+'\''+nextStartPage+'\''+","+'\''+nextEndPage+'\''+');>'
		if(len(imageURLs) != 0):
			self.response.write(more_images_html)


		#Requesting to upload image
		upload_url = blobstore.create_upload_url('/upload?streamId='+streamId+"&username=" + username)

		self.response.out.write('<html><body>')
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write('<fieldset class = "uploadImage">')
		self.response.out.write("""<br><br><input class = "chooseFile" type ="file" name="file"><br>
			<textarea class ="commentsField" type="text" name="comments" id ="comments" placeholder="Add Comments" rows="4" cols="40"></textarea>
			 <input class ="uploadButton" type="submit" name="submit" value="Upload"> 
			 </fieldset> 
			 <br>
			 <br>
			 <br>
			 </form></body></html>""")


		#Subscribe to stream
		subsribe_html = '<input class ="subscribeButton" type="submit" name="Subscribe" value="Subscribe" onClick=subscribe('+'\''+username+'\''+","+'\''+streamId +'\''+');><p></p>'
		self.response.write(subsribe_html)



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
		upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
		blob_info = upload_files[0]
		streamId = self.request.get('streamId')
		username = self.request.get('username')
		url_to_fetch = Main_URl + "uploadimage?"
		query_params = {}
		query_params.update({'streamId':streamId,'BlobKey':blob_info.key()})
		result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
		time.sleep(2)
		self.redirect(str('viewStream?username='+username+"&streamId="+streamId + "&end_page=3&start_page=0"))

class SubscribeStream(webapp2.RequestHandler):
	def get(self):
		username = self.request.get('username')
		streamId = self.request.get('streamId')

		url_to_fetch = Main_URl + "subscribe?"
		query_params = {}
		query_params.update({'username':username,'streamId':streamId})
		result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
		#self.response.write(url_to_fetch + urllib.urlencode(query_params))
		time.sleep(2)
		self.redirect(str('viewStream?username='+username+"&streamId="+streamId + "&end_page=3&start_page=0"))


class UnSubscribeStream(webapp2.RequestHandler):
	def get(self):
		username = self.request.get('username');
		streamIds =[]
		params = self.request.arguments()
		
		for i in range (0,len(params)):
			parameter = params[i]
			if(parameter.find("check") != -1):
				streamId = parameter.replace("check","")
				streamIds.append(streamId)

		query_params = {}
		query_params.update({'username':username})
		for i in range(len(streamIds)):
			query_params.update({'stream'+str(int(i)+1) : streamIds[i]})

		url_to_fetch = Main_URl + "unsubscribe?"
		result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
		time.sleep(3)
		self.redirect('/manage?username='+username)

class ViewAllStreams(webapp2.RequestHandler):
	def get(self):
		self.response.write("")

		username = self.request.get('username')
		startPage = 0
		endPage = 3
		template = JINJA_ENVIRONMENT.get_template('viewAll.html')
		self.response.write(template.render())

		viewAllStreams_html = '<body bgcolor="#FFFFFF"><fieldset class="HeaderFieldset"><img src="assets/images/Connexus.png" width="200"/>'
		viewAllStreams_html = viewAllStreams_html  +  '<a href = "/manage?username='+username+"\""+ ' class="header1"> Manage</a> <a href = "/create?username='+username +"\"" +' class="header2"> Create</a>'
		viewAllStreams_html = viewAllStreams_html + '<a class="header3"> View</a>'
		viewAllStreams_html = viewAllStreams_html + '<a href = "/search?username='+username +"\"" +' class="header4"> Search</a>'
		viewAllStreams_html = viewAllStreams_html + '<a href = "/trending?username='+username +"\"" +' class="header5"> Trending</a>'
		viewAllStreams_html = viewAllStreams_html + '<a href = "/social?username='+username +"\"" +' class="header6"> Social</a></fieldset>'

		viewAllStreams_html = viewAllStreams_html + '<fieldset class="AllStreamsDisplay">'

		url_to_fetch = Main_URl + "viewAllStreams?"
		result = urlfetch.fetch(url_to_fetch,method = urlfetch.POST)

		streamInfo = json.loads(result.content)['stream_list']
		streamsIds = []

		for i in range(len(streamInfo)):
			streamsIds.append(streamInfo[i]['stream_id'])

		streamsIds.sort(reverse=True)

		for i in range(len(streamsIds)):
			streamId = streamsIds[i]
			index = 0
			for j in range(len(streamInfo)):
				if (streamInfo[j]['stream_id']==streamId):
					index = j

			stream_name = streamInfo[index][str(streamId)][0]
			stream_cover_url =streamInfo[index][str(streamId)][1]
			viewAllStreams_html = viewAllStreams_html + '<input style="background:url(' + stream_cover_url +'); background-size: 100% 100%; " class="streamButton" type="submit" value ="' +stream_name +'"  onClick=viewSingleStream('+'\''+username+'\''+","+'\''+str(streamId)+'\''+","+'\''+str(startPage)+'\''+","+'\''+str(endPage)+'\''+');>'




		viewAllStreams_html = viewAllStreams_html + '</fieldset>'
		self.response.write(viewAllStreams_html)


class SearchStream (webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('search.html')
		self.response.write(template.render())

		username = self.request.get('username')
		searchQuery = self.request.get('query_string')
		startPage =0
		endPage =3

		search_html = '<body bgcolor="#FFFFFF"><fieldset class="HeaderFieldset"><img src="assets/images/Connexus.png" width="200"/>'
		search_html = search_html  +  '<a href = "/manage?username='+username+"\""+ ' class="header1"> Manage</a> <a href = "/create?username='+username +"\"" +' class="header2"> Create</a>'
		search_html = search_html + '<a href = "/viewAllStreams?username='+username +"\"" + ' class="header3"> View</a>'
		search_html = search_html + '<a class="header4"> Search</a>'
		search_html = search_html + '<a href = "/trending?username='+username +"\"" +'class="header5"> Trending</a>'
		search_html = search_html + '<a href = "/social?username='+username +"\"" +'class="header6"> Social</a></fieldset>'
		search_html = search_html + '<input class="SearchBar" id ="query_string" type="text" name ="query_string" placeholder="Search" required>'
		search_html = search_html + '<input class="SearchButton" type="submit" value = "Search" onClick=Search('+'\''+username+'\''+');>'

		if searchQuery:
			search_html = search_html + '<fieldset class = "AllStreamsDisplay">'
			url_to_fetch = Main_URl + "search?"
			query_params={}
			query_params.update({'username':username,'query_string':searchQuery})
			result = urlfetch.fetch(url_to_fetch + urllib.urlencode(query_params),method=urlfetch.POST)
			streamInfo = json.loads(result.content)['stream_list']
			
			if (len(streamInfo)!=0):

				for i in range(len(streamInfo)):
					streamId = streamInfo[i]['stream_id']
					stream_name = streamInfo[i][str(streamId)][0]
					stream_cover_url = streamInfo[i][str(streamId)][1]
					search_html = search_html + '<input style="background:url(' + stream_cover_url +'); background-size: 100% 100%; " class="streamButton" type="submit" value ="' +stream_name +'"  onClick=viewSingleStream('+'\''+username+'\''+","+'\''+str(streamId)+'\''+","+'\''+str(startPage)+'\''+","+'\''+str(endPage)+'\''+');>'
				search_html = search_html + '</fieldset>'

			else:
				search_html = search_html + '<label class = "NoResult"> Your Search Returned no Results </label>'

		else:
			search_html = search_html + '<label class = "NoResult"> Please enter a Search Query</label>'

		
		self.response.write(search_html)



class TrendingStreams(webapp2.RequestHandler):
	def get(self):

		
		username = self.request.get('username')
		time = self.request.get('time')
		#self.response.write(username)
		template = JINJA_ENVIRONMENT.get_template('trending.html')
		self.response.write(template.render())

		startPage = 0
		endPage =3

		href_html = '<body bgcolor="#FFFFFF" onload="selectRadio(' + '\''+ time + '\');' + '"><fieldset class="HeaderFieldset"><img src="assets/images/Connexus.png" width="200"/>'
		href_html = href_html  +  '<a href = "/manage?username='+username+"\""+ ' class="header1"> Manage</a> <a href = "/create?username='+username +"\"" +' class="header2"> Create</a>'
		href_html = href_html + '<a href = "/viewAllStreams?username='+username +"\"" + ' class="header3"> View</a>'
		href_html = href_html + '<a href = "/search?username='+username +"\"" + 'class="header4"> Search</a>'
		href_html = href_html + '<a class="header5"> Trending</a>'
		href_html = href_html + '<a href = "/social?username='+username +"\"" +'class="header6"> Social</a></fieldset>'
		self.response.write(href_html)

		url_to_fetch = Main_URl + "getTrending"
		result = urlfetch.fetch(url_to_fetch, method = urlfetch.POST)
		streamInfo = json.loads(result.content)['stream_list']
		top_streams = []
		for i in range(len(streamInfo)):
			streamId = streamInfo[i]['stream_id']
			stream = streamInfo[i][str(streamId)]
			stream.append(int(streamId))
			top_streams.append(stream)
			
			
		top_streams = sorted(top_streams, key=lambda x: -x[1])
		#self.response.write(streamInfo)

		trending_url = '''<fieldset class = "AllStreamsDisplay">'''

		for i in range(len(top_streams)):
			trending_url = trending_url + '<input style="background:url(' + top_streams[i][2] +'); background-size: 100% 100%; " class="streamButton" type="submit" value ="' +top_streams[i][0] +'"  onClick=viewSingleStream('+'\''+username+'\''+","+'\''+str(top_streams[i][3])+'\''+","+'\''+str(startPage)+'\''+","+'\''+str(endPage)+'\''+');>'

		if (len(top_streams) == 0):
			trending_url = '<label class="NoTrending"> No Streams are Trending at the Moment</label>'

		self.response.write(trending_url)

		update_html = ""

		update_html = update_html + '</fieldset>'
		update_html = update_html +' <form action=""> <input type="hidden" name="username" value="' + username + '">'
		update_html = update_html + '''<input id = "rd1" type="radio" name="time" class="RadioButton1" value="0"><label class="Label1"> No Rep </label><br>
		<input type="radio" id = "rd2" name="time" class="RadioButton2"  value="5"><label class="Label2" value="5"> 5 min </label><br>
		<input type="radio" id = "rd3" name="time" class="RadioButton3" value="1"><label class="Label3" value="1"> 1 hour </label><br>
		<input type="radio" id = "rd4" name="time" class="RadioButton4" value="24"><label class="Label4" value="24"> 24 hours </label><br>
		<input type = "submit" class = "UpdateButton" value ="Update">
		</form>'''

		self.response.write(update_html)

		if time:
			url_to_fetch = Main_URl + "updateEmailPreference?time=" + time+"&username=" + username
			result = urlfetch.fetch(url_to_fetch,method=urlfetch.POST)




application = webapp2.WSGIApplication([
    ('/', LoginUser),
    ('/manage', ManagePage),
    ('/create', CreateStream),
    ('/delete',DeleteStream),
    ('/upload',UploadHandler),
    ('/subscribe',SubscribeStream),
    ('/unsubscribe',UnSubscribeStream),
    ('/viewStream',ViewStream),
    ('/viewAllStreams', ViewAllStreams),
    ('/trending',TrendingStreams),
    ('/search',SearchStream)

], debug=True)



