from Utils import *
import xbmcgui
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
eventful_key = 'Nw3rh3mXn8RhMQNK'


class Eventful():

    def __init__(self):
        pass

    def SelectCategory(self):
        url = "http://api.eventful.com/json/categories/list?app_key=%s" % (eventful_key)
        results = Get_JSON_response("", url, 7)
        modeselect = []
   #     prettyprint(results)
        modeselect.append("All Categories")
        for item in results["category"]:
            modeselect.append(cleanText(item["name"]))
        categorydialog = xbmcgui.Dialog()
        provider_index = categorydialog.select("Choose Category", modeselect)
        if provider_index > 0:
            return results["category"][provider_index - 1]["id"]
        elif provider_index > -1:
            return ""
        else:
            return None

    def GetEventfulEventList(self, lat="", lon="", query="", category="", radius=30):
        base_url = "http://api.eventful.com/json/events/search?image_sizes=large&include=price&units=km&page_size=26&sort_order=date&date=Future&app_key=%s" % (eventful_key)
        url = '&where=%.8f,%.8f&within=%i' % (lat, lon, int(radius))
        log(url)
        if query is not "":
            url = url + '&query=%s' % (query)
        if category is not "":
            url = url + '&category=%s' % (category)
        results = Get_JSON_response(base_url, url)
        return self.HandleEventfulEventResult(results['events']['event'])

    def GetEventfulVenueList(self, lat="", lon="", query=""):
        base_url = "http://api.eventful.com/json/events/search?image_sizes=large&include=price&units=km&page_size=26&sort_order=date&date=Future&app_key=%s" % (eventful_key)
        url = '&where=%.8f,%.8f&within=%i' % (lat, lon, int(radius))
        if query is not "":
            url = url + '&query=%s' % (query)
      #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
        results = Get_JSON_response(base_url, url)
        return self.HandleEventfulEventResult(results['events']['event'])

    def GetEventInfo(self, event_id=""):
        base_url = "http://api.eventful.com/json/venues/get?app_key=%s" % (eventful_key)
        url = '&id=%s' % (str(event_id))
        log(url)
        results = Get_JSON_response(base_url, url)
   #     prettyprint(results)
        return self.HandleEventfulEventResult(results['venue'])

    def HandleEventfulEventResult(self, results):
        PinString = ""
        places_list = list()
        letter = ord('A')
        count = 0
        if not isinstance(results, list):
            results = [results]
        for venue in results:
            eventname = cleanText(venue['title'])
            venuename = cleanText(venue['venue_name'])
            formattedAddress = cleanText(venue["venue_address"])
            lat = str(venue['latitude'])
            lon = str(venue['longitude'])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
            if venue["image"] is not None:
                photo = venue["image"]["large"]["url"]
            else:
                photo = ""
         #   start_time = venue["start_time"].split(" ")
          #  stop_time = venue["stop_time"].split(" ")
            if (venue["start_time"] == venue["stop_time"]) or (venue["stop_time"] is None):
                date = venue["start_time"]
            else:
                date = venue["start_time"] + " - " + venue["stop_time"]
            date = date.replace("00:00:00", "")
            prop_list = {"id": str(venue['id']),
                         "eventname": eventname,
                         "description": cleanText(venue['description']),
                         "name": venuename,
                         "label": venuename,
                         "label2": date,
                         "photo": photo,
                         "thumb": photo,
                         "date": date,
                         "address": formattedAddress,
                         "Venue_Image": photo,
                         "venue_id_eventful": venue['venue_id'],
                         "GoogleMap": googlemap,
                         "index":  str(count),
                         "sortletter": chr(letter),
                         "lat": lat,
                         "lon": lon}
            item = CreateListItem(prop_list)
            PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places_list.append(item)
            count += 1
            letter += 1
        return places_list, PinString

