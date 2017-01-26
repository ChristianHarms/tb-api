# -*- coding: utf-8 -*-
#
import json, logging, os, urllib
from datetime import datetime, timedelta
from google.appengine.api import users
from google.appengine.ext import ndb
from baserequest import AuthorizedRequest, HelperGeofencyRequest, JINJA
from data import Booking, Geofancy, MyDevice, ApiKey, Location

_IN = 0
_OUT = 1

CONFIG = [
    {  # Zwei CheckIns am gleichen Ort
        'EVENT_LAST': _IN, 'EVENT_NEXT': _IN, 'LOCATION_CHECK': True, 'ACTION': None},
    {  # Hier fehlt die OUT-Zeit von LAST!
        'EVENT_LAST': _IN, 'EVENT_NEXT': _IN, 'LOCATION_CHECK': False, 'ACTION': 'ADD'},
    {  #
        'EVENT_LAST': None, 'EVENT_NEXT': _IN, 'ACTION': 'ADD'},
    {  # CheckIn am gleichen Ort, wo vorher CheckOut war: PAUSE, wenn am gleichen Tag
        'EVENT_LAST': _OUT, 'EVENT_NEXT': _IN, 'LOCATION_CHECK': True, 'DATE_CHECK': True, 'ACTION': 'PAUSE'},
    {'EVENT_LAST': _OUT, 'EVENT_NEXT': _IN, 'LOCATION_CHECK': True, 'DATE_CHECK': False, 'ACTION': 'ADD'},
    {  # normales Logging zwischen zwei Orten
        'EVENT_LAST': _OUT, 'EVENT_NEXT': _IN, 'LOCATION_CHECK': False, 'ACTION': 'ADD'},
    {  # End-zeit übernehmen
        'EVENT_LAST': _IN, 'EVENT_NEXT': _OUT, 'LOCATION_CHECK': True, 'ACTION': 'ENDTIME'},
    {  # Am Ort A eingecheckt, am Ort B ausgecheckt -> Fehler
        'EVENT_LAST': _IN, 'EVENT_NEXT': _OUT, 'LOCATION_CHECK': False, 'ACTION': None},
    {  # am gleichen Ort zweimal ausgecheckt -> END-Zeit korrigieren
        'EVENT_LAST': _OUT, 'EVENT_NEXT': _OUT, 'LOCATION_CHECK': True, 'ACTION': 'ENDTIME'},
    {  # Hier fehlt die IN-zeit vom zweiten Ort
        'EVENT_LAST': _OUT, 'EVENT_NEXT': _OUT, 'LOCATION_CHECK': False, 'ACTION': 'ADD'},
    {  # Hier fehlt die IN-zeit vom Ort
        'EVENT_LAST': None, 'EVENT_NEXT': _OUT, 'ACTION': 'ADD'},
]


class DashBoard(AuthorizedRequest, HelperGeofencyRequest):
    def get(self):
        # read all logged geo event
        geofancy = Geofancy.getSortedByTime(self.user.user_id())
        timings = self.calculateTimes(geofancy)

        # read all registered devices
        devices = MyDevice.getAllDevices(user_id=self.user.user_id())

        locations = Location.getAllLocations(self.user.user_id())

        data = {'username': self.user.nickname(),
                'hostname': self.request.host,
                'geofency': geofancy,
                'timings': timings,
                'devices': devices,
                'locations': locations,
                'apikey': ApiKey.getApiKey(self.user.user_id()),
                'unregistered_devices': len(filter(lambda x: x.name == "", devices)),
                'registered_devices': len(filter(lambda x: x.name != "", devices)),
                'msg': self.request.get('msg')}

        template = JINJA.get_template('dashboard.html')
        self.response.write(template.render(data))

    # get

    def calculateTimes(self, geofancy):
        items = []
        work = None
        last = None
        for item in geofancy:
            action = None
            if last:
                logging.info('%s (%s) -> %s (%s)' % (last.entry, last.name, item.entry, item.name))
            for cfg in CONFIG:
                if last:
                    if last.entry == cfg['EVENT_LAST'] and \
                                    item.entry == cfg['EVENT_NEXT'] and \
                                    (last.name == item.name) == cfg['LOCATION_CHECK']:
                        if cfg.has_key('DATE_CHECK'):
                            logging.info('DATE_CHECK')
                            logging.info(cfg['DATE_CHECK'] == (last.event.date() == item.event.date()))
                            if cfg['DATE_CHECK'] == (last.event.date() == item.event.date()):
                                action = cfg['ACTION']
                        else:
                            action = cfg['ACTION']
                elif item.entry == cfg['EVENT_NEXT']:
                    action = cfg['ACTION']
            # action ausführen.
            logging.info('Action: %s' % action)
            if action == 'ADD':
                if work:
                    items.append(work)
                work = {"name": item.name,
                        "start": item.event,
                        "end": item.event,
                        "pause": timedelta(0)
                        }
            if action == 'PAUSE':
                work['pause'] = item.event - work['end']
                work['end'] = item.event
            if action == 'ENDTIME':
                work['end'] = item.event
            last = item

        if work:
            items.append(work)

        # round minuts
        for item in items:
            # Startzeit abrunden
            old_start = item['start']
            item['start'] -= timedelta(seconds=(old_start.minute % 15) * 60 + old_start.second)
            # Endzeit aufrunden
            old_end = item['end']
            item['end'] += timedelta(seconds=(14 - old_end.minute % 15) * 60 + (60 - old_end.second))
            # Pause abrunden - Pausen unter 15 min gelten nicht als abzugsfähige Arbeitszeit.
            item['pause'] = timedelta(seconds=(item['pause'].total_seconds() // (15 * 60)) * 15 * 60)
        return items

    # calculateTimes

    def post(self):
        if self.request.get('name') or self.request.get('device'):
            self.saveGeoRequestParam(self.request, self.user.user_id())
            self.redirect('/dashboard')
        else:
            self.redirect('/dashboard?msg=' + urllib.quote(ERROR_PARAMS))
            # post


# DashBoard

class DashBoardConfig(AuthorizedRequest):
    def post(self):
        devices = MyDevice.getAllDevices(self.user.user_id())

        logging.info(self.request.POST)
        for name, value in self.request.POST.iteritems():
            cmd, device_id = name.split("_", 1)

            logging.info(u'cmd: %s, device_id: %s, value: %s' % (cmd, device_id, value))
            for dev in devices:
                if dev.device_id == device_id:
                    if cmd == 'name':
                        logging.info('bocked-param: %s = %s' %
                                     ('block_' + device_id, self.request.get('block_' + device_id)))
                        if dev.name != value:
                            dev.name = value
                            dev.blocked = self.request.get('block_' + device_id) == 'on'
                            dev.put()
                        else:
                            if dev.blocked != (self.request.get('block_' + device_id) == 'on'):
                                dev.blocked = self.request.get('block_' + device_id) == 'on'
                            dev.put()
                    if cmd == 'delete':
                        Geofancy.deleteByDeviceId(self.user.user_id(), dev.device_id)
                        if dev.name:
                            dev.key.delete()
                        # Should I hide it from the list?
                        dev.device_id = '_'

        self.redirect('/dashboard#config')
        # post
        # DashBoardConfig
