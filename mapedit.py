import json, logging, os, urllib
from datetime import datetime, timedelta
from google.appengine.api import users
from google.appengine.ext import ndb
from baserequest import AuthorizedRequest, HelperGeofancyRequest, JINJA
from data import Geofency, Location

class MapEdit(AuthorizedRequest):
    def get(self):
        geofancy = Geofency.getSortedByLocation(self.user.user_id())
        locations = Location.getAllLocations(self.user.user_id())
        data = {'username': self.user.nickname(),
                'geofancy': map(lambda x:x.to_dict(), geofancy),
                'locations': map(lambda x:x.to_dict(), locations)}

        template = JINJA.get_template('mapedit.html')
        self.response.write(template.render(data))
    # get
    def post(self):
        if self.request.get('name') and self.request.get('lat') and self.request.get('lng'):
            loc = Location(user_id = self.user.user_id(),
                           pos = ndb.GeoPt(self.request.get('lat'), self.request.get('lng')),
                           radius=100,
                           name=self.request.get('name'),
                           home=False,
                           work=False)
            loc.put()

            self.redirect('/mapedit')
    #post
#MapEdit