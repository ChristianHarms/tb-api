import webapp2, logging
from google.appengine.api import users
from dashboard import DashBoard, DashBoardConfig
from api import ApiGeofency

class MainPage(webapp2.RequestHandler):
    'HTML-view of all timeBooking'

    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/dashboard')
        else:
            login_url = users.create_login_url('/')
            greeting = 'You have to <a href="{}">sign in</a> to use this application'.format(login_url)

            self.response.write(
                '<html><body>{}</body></html>'.format(greeting))
    #get
#MainPage

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/dashboard', DashBoard),
    ('/config', DashBoardConfig),
    ('/api/(\d*)', ApiGeofency),
], debug=True)