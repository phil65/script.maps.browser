# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from __future__ import absolute_import
from __future__ import unicode_literals

import urllib
import xbmc

from kodi65 import addon
from kodi65 import selectdialog
from kodi65 import VideoItem
from kodi65 import ItemList
from kodi65 import utils


GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
GOOGLE_STREETVIEW_KEY = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'

BASE_URL = "http://maps.googleapis.com/maps/api/"


def get_static_map(lat=None, lon=None, location="", scale=2, zoom=13, maptype="roadmap", size="640x640"):
    if lat and lon:
        location = "%s,%s" % (lat, lon)
    params = {"sensor": "false",
              "scale": scale,
              "maptype": maptype,
              "format": addon.setting("ImageFormat"),
              "language": xbmc.getLanguage(xbmc.ISO_639_1),
              "center": location.replace('"', ''),
              "zoom": zoom,
              "markers": location.replace('"', ''),
              "size": size,
              "key": GOOGLEMAPS_KEY}
    return BASE_URL + 'staticmap?' + urllib.urlencode(params)


def get_streetview_image(lat=None, lon=None, fov=0, location="", heading=0, pitch=0, size="640x400"):
    params = {"sensor": "false",
              "format": addon.setting("ImageFormat"),
              "language": xbmc.getLanguage(xbmc.ISO_639_1),
              "fov": fov,
              "location": "%s,%s" % (lat, lon) if lat and lon else location.replace('"', ''),
              "heading": heading,
              "pitch": pitch,
              "size": size,
              "key": GOOGLE_STREETVIEW_KEY}
    return BASE_URL + "streetview?&" + urllib.urlencode(params)


def get_coords_by_location(show_dialog, search_string):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false"
    url = "&address=%s" % (urllib.quote_plus(search_string))
    results = utils.get_JSON_response(base_url + url)
    if not results or not results.get("results"):
        return None
    first_match = results["results"][0]["geometry"]["location"]
    if show_dialog and len(results["results"]) > 1:
        places = ItemList()
        for item in results["results"]:
            location = item["geometry"]["location"]
            googlemap = get_static_map(lat=location["lat"],
                                       lon=location["lng"],
                                       scale=1,
                                       size="320x320")
            place = VideoItem(label=item['formatted_address'])
            place.set_properties({'lat': location["lat"],
                                  'lon': location["lng"],
                                  'id': item['formatted_address']})
            place.set_art("thumb", googlemap)
            places.append(place)
        index = selectdialog.open(header=addon.LANG(32024),
                                  listitems=places)
        if index > -1:
            return (places[index].get_property("lat"), places[index].get_property("lon"), 12)
    elif results["results"]:
        return (first_match["lat"], first_match["lng"], 12)  # no window when only 1 result
    return None  # old values when no hit


def create_letter_pins(items):
    letter = ord('A')
    pins = ""
    for i, item in enumerate(items):
        char = chr(letter + i)
        item["letter"] = char
        pins += "&markers=color:blue%7Clabel:{0}%7C{1},{2}".format(char, item["lat"], item["lon"])
    return pins


def create_pins(items):
    pins = "&markers=color:blue"
    for i, item in enumerate(items):
        if len(pins) < 1830:
            pins += "%7C{0},{1}".format(item["lat"], item["lon"])
    return pins
