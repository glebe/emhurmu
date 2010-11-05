# -*- coding: UTF-8 -*-
import cgi
import datetime
import wsgiref.handlers
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '1.1')
from django import template

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template



#from google.appengine.ext.webapp.util import run_wsgi_app

class Eating(db.Model):
  author = db.UserProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            template_values = {
                'user': user,
                }
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
			
        else:
            self.redirect(users.create_login_url(self.request.uri))

class ListEaters(webapp.RequestHandler):
    def get(self):

        eaters_query = Eating.all().order('-date')
        eaters = eaters_query.fetch(10)
	
        template_values = {
            'eaters': eaters,
            }
	
        path = os.path.join(os.path.dirname(__file__), 'eaters.html')
        self.response.out.write(template.render(path, template_values))
	
class ListLeaders(webapp.RequestHandler):
    def get(self):

        top_eaters = Eating.all()
# collect stats on each author name
        stats = {}
        for eater in top_eaters:
            if eater.author in stats:
                stats[eater.author] += 1
            else:
                stats[eater.author] = 1

        template_values = {
            'top_eaters': stats,
            }

        path = os.path.join(os.path.dirname(__file__), 'leaders.html')
        self.response.out.write(template.render(path, template_values))


class Eat(webapp.RequestHandler):
  def post(self):
    eating = Eating()

    if users.get_current_user():
      eating.author = users.get_current_user()

    eating.put()
    self.redirect('/status')

class Logout(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.redirect(users.create_logout_url(self.request.uri))
        else:
            self.redirect('/')

application = webapp.WSGIApplication([
    ('/', MainPage),
    ('/status', ListEaters),
    ('/leaders', ListLeaders),
    ('/eat', Eat),
    ('/logout', Logout)],
    debug=True)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
