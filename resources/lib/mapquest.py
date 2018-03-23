# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from __future__ import absolute_import
from __future__ import unicode_literals

import urllib
from resources.lib import Utils
from resources.lib import googlemaps

from kodi65 import utils
from kodi65 import VideoItem
from kodi65 import ItemList

MAPQUEST_KEY = "lACkugtJjBp3lSA1ajvP05Sb6SikjNAW"
MAX_LIMIT = 25
BASE_URL = 'http://www.mapquestapi.com/traffic/v2/'

incident_types = {1: "Construction",
                  2: "Event",
                  3: "Congestion / Flow",
                  4: "Incident / Accident"}


def get_incidents(lat, lon, zoom):
    lat_high, lon_high, lat_low, lon_low = Utils.get_bounding_box(lat, lon, zoom)
    params = {"key": MAPQUEST_KEY,
              "inFormat": "kvp",
              "boundingBox": "%s,%s,%s,%s" % (lat_high, lon_high, lat_low, lon_low)}
    url = BASE_URL + 'incidents?' + urllib.urlencode(params)
    results = Utils.get_JSON_response(url)
    places = ItemList()
    if results['info']['statuscode'] == 400:
        utils.notify("Error", " - ".join(results['info']['messages']), time=10000)
        return []
    elif "incidents" not in results:
        utils.notify("Error", "Could not fetch results")
        return []
    for place in results['incidents'][:MAX_LIMIT]:
        lat = str(place['lat'])
        lon = str(place['lng'])
        params = {"key": MAPQUEST_KEY,
                  "mapLat": place['lat'],
                  "mapLng": place['lng'],
                  "mapHeight": 400,
                  "mapWidth": 400,
                  "mapScale": 433342}
        url = BASE_URL + "flow?" + urllib.urlencode(params)
        item = VideoItem(label=place['shortDesc'],
                         label2=place['startTime'])
        item.set_properties({'name': place['shortDesc'],
                             'description': place['fullDesc'],
                             'distance': str(place['distance']),
                             'delaytypical': str(place['delayFromTypical']),
                             'delayfreeflow': str(place['delayFromFreeFlow']),
                             'date': place['startTime'],
                             'severity': str(place['severity']),
                             'type': incident_types.get(place['type'], ""),
                             "lat": lat,
                             "lon": lon})
        item.set_artwork({"thumb": url,
                          "icon": place['iconURL'],
                          "googlemap": googlemaps.get_static_map(lat=lat, lon=lon)})
        places.append(item)
    return places


def get_bounding_box(lat, lon, zoom):
    lat_high, lon_high, lat_low, lon_low = Utils.get_bounding_box(lat, lon, zoom)
    box_params = ["&path=color:0x00000000",
                  "weight:5",
                  "fillcolor:0xFFFF0033",
                  "%s,%s" % (lat_high, lon_high),
                  "%s,%s" % (lat_high, lon_low),
                  "%s,%s" % (lat_low, lon_low),
                  "%s,%s" % (lat_low, lon_high)]
    return "%7C".join(box_params)
