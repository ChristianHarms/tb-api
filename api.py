import webapp2,logging
from google.appengine.api import users
from data import ApiKey, Geofancy
from baserequest import HelperGeofencyRequest

class ApiGeofency(HelperGeofencyRequest):

    def get(self, api_key):
        api_key_number = 0
        self.response.status = 204
        try:
            api_key_number = int(api_key)
        except ValueError:
            logging.warn('Got no int as api_key: {}'.format(api_key))
            return

        owner = ApiKey.getOwner(api_key_number)
        if not owner:
            logging.warn('No owner found for api-key: {}'.format(api_key_number))
            return

        params = [self.request.get(x) for x in ['name', 'entry', 'date', 'latitude', 'longitude', 'device']]
        logging.info(params)
        name, entry, event_date, lat, long, device = self.parseGeoParams(*params)
        if not name:
            logging.warn('No location name as param')
            return

        logging.info('API-request with: name: {}, entry:{}, date:{}, lat:{}, long:{}, device:{}'\
            .format(name, entry, event_date, lat, long, device ))
        self.saveGeoRequestParam(self.request, owner)

        self.response.status = 204
    #get
#ApiGeofence