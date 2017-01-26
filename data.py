# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import logging, random

API_KEY_MIN=10000
API_KEY_MAX=99999

class Booking(ndb.Model):
    user_id = ndb.StringProperty()
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
    hours = ndb.TimeProperty()
    pause = ndb.TimeProperty()
    name = ndb.StringProperty()

class ApiKey(ndb.Model):
    '''
    Each user has one API-Key.
    '''
    user_id = ndb.StringProperty()
    key = ndb.IntegerProperty()

    @classmethod
    def getApiKey(cls, user_id):
        '''
        Return the API-Key for this user - if nothing stored -> generate it.
        :param user_id:
        :return: the api-key-id
        '''
        keys = cls.query(ApiKey.user_id == str(user_id)).fetch()
        if len(keys) == 0:
            #read all keys and choose one unused
            usedKeys = set([x.key for x in cls.query().fetch()])
            newApiKey = ApiKey(user_id = str(user_id),
                               key = random.choice(filter(lambda x:x not in usedKeys,
                                                          xrange(API_KEY_MIN,API_KEY_MAX))))
            newApiKey.put()
            return newApiKey.key
        else:
            return keys[0].key
    #getApiKey

    @classmethod
    def getOwner(cls, api_key):
        '''
        Return the userId for the api_key
        :param api_key: the API-KEY id
        :return: the user_id
        '''
        keys = cls.query(ApiKey.key == api_key).fetch(1)
        if len(keys)==1:
            return keys[0].user_id
    #getOwner
#ApiKey

class Location(ndb.Model):
    '''Registrierte Orte
    '''
    user_id = ndb.StringProperty()
    pos = ndb.GeoPtProperty()
    radius = ndb.FloatProperty()
    name = ndb.StringProperty()
    home = ndb.BooleanProperty()
    work = ndb.BooleanProperty()

    @classmethod
    def getAllLocations(cls, user_id):
        '''
        Liefert alle registrierte Orts zurück.
        :param user_id:
        :return:
        '''
        locations = cls.query(Location.user_id == str(user_id)).fetch()
        return locations
    #getAllLocations
#Location

class MyDevice(ndb.Model):
    '''
    List of all devices with block-flag and readable name.
    '''
    user_id = ndb.StringProperty()
    device_id = ndb.StringProperty()
    name = ndb.StringProperty()
    blocked = ndb.BooleanProperty()

    @classmethod
    def getAllDevices(cls, user_id, deviceIdFromList=set()):
        devices = cls.query(MyDevice.user_id == str(user_id)).fetch()

        used_devices = Geofancy.query(projection=['device'], distinct=True).fetch()

        other_devices = list(set([dev.device for dev in used_devices]) -
                             set([dev.device_id for dev in devices]))
        logging.info(other_devices)
        #we have no saved devices and only one deviceId from list
        if len(devices)==0 and len(other_devices)==1:
            #store this one device_id as default smartphone
            defaultDevice = MyDevice(user_id=user_id,
                                     device_id=other_devices[0],
                                     name='SmartPhone',
                                     blocked=False)
            defaultDevice.put()
            devices = [defaultDevice]
        else:
            devices.extend([MyDevice(name="", device_id=x) for x in other_devices])

        return devices
    #getAllDevices
#MyDevices

class Geofancy(ndb.Model):
    user_id = ndb.StringProperty()
    name = ndb.StringProperty()
    entry = ndb.IntegerProperty()
    event = ndb.DateTimeProperty()
    pos = ndb.GeoPtProperty()
    device = ndb.StringProperty()

    @classmethod
    def getSortedByTime(cls, user_id, max=100):
        all_geo = cls.query(Geofancy.user_id == str(user_id)).order(cls.event).fetch(max)

        device_dict = dict([dev.device_id, dev.name] for dev in MyDevice.getAllDevices(user_id))
        for geo in all_geo:
            #replace all known geo.device entires with MyDevice.name
            geo.device = device_dict.get(geo.device, geo.device)
        return all_geo
    #getSortedByTime

    @classmethod
    def deleteByDeviceId(cls, user_id, device_id):
        qo = ndb.QueryOptions(keys_only = True)
        query = cls.query(Geofancy.user_id == str(user_id), Geofancy.device==device_id)
        keys = query.fetch(100, options = qo)
        logging.info('Found %d items to delete' % len(keys))
        logging.info(keys)
        ndb.delete_multi(keys)


    @classmethod
    def getAllDevices(cls, user_id, max=100):
        return cls.query(Geofancy.user_id == str(user_id), projection=['device']).fetch(max)
    #getAllDevices

    @classmethod
    def getSortedByLocation(cls, user_id):
        result = []
        for log in cls.query(Geofancy.user_id == str(user_id)).order(cls.event):
            result.append(log)
        return result


class TimeProject(ndb.Model):
    name = ndb.StringProperty()
