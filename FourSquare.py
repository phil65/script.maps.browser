# code for FourSquare Scraping based on script.maps by a.a.alsaleh. credits to him.

import xbmcgui
import xbmcaddon
from Utils import *

ADDON = xbmcaddon.Addon()
GOOGLEMAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
FOURSQUARE_ID = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
FOURSQUARE_SECRET = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
FACTUAL_KEY = 'n1yQsp5q68HLgKSYkBmRSWG710KI0IzlQS55hOIY'
FACTUAL_SECRET = '8kG0Khj87JfcNiabqmixuQYuGgDUvu1PnWN5IVca'
BING_KEY = 'Ai8sLX5R44tf24_2CGmbxTYiIX6w826dsCVh36oBDyTmH21Y6CxYEqtrV9oYoM6O'

# def GetBingMap(self):
# url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s?mapSize=800,600&key=%s' % (urllib.quote(self.search_string),BING_KEY)
# url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/5?key=%s' % (self.lat,self.lon, BING_KEY)
#         'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/%i?fmt=%s&key=%s' % (self.lat, self.lon, self.zoom_level, self._format, BING_KEY)
# log(url)
# return url


class FourSquare():

    def __init__(self):
        pass

    def HandleFourSquarePlacesResult(self, results):
        self.PinString = ""
        places_list = list()
        letter = ord('A')
        count = 0
        for venue in results:
            try:
                photo_node = venue['venue']['photos']['groups'][0]['items'][0]
                photo = photo_node['prefix'] + str(photo_node['height']) + photo_node['suffix']
            except:
                photo = ""
            if "name" not in venue:
                venue = venue["venue"]
            if len(venue['categories']) > 0:
                icon = venue['categories'][0]['icon']['prefix'] + "88" + venue['categories'][0]['icon']['suffix']
            else:
                icon = ""
            if 'formattedAddress' in venue['location']:
                formattedAddress = "[CR]".join(filter(None, venue['location']['formattedAddress']))
            lat = str(venue['location']['lat'])
            lon = str(venue['location']['lng'])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLEMAPS_KEY)
            prop_list = {"id": str(venue['id']),
                         "foursquare_id": str(venue['id']),
                         "distance": str(venue['location']['distance']),
                         "visited": str(venue['stats']['usersCount']),
                         "twitter": venue['contact'].get('twitter', ""),
                         "eventname": formattedAddress,
                         "description": formattedAddress,
                         "name": venue['name'],
                         "label": venue['name'],
                         "label2": venue['name'],
                         "icon": icon,
                         "photo": photo,
                         "thumb": photo,
                         "Venue_Image": icon,
                         "GoogleMap": googlemap,
                         "index":  str(count),
                         "sortletter": chr(letter),
                         "lat": lat,
                         "lon": lon,
                         "phone": venue['contact'].get('phone', ""),
                         "comments": str(venue['stats']['tipCount'])}
            self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places_list.append(prop_list)
            count += 1
            letter += 1
        return places_list, self.PinString

    def GetPlacesList(self, lat, lon, query="", categoryid=""):
        base_url = "https://api.foursquare.com/v2/venues/search?limit=26&client_id=%s&client_secret=%s&v=20130815" % (FOURSQUARE_ID, FOURSQUARE_SECRET)
        url = '&ll=%.8f,%.8f' % (lat, lon)
        if query is not "":
            url = url + "&query=%s" % (query)
        if categoryid is not "":
            url = url + "&categoryId=%s" % (categoryid)
        results = Get_JSON_response(base_url + url)
        if results and 'meta' in results:
            if results['meta']['code'] == 200:
                return self.HandleFourSquarePlacesResult(results['response']['venues'])
            elif results['meta']['code'] == 400:
                Notify("Error", "LIMIT EXCEEDED")
            else:
                Notify("ERROR", "Could not get requested information")
        else:
            log("ERROR")
        return [], ""

    def GetPlacesListExplore(self, lat, lon, placetype):
        base_url = "https://api.foursquare.com/v2/venues/explore?limit=26&client_id=%s&client_secret=%s&v=20130815&venuePhotos=1" % (FOURSQUARE_ID, FOURSQUARE_SECRET)
        # url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, FOURSQUARE_ID, FOURSQUARE_SECRET)
        # url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", FOURSQUARE_ID, FOURSQUARE_SECRET)
        url = '&ll=%.8f,%.8f&section=%s' % (float(lat), float(lon), placetype)
        results = Get_JSON_response(base_url + url)
        if results and 'meta' in results:
            if results['meta']['code'] == 200:
                if len(results['response']['groups'][0]['items']) > 0:
                    return self.HandleFourSquarePlacesResult(results['response']['groups'][0]['items'])
                else:
                    Notify("Error", "No results found near the selected area.")
            elif results['meta']['code'] == 400:
                log("LIMIT EXCEEDED")
            else:
                log("ERROR")
        else:
            log("ERROR")
        return [], ""

    def SelectCategory(self):
        url = "https://api.foursquare.com/v2/venues/categories?client_id=%s&client_secret=%s&v=20130815" % (FOURSQUARE_ID, FOURSQUARE_SECRET)
        results = Get_JSON_response(url, 7)
        modeselect = []
        modeselect.append("All Categories")
        for item in results["categories"]:
            modeselect.append(cleanText(item["name"]))
        categorydialog = xbmcgui.Dialog()
        provider_index = categorydialog.select("Choose Category", modeselect)
        if provider_index > 0:
            return results["categories"][provider_index - 1]["id"]
        elif provider_index > -1:
            return ""
        else:
            return None

    def SelectSection(self):
        Sections = {"topPicks": ADDON.getLocalizedString(32005),
                    "food": ADDON.getLocalizedString(32006),
                    "drinks": ADDON.getLocalizedString(32007),
                    "coffee": ADDON.getLocalizedString(32008),
                    "shops": ADDON.getLocalizedString(32009),
                    "arts": ADDON.getLocalizedString(32010),
                    "outdoors": ADDON.getLocalizedString(32011),
                    "sights": ADDON.getLocalizedString(32012),
                    "trending": ADDON.getLocalizedString(32013),
                    "specials": ADDON.getLocalizedString(32014),
                    "nextVenues": ADDON.getLocalizedString(32015)}
        modeselect = []
        modeselect.append("All Sections")
        for value in Sections.itervalues():
            modeselect.append(value)
        categorydialog = xbmcgui.Dialog()
        provider_index = categorydialog.select("Choose Section", modeselect)
        if provider_index > 0:
            return Sections.keys()[provider_index - 1]
        elif provider_index > -1:
            return ""
        else:
            return None
