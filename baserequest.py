import webapp2, logging, jinja2, os, logging
from datetime import datetime, timedelta

from google.appengine.api import users
from google.appengine.ext import ndb
from data import Geofency, MyDevice, ApiKey

#config something for templating engine
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
    autoescape=True)
JINJA.install_null_translations()

def datetimeformat(value, format='%d.%m.%Y %H:%M'):
    logging.error('DATETIMEFORMAT: <%s>' % value)
    return value.strftime(format)
JINJA.filters['datetimeformat'] = datetimeformat

def timeformat(value, format='%H:%M'):
    logging.error('TIMEFORMAT: <%s>' % value)
    return value.strftime(format)
JINJA.filters['timeformat'] = timeformat

def deltaformat(value, format='%H:%M'):
    logging.info('DELTAFORMAT: <%s>'%value)
    logging.info('DELTAFORMAT type: <%s>'%type(value))
    total = value.total_seconds()
    hours, remainder = divmod(total,60*60)
    minutes, seconds = divmod(remainder, 60)
    return "%02d:%02d" % (hours, minutes)
JINJA.filters['deltaformat'] = deltaformat

class FAKEUSER():
    def nickname(self):
        return 'Peter'
    def user_id(self):
        return '42'
#FAKEUSER

class HelperGeofancyRequest(webapp2.RequestHandler):
    '''Inherit this if you want to parse/save geofancy call
    '''
    def parseGeoParams(self, name, entry, event, lat, long, device):
        try:
            entry = int(entry)
        except:
            entry = 0

        #parse ISO-Date-String or return now()
        try:
            event = datetime.strptime(event, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            logging.warn('param date with invalid format: %s' % event)
            try:
                event = datetime.strptime(event, '%Y-%m-%dT%H:%M')
            except ValueError:
                logging.warn('param date with invalid format: %s' % event)
                event = datetime.now()

        #parse floating value for lat
        try:
            lat = float(lat)
        except:
            logging.warn('No parseable latitide: "%s"' % lat)
            lat = 0

        #parse floating value for long
        try:
            long = float(long)
        except:
            logging.warn('No parseable longitude: "%s"' % long)
            long = 0

        return name, entry, event, lat, long, device
    #parseGeoParams

    def saveGeoRequestParam(self, request, user_id):
        params = [request.get(x) for x in ['name', 'entry', 'date', 'latitude', 'longitude', 'device']]
        name, entry, eventDate, lat, long, device = self.parseGeoParams(*params)
        #save event
        newGeo = Geofency(user_id = user_id, name=name, entry=entry % 2,
                          event=eventDate, pos=ndb.GeoPt(lat, long), device=device)
        newGeo.put()
        #save second event as LEAVE and 1 hour later
        if entry==2:
            newGeo = Geofency(user_id = user_id, name=name, entry=1,
                              event=eventDate+timedelta(hours=1), pos=ndb.GeoPt(lat, long), device=device)
            newGeo.put()
            #saveGeo
#HelperGeofencyRequest


class AuthorizedRequest(webapp2.RequestHandler):
    '''inherit this if the request shold be authorized.
    '''
    def __init__(self, request, response):
        self.user = None
        super(AuthorizedRequest, self).__init__(request, response)

    def dispatch(self):
        'every request should have the user scope'
        self.user = users.get_current_user()
        if self.request.headers.get('User-Agent').find('curl')!=-1:
            self.user = FAKEUSER()
            logging.info('Dispatch - fakeuser')

        if self.user:
            super(AuthorizedRequest, self).dispatch()
        else:
            logging.info('Redir to / because it"s for not-logged-in')
            self.redirect('/')
#AuthorizedPage
