# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

# code for FourSquare Scraping based on script.maps by a.a.alsaleh. credits to him.

from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import str

import urllib

import xbmcgui
from resources.lib import Utils
from resources.lib import googlemaps

from kodi65 import utils
from kodi65 import addon
from kodi65 import VideoItem
from kodi65 import ItemList

FOURSQUARE_ID = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
FOURSQUARE_SECRET = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
BASE_URL = "https://api.foursquare.com/v2/"

SECTIONS = {"topPicks": addon.LANG(32005),
            "food": addon.LANG(32006),
            "drinks": addon.LANG(32007),
            "coffee": addon.LANG(32008),
            "shops": addon.LANG(32009),
            "arts": addon.LANG(32010),
            "outdoors": addon.LANG(32011),
            "sights": addon.LANG(32012),
            "trending": addon.LANG(32013),
            "specials": addon.LANG(32014),
            "nextVenues": addon.LANG(32015)}


class FourSquare():

    def __init__(self):
        pass

    def handle_places(self, results):
        places = ItemList()
        for venue in results:
            try:
                photo = venue['venue']['photos']['groups'][0]['items'][0]
                photo = "%s%s%s" % (photo['prefix'], photo['height'], photo['suffix'])
            except Exception:
                photo = ""
            if "name" not in venue:
                venue = venue["venue"]
            if venue['categories']:
                icon = venue['categories'][0]['icon']
                icon = "%s88%s" % (icon['prefix'], icon['suffix'])
            else:
                icon = ""
            if 'formattedAddress' in venue['location']:
                formattedAddress = "[CR]".join(filter(None, venue['location']['formattedAddress']))
            lat = venue['location']['lat']
            lon = venue['location']['lng']
            item = VideoItem(label=venue['name'],
                             label2=venue['name'])
            item.set_properties({"id": venue['id'],
                                 "foursquare_id": venue['id'],
                                 "distance": venue['location']['distance'],
                                 "visited": venue['stats']['usersCount'],
                                 "twitter": venue['contact'].get('twitter', ""),
                                 "eventname": venue['location'].get('address'),
                                 "description": formattedAddress,
                                 "name": venue['name'],
                                 "lat": lat,
                                 "lon": lon,
                                 "phone": venue['contact'].get('phone', ""),
                                 "comments": venue['stats']['tipCount']})
            item.set_artwork({"thumb": photo,
                              "icon": icon,
                              "googlemap": googlemaps.get_static_map(lat=lat, lon=lon)})
            places.append(item)
        return places

    def get_places(self, lat, lon, query="", category_id="", intent="checkin"):
        params = {"limit": 26,
                  "ll": '%.8f,%.8f' % (lat, lon),
                  "query": query,
                  "intent": intent,
                  "categoryId": category_id}
        results = self.get_data(method="venues/search",
                                params=params,
                                cache_days=7)
        if results and 'meta' in results:
            if results['meta']['code'] == 200:
                return self.handle_places(results['response']['venues'])
            elif results['meta']['code'] == 400:
                utils.notify("Error", "LIMIT EXCEEDED")
            else:
                utils.notify("ERROR", "Could not get requested information")
        else:
            utils.log("ERROR")
        return []

    def get_places_by_section(self, lat, lon, placetype):
        params = {"venuePhotos": 1,
                  "ll": '%.8f,%.8f' % (float(lat), float(lon)),
                  "section": placetype}
        results = self.get_data(method="venues/explore",
                                params=params,
                                cache_days=7)
        if not results or 'meta' not in results:
            return []
        if results['meta']['code'] == 200:
            if results['response']['groups'][0]['items']:
                return self.handle_places(results['response']['groups'][0]['items'])
            else:
                utils.notify("Error", "No results found near the selected area.")
        elif results['meta']['code'] == 400:
            utils.log("LIMIT EXCEEDED")
        else:
            utils.log("ERROR" + str(results['meta']['code']))
        return []

    def select_category(self):
        results = self.get_data(method="venues/categories",
                                cache_days=7)
        modeselect = [addon.LANG(32122)]
        modeselect += [item["name"] for item in results["categories"]]
        index = xbmcgui.Dialog().select(addon.LANG(32123), modeselect)
        if index > 0:
            return results["categories"][index - 1]["id"]
        elif index > -1:
            return ""

    def select_section(self):
        modeselect = [addon.LANG(32120)]
        modeselect += [value for value in SECTIONS.itervalues()]
        index = xbmcgui.Dialog().select(addon.LANG(32121), modeselect)
        if index > 0:
            return SECTIONS.keys()[index - 1]
        elif index == 0:
            return ""

    def get_data(self, method, params={}, cache_days=0.5):
        params["client_id"] = FOURSQUARE_ID
        params["client_secret"] = FOURSQUARE_SECRET
        params["v"] = 20130815
        params = {k: v for (k, v) in params.iteritems() if v}
        params = {k: str(v) for (k, v) in params.iteritems()}
        url = "{base_url}{method}?{params}".format(base_url=BASE_URL,
                                                   method=method,
                                                   params=urllib.urlencode(params))
        return Utils.get_JSON_response(url=url,
                                       cache_days=cache_days)


FS = FourSquare()
