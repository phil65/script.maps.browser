# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib

from Utils import *

MAPQUEST_KEY = "Fmjtd%7Cluur2hu829%2C75%3Do5-9wasd4"
GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
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
        mx, my = latlon_to_meters(lat, lon)
        px, py = meters_to_pixels(mx, my, zoom)
        mx_high, my_high = pixels_to_meters(px + 320, py + 200, zoom)
        mx_low, my_low = pixels_to_meters(px - 320, py - 200, zoom)
        lat_high, lon_high = meters_to_latlon(mx_high, my_high)
        lat_low, lon_low = meters_to_latlon(mx_low, my_low)
        params = {"key": MAPQUEST_KEY,
                  "inFormat": "kvp",
                  "boundingBox": "%s,%s,%s,%s" % (lat_high, lon_high, lat_low, lon_low)}
        url = BASE_URL + 'incidents?' + urllib.urlencode(params)
        results = Get_JSON_response(url)
        places = []
        pin_string = ""
        letter = ord('A')
        if results['info']['statuscode'] == 400:
            Notify("Error", " - ".join(results['info']['messages']))
            return [], ""
        elif "incidents" not in results:
            Notify("Error", "Could not fetch results")
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
            url = "flow?" + urllib.urlencode(params)
            image = BASE_URL + url
            search_string = lat + "," + lon
            params = {"sensor": "false",
                      "scale": 2,
                      "maptype": "roadmap",
                      "center": search_string,
                      "zoom": 13,
                      "markers": search_string,
                      "size": "640x640",
                      "key": GOOGLE_MAPS_KEY}
            google_map = 'http://maps.googleapis.com/maps/api/staticmap?' + urllib.urlencode(params)
            incident_type = incident_types.get(place['type'], "")
            prop_list = {'name': place['shortDesc'],
                         'label': place['shortDesc'],
                         'label2': place['startTime'],
                         'description': place['fullDesc'],
                         'distance': str(place['distance']),
                         'delaytypical': str(place['delayFromTypical']),
                         'delayfreeflow': str(place['delayFromFreeFlow']),
                         "GoogleMap": google_map,
                         "venue_image": image,
                         "thumb": image,
                         "icon": place['iconURL'],
                         'date': place['startTime'],
                         'severity': str(place['severity']),
                         'type': incident_type,
                         "sortletter": chr(letter),
                         "lat": lat,
                         "lon": lon,
                         "index": str(i)}
            pin_string = pin_string + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places.append(prop_list)
            letter += 1
            if i > MAX_LIMIT:
                break
        fill_area = "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|%s,%s|%s,%s|%s,%s|%s,%s" % (lat_high, lon_high, lat_high, lon_low, lat_low, lon_low, lat_low, lon_high)
        pin_string = pin_string + fill_area.replace("|", "%7C")
        return places, pin_string
