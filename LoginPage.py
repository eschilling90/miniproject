import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import connexus
import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class LoginPage(webapp2.RequestHandler):

    def get(self):
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        connexus.addNewUser(3, "user3")
        userList, t = connexus.getUserStreams("user3")
        template_values = {
            'users': t + userList,
            'url_linktext': connexus.userCount()
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def adduser(self):
        connexus.addNewUser(connexus.getNewUserId(), "user" + str(connexus.getNewUserId()))

application = webapp2.WSGIApplication([
    ('/', LoginPage),
], debug=True)