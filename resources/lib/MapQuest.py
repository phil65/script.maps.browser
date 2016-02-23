# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import Utils
import googlemaps

MAPQUEST_KEY = "Fmjtd%7Cluur2hu829%2C75%3Do5-9wasd4"
MAX_LIMIT = 25
BASE_URL = 'http://www.mapquestapi.com/traffic/v2/'

incident_types = {1: "Construction",
                  2: "Event",
                  3: "Congestion / Flow",
                  4: "Incident / Accident"}


class MapQuest():

    def __init__(self):
        pass

    def get_incidents(self, lat, lon, zoom):
        mx, my = Utils.latlon_to_meters(lat, lon)
        px, py = Utils.meters_to_pixels(mx, my, zoom)
        mx_high, my_high = Utils.pixels_to_meters(px + 320, py + 200, zoom)
        mx_low, my_low = Utils.pixels_to_meters(px - 320, py - 200, zoom)
        lat_high, lon_high = Utils.meters_to_latlon(mx_high, my_high)
        lat_low, lon_low = Utils.meters_to_latlon(mx_low, my_low)
        params = {"key": MAPQUEST_KEY,
                  "inFormat": "kvp",
                  "boundingBox": "%s,%s,%s,%s" % (lat_high, lon_high, lat_low, lon_low)}
        url = BASE_URL + 'incidents?' + urllib.urlencode(params)
        results = Utils.get_JSON_response(url)
        places = []
        pins = ""
        letter = ord('A')
        if results['info']['statuscode'] == 400:
            Utils.notify("Error", " - ".join(results['info']['messages']))
            return [], ""
        elif "incidents" not in results:
            Utils.notify("Error", "Could not fetch results")
            return [], ""
        for i, place in enumerate(results['incidents']):
            lat = str(place['lat'])
            lon = str(place['lng'])
            params = {"key": MAPQUEST_KEY,
                      "mapLat": place['lat'],
                      "mapLng": place['lng'],
                      "mapHeight": 400,
                      "mapWidth": 400,
                      "mapScale": 433342}
            url = BASE_URL + "flow?" + urllib.urlencode(params)
            googlemap = googlemaps.get_static_map(lat=lat,
                                                  lon=lon)
            props = {'name': place['shortDesc'],
                     'label': place['shortDesc'],
                     'label2': place['startTime'],
                     'description': place['fullDesc'],
                     'distance': str(place['distance']),
                     'delaytypical': str(place['delayFromTypical']),
                     'delayfreeflow': str(place['delayFromFreeFlow']),
                     "GoogleMap": googlemap,
                     "venue_image": url,
                     "thumb": url,
                     "icon": place['iconURL'],
                     'date': place['startTime'],
                     'severity': str(place['severity']),
                     'type': incident_types.get(place['type'], ""),
                     "letter": chr(letter),
                     "lat": lat,
                     "lon": lon,
                     "index": str(i)}
            pins += "&markers=color:blue%7Clabel:{0}%7C{1},{2}".format(chr(letter), lat, lon)
            places.append(props)
            letter += 1
            if i > MAX_LIMIT:
                break
        fill_area = "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|%s,%s|%s,%s|%s,%s|%s,%s" % (lat_high, lon_high, lat_high, lon_low, lat_low, lon_low, lat_low, lon_high)
        pins = pins + fill_area.replace("|", "%7C")
        return places, pins
