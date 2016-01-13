from Utils import *
import xbmcgui

GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
EVENTFUL_KEY = 'Nw3rh3mXn8RhMQNK'


class Eventful():

    def __init__(self):
        pass

    def select_category(self):
        url = "http://api.eventful.com/json/categories/list?app_key=%s" % (EVENTFUL_KEY)
        results = Get_JSON_response(url, 7)
        modeselect = ["All Categories"]
        for item in results["category"]:
            modeselect.append(cleanText(item["name"]))
        index = xbmcgui.Dialog().select("Choose Category", modeselect)
        if index > 0:
            return results["category"][index - 1]["id"]
        elif index > -1:
            return ""
        else:
            return None

    def get_eventlist(self, lat="", lon="", query="", category="", radius=30):
        base_url = "http://api.eventful.com/json/events/search?image_sizes=large&include=price&units=km&page_size=26&sort_order=date&date=Future&app_key=%s" % (EVENTFUL_KEY)
        url = '&where=%.8f,%.8f&within=%i' % (lat, lon, int(radius))
        if query:
            url = url + '&query=%s' % (query)
        if category:
            url = url + '&category=%s' % (category)
        results = Get_JSON_response(base_url + url)
        return self.handle_events(results['events']['event'])

    def get_venuelist(self, lat="", lon="", query=""):
        base_url = "http://api.eventful.com/json/events/search?image_sizes=large&include=price&units=km&page_size=26&sort_order=date&date=Future&app_key=%s" % (EVENTFUL_KEY)
        url = '&where=%.8f,%.8f&within=%i' % (lat, lon, int(radius))
        if query:
            url = url + '&query=%s' % (query)
        #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
        results = Get_JSON_response(base_url + url)
        return self.handle_events(results['events']['event'])

    def get_venue_info(self, event_id=""):
        base_url = "http://api.eventful.com/json/venues/get?app_key=%s" % (EVENTFUL_KEY)
        url = '&id=%s' % (str(event_id))
        results = Get_JSON_response(base_url + url)
        return self.handle_events(results['venue'])

    def get_event_info(self, event_id=""):
        base_url = "http://api.eventful.com/json/events/get?app_key=%s" % (EVENTFUL_KEY)
        url = '&id=%s&image_sizes=blackborder500,edpborder500' % (str(event_id))
        results = Get_JSON_response(base_url + url)
        return self.handle_events(results['venue'])

    def handle_events(self, results):
        pin_string = ""
        places_list = list()
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
            if ("image" in venue) and venue["image"]:
                photo = venue["image"]["large"]["url"]
            else:
                photo = ""
            #  start_time = venue["start_time"].split(" ")
            #  stop_time = venue["stop_time"].split(" ")
            if (venue["start_time"] == venue["stop_time"]) or (venue["stop_time"] is None):
                date = venue["start_time"]
            else:
                date = venue["start_time"] + " - " + venue["stop_time"]
            date = date.replace("00:00:00", "")
            prop_list = {"id": str(venue['id']),
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
            pin_string = pin_string + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places_list.append(prop_list)
            count += 1
            letter += 1
        return places_list, pin_string

