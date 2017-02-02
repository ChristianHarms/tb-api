import webapp2, logging, datetime
from google.appengine.api import users
from data import ApiKey, Geofency
from baserequest import HelperGeofancyRequest

class ApiGeofancy(HelperGeofancyRequest):

    def get(self, api_key):
        api_key_number = 0
        self.response.status = 200
        try:
            api_key_number = int(api_key)
        except ValueError:
            logging.warn('Got no int as api_key: {}'.format(api_key))
            return

        owner_id = ApiKey.getOwnerId(api_key_number)
        if not owner_id:
            logging.warn('No owner found for api-key: {}'.format(api_key_number))
            return

        params = [self.request.get(x) for x in ['name', 'entry', 'date', 'latitude', 'longitude', 'device']]
        logging.info(params)
        name, entry, event_date, lat, long, device = self.parseGeoParams(*params)
        if not name:
            logging.warn('No location name as param')
            return

        #logging below 60 sec with same entry/name will be ignored.
        last = Geofency.getSortedByTime(user_id = owner_id, max=1)
        if last and len(last)>0:
            delta =
            if last[0].event - event_date < datetime.timedelta(60) and \
                    (name==last[0].name or entry == last[0].entry):
                logging.info('Ignore name:%s, entry: %s, time to last: %s' % (
                    name, entry, last[0].event - event_date))
                return

        logging.info('API-request with: name: {}, entry:{}, date:{}, lat:{}, long:{}, device:{}'\
            .format(name, entry, event_date, lat, long, device ))
        self.saveGeoRequestParam(self.request, owner_id)
    #get
#ApiGeofence