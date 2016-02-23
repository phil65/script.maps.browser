# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import xbmc
import xbmcaddon

GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
GOOGLE_STREETVIEW_KEY = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'

BASE_URL = "http://maps.googleapis.com/maps/api/"

ADDON = xbmcaddon.Addon()


def get_static_map(lat=None, lon=None, location="", scale=2, zoom=13, maptype="roadmap", size="640x640"):
    if lat and lon:
        location = "%s,%s" % (lat, lon)
    params = {"sensor": "false",
              "scale": scale,
              "maptype": maptype,
              "format": ADDON.getSetting("ImageFormat"),
              "language": xbmc.getLanguage(xbmc.ISO_639_1),
              "center": location.replace('"', ''),
              "zoom": zoom,
              "markers": location.replace('"', ''),
              "size": size,
              "key": GOOGLEMAPS_KEY}
    return BASE_URL + 'staticmap?' + urllib.urlencode(params)


def get_streetview_image(lat=None, lon=None, fov=0, location="", heading=0, pitch=0, size="640x400"):
    params = {"sensor": "false",
              "format": ADDON.getSetting("ImageFormat"),
              "language": xbmc.getLanguage(xbmc.ISO_639_1),
              "fov": fov,
              "location": "%s,%s" % (lat, lon) if lat and lon else location.replace('"', ''),
              "heading": heading,
              "pitch": pitch,
              "size": size,
              "key": GOOGLE_STREETVIEW_KEY}
    return BASE_URL + "streetview?&" + urllib.urlencode(params)
