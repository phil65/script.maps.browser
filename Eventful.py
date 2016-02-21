# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *
import xbmcgui

GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
EVENTFUL_KEY = 'Nw3rh3mXn8RhMQNK'
BASE_URL = "http://api.eventful.com/json/"


class Eventful():

    def __init__(self):
        pass

    def select_category(self):
        results = self.get_data(method="categories/list",
                                cache_days=7)
        modeselect = ["All Categories"]
        for item in results["category"]:
            modeselect.append(cleanText(item["name"]))
        index = xbmcgui.Dialog().select("Choose Category", modeselect)
        if index == -1:
            return None
        if index > 0:
            return results["category"][index - 1]["id"]
        elif index > -1:
            return ""

    def get_eventlist(self, lat="", lon="", query="", category="", radius=30):
        params = {"image_sizes": "large",
                  "include": "price",
                  "units": "km",
                  "page_size": 26,
                  "sort_order": "date",
                  "date": "Future",
                  "where": "%.8f,%.8f" % (lat, lon),
                  "within": int(radius),
                  "query": query,
                  "category": category}
        results = self.get_data(method="events/search",
                                params=params,
                                cache_days=7)
        return self.handle_events(results['events']['event'])

    def get_venue_info(self, event_id=""):
        results = self.get_data(method="venues/get",
                                params={"id": event_id},
                                cache_days=7)
        return self.handle_events(results['venue'])

    def get_event_info(self, event_id=""):
        params = {"id": event_id,
                  "image_sizes": "blackborder500,edpborder500"}
        results = self.get_data(method="events/get",
                                params=params,
                                cache_days=7)
        return self.handle_events(results['venue'])

    def handle_events(self, results):
        pin_string = ""
        places = []
        letter = ord('A')
        count = 0
        if not isinstance(results, list):
            results = [results]
        for venue in results:
            venuename = cleanText(venue['venue_name'])
            lat = str(venue['latitude'])
            lon = str(venue['longitude'])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLEMAPS_KEY)
            if "image" in venue and venue["image"]:
                photo = venue["image"]["large"]["url"]
            else:
                photo = ""
            #  start_time = venue["start_time"].split(" ")
            #  stop_time = venue["stop_time"].split(" ")
            if venue["start_time"] == venue["stop_time"] or not venue["stop_time"]:
                date = venue["start_time"]
            else:
                date = venue["start_time"] + " - " + venue["stop_time"]
            date = date.replace("00:00:00", "")
            props = {"id": str(venue['id']),
                     "eventful_id": str(venue['venue_id']),
                     "eventname": cleanText(venue['title']),
                     "description": cleanText(venue['description']),
                     "name": venuename,
                     "label": venuename,
                     "label2": date,
                     "photo": photo,
                     "thumb": photo,
                     "date": date,
                     "address": cleanText(venue["venue_address"]),
                     "Venue_Image": photo,
                     "venue_id_eventful": venue['venue_id'],
                     "GoogleMap": googlemap,
                     "index":  str(count),
                     "sortletter": chr(letter),
                     "lat": lat,
                     "lon": lon}
            pin_string += "&markers=color:blue%7Clabel:%s%7C%s,%s" % (chr(letter), lat, lon)
            places.append(props)
            count += 1
            letter += 1
        return places, pin_string

    def get_data(self, method, params={}, cache_days=0.5):
        params["app_key"] = EVENTFUL_KEY
        # params = {k: v for k, v in params.items() if v}
        params = dict((k, v) for (k, v) in params.iteritems() if v)
        params = dict((k, unicode(v).encode('utf-8')) for (k, v) in params.iteritems())
        url = "{base_url}{method}?{params}".format(base_url=BASE_URL,
                                                   method=method,
                                                   params=urllib.urlencode(params))
        return get_JSON_response(url=url,
                                 cache_days=cache_days)
