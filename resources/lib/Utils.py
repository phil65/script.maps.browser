# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from __future__ import absolute_import
from __future__ import unicode_literals

import requests
import os
import re
import time
import math
from PIL import Image
import hashlib
import json

import xbmc
import xbmcvfs
import xbmcgui

from resources.lib import imagetags

from kodi65 import utils
from kodi65 import VideoItem

TILESIZE = 256
INITIAL_RESOLUTION = 2 * math.pi * 6378137 / TILESIZE  # 156543.03392804062 for tileSize 256 pixels
ORIGIN_SHIFT = 2 * math.pi * 6378137 / 2.0  # 20037508.342789244
HOME = xbmcgui.Window(10000)


def get_bounding_box(lat, lon, zoom):
    '''
    returns 4 rectangle values lat high, lon high, lat low, lon low
    '''
    mx, my = latlon_to_meters(lat, lon)
    px, py = meters_to_pixels(mx, my, zoom)
    mx_high, my_high = pixels_to_meters(px + 320, py + 200, zoom)
    mx_low, my_low = pixels_to_meters(px - 320, py - 200, zoom)
    lat_high, lon_high = meters_to_latlon(mx_high, my_high)
    lat_low, lon_low = meters_to_latlon(mx_low, my_low)
    return lat_high, lon_high, lat_low, lon_low


def get_radius(lat, lon, zoom, size):
    '''
    get screen radius for given position / zoom
    '''
    hor_px = int(size.split("x")[0])
    ver_px = int(size.split("x")[1])
    mx, my = latlon_to_meters(lat, lon)
    px, py = meters_to_pixels(mx, my, zoom)
    mx2, my2 = pixels_to_meters(px + hor_px / 2, py + ver_px / 2, zoom)
    return min(abs((my - my2) / 2000), 500)


def latlon_to_meters(lat, lon):
    '''
    Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913
    '''

    if not lon:
        return None
    mx = lon * ORIGIN_SHIFT / 180.0
    my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    my = my * ORIGIN_SHIFT / 180.0
    return mx, my


def meters_to_pixels(mx, my, zoom):
    '''
    Converts EPSG:900913 to pyramid pixel coordinates in given zoom level
    '''

    res = INITIAL_RESOLUTION / (2 ** zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py


def pixels_to_meters(px, py, zoom):
    '''
    Converts pixel coordinates in given zoom level of pyramid to EPSG:900913
    '''

    res = INITIAL_RESOLUTION / (2 ** zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    return mx, my


def meters_to_latlon(mx, my):
    '''
    Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum
    '''

    lon = (mx / ORIGIN_SHIFT) * 180.0
    lat = (my / ORIGIN_SHIFT) * 180.0

    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon


def get_string_from_url(url):
    '''
    download content from *url and return as text
    '''
    for i in range(0, 3):
        try:
            r = requests.get(url=url,
                             headers={'User-agent': 'XBMC/14.2 ( phil65@kodi.tv )'})
            return r.text
        except Exception:
            xbmc.sleep(500)
    utils.notify("Error", "Could not download data. Internet connection OK?")
    utils.log("get_string_from_url: could not get data from %s" % url)
    return ""


def get_images(path=""):
    images = []
    for filename in xbmcvfs.listdir(path)[-1]:
        try:
            img = Image.open(path + filename)
            exif_data = imagetags.get_exif_data(img)
            lat, lon = imagetags.get_lat_lon(exif_data)
            if not lat or not lon:
                continue
            if "DateTimeOriginal" in exif_data:
                date = exif_data["DateTimeOriginal"]
            elif "DateTime" in exif_data:
                date = exif_data["DateTime"]
            else:
                date = ""
            image = VideoItem(label=filename)
            image.set_properties({"lat": str(lat),
                                  "lon": str(lon),
                                  "date": date,
                                  "description": date})
            image.set_art("thumb", path + filename)
            images.append(image)
        except Exception:
            pass
    return images


def string_to_deg(string):
    reverse = string[0].lower() in ["w", "s"]
    string = string.strip().replace('"', '').replace("'", "")
    string = string[1:].replace("d", "").replace("  ", " ").replace("  ", " ")
    div = '[|:|\s]'  # allowable field delimiters "|", ":", whitespace
    sdec = '(\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}\.?\d+?)'
    co_search = re.compile(sdec).search(string)
    if co_search is None:
        raise ValueError("Invalid input string: %s" % string)
    elems = co_search.groups()
    dec_degrees = float(elems[0]) + float(elems[1]) / 60.0 + float(elems[2]) / 3600.0
    if string[0].lower() in ["w", "s"] or reverse:
        dec_degrees = -1.0 * dec_degrees
    return dec_degrees


def parse_geotags(lat, lon):
    '''
    parse Kodi GPS String and return lat, lon
    '''
    if lon:
        return string_to_deg(lat), string_to_deg(lon)
    else:
        coords = lat.split(",lon=")
        return string_to_deg(coords[0]), string_to_deg(coords[1])


def get_coords_by_ip():
    '''
    returns lat, lon for current position (based on geoip)
    '''
    # url = 'https://www.telize.com/geoip'
    response = get_string_from_url('http://ip-api.com/json')
    if not response:
        return "", ""
    results = json.loads(response)
    return results["lat"], results["lon"]
