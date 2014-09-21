import os
import urllib
import json

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
	
class CreatePage(webapp2.RequestHandler):
    def post(self):
        str = "s"

    def get(self):
    	template_values = {}
    	template = JINJA_ENVIRONMENT.get_template('createIndex.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
	('/create', CreatePage),
], debug=True)