# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib
import xbmc
import xbmcaddon

GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
ADDON = xbmcaddon.Addon()


def get_static_map(lat=None, lon=None, location="", scale=2, zoom=13, maptype="roadmap"):
    if lat and lon:
        location = "%s,%s" % (lat, lon)
    params = {"sensor": "false",
              "scale": scale,
              "maptype": maptype,
              "format": ADDON.getSetting("ImageFormat"),
              "language": xbmc.getLanguage(xbmc.ISO_639_1),
              "center": location,
              "zoom": zoom,
              "markers": location,
              "size": "640x640",
              "key": GOOGLEMAPS_KEY}
    return 'http://maps.googleapis.com/maps/api/staticmap?' + urllib.urlencode(params)


