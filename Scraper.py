    # code for FourSquare Scraping based on script.maps by a.a.alsaleh. credits to him.
import xbmc
import os
import sys
import xbmcgui
import xbmcaddon
import urllib
from default import dialog_select_UI
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
__addonpath__ = __addon__.getAddonInfo('path')

Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
foursquare_id = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
foursquare_secret = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
factual_key = 'n1yQsp5q68HLgKSYkBmRSWG710KI0IzlQS55hOIY'
factual_secret = '8kG0Khj87JfcNiabqmixuQYuGgDUvu1PnWN5IVca'
wunderground_key = "xx"
bing_key = 'Ai8sLX5R44tf24_2CGmbxTYiIX6w826dsCVh36oBDyTmH21Y6CxYEqtrV9oYoM6O'
max_limit = 25


# def GetRadarImage(self, lat, lon):
#     url = "http://api.wunderground.com/api/%s/animatedradar/image.gif?centerlat=%s&centerlon=%s&radius=100&width=280&height=280&newmaps=0" % (wunderground_key, str(self.lat), str(self.lon))
#     pass

# def GetBingMap(self):
   # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s?mapSize=800,600&key=%s' % (urllib.quote(self.search_string),bing_key)
    # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/5?key=%s' % (self.lat,self.lon, bing_key)
   ##         'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/%i?fmt=%s&key=%s' % (self.lat, self.lon, self.zoom_level, self._format, bing_key)
    # log(url)
    # return url


def GetGeoCodes(self, show_dialog, search_string):
    try:
        search_string = urllib.quote_plus(search_string)
        url = 'https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&address=%s' % (search_string)
        log("Google Geocodes Search:" + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
        events = []
        for item in results["results"]:
            locationinfo = item["geometry"]["location"]
            lat = str(locationinfo["lat"])
            lon = str(locationinfo["lng"])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=1&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
            event = {'generalinfo': item['formatted_address'],
                     'lat': lat,
                     'lon': lon,
                     'map': lon,
                     'preview': googlemap,
                     'id': item['formatted_address']}
            events.append(event)
        first_hit = results["results"][0]["geometry"]["location"]
        if show_dialog:
            if len(results["results"]) > 1:  # open dialog when more than one hit
                w = dialog_select_UI('DialogSelect.xml', __addonpath__, listing=events)
                w.doModal()
                log(w.lat)
                return (w.lat, w.lon)
            elif len(results["results"]) == 1:
                return (first_hit["lat"], first_hit["lng"])  # no window when only 1 result
            else:
                return (self.lat, self.lon)  # old values when no hit
        else:
            return (first_hit["lat"], first_hit["lng"])
    except Exception as e:
        log(e)
        return ("", "")


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
        if not "name" in venue:
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
        googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
        prop_list = {"id": str(venue['id']),
                     "distance": str(venue['location']['distance']),
                     "visited": str(venue['stats']['usersCount']),
                     "twitter": venue['contact'].get('twitter', ""),
                     "eventname": formattedAddress,
                     "description": formattedAddress,
                     "name": venue['name'],
                     "icon": icon,
                     "photo": photo,
                     "Venue_Image": icon,
                     "GoogleMap": googlemap,
                     "index":  str(count),
                     "sortletter": chr(letter),
                     "lat": lat,
                     "lon": lon,
                     "phone": venue['contact'].get('phone', ""),
                     "comments": str(venue['stats']['tipCount'])}
        item = xbmcgui.ListItem(venue['name'])
        for key, value in prop_list.iteritems():
            item.setProperty(key, value)
        item.setProperty("item_info", simplejson.dumps(prop_list))
        if photo is not "":
            item.setArt({'thumb': photo})
        else:
            item.setArt({'thumb': icon})
        item.setLabel(venue['name'])
        item.setLabel2(venue['name'])
        self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
        places_list.append(item)
        count += 1
        letter += 1
        if count > max_limit:
            break
    return places_list


def GetPlacesList(self, lat, lon, query="", categoryid=""):
    base_url = "https://api.foursquare.com/v2/venues/search?limit=25&client_id=%s&client_secret=%s&v=20130815" % (foursquare_id, foursquare_secret)
    url = '&ll=%.8f,%.8f' % (lat, lon)
    if query is not "":
        url = url + "&query=%s" % (query)
    if categoryid is not "":
        url = url + "&categoryId=%s" % (categoryid)
    results = Get_JSON_response(base_url, url)
    if results and 'meta' in results:
        if results['meta']['code'] == 200:
            return self.HandleFourSquarePlacesResult(results['response']['venues'])
        elif results['meta']['code'] == 400:
            Notify("Error", "LIMIT EXCEEDED")
        else:
            Notify("ERROR", "Could not get requested information")
    else:
        log("ERROR")
    return []


def GetPlacesListExplore(self, placetype):
    base_url = "https://api.foursquare.com/v2/venues/explore?limit=25&client_id=%s&client_secret=%s&v=20130815&venuePhotos=1" % (foursquare_id, foursquare_secret)
   # url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, foursquare_id, foursquare_secret)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
    url = '&ll=%.8f,%.8f&section=%s' % (self.lat, self.lon, placetype)
    results = Get_JSON_response(base_url, url)
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
    return []


def SelectCategory(self):
    url = "https://api.foursquare.com/v2/venues/categories?client_id=%s&client_secret=%s&v=20130815" % (foursquare_id, foursquare_secret)
    results = Get_JSON_response("", url, 7)
    modeselect = []
    prettyprint(results)
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
    Sections = {"topPicks": __language__(34005),
                "food": __language__(34006),
                "drinks": __language__(34007),
                "coffee": __language__(34008),
                "shops": __language__(34009),
                "arts": __language__(34010),
                "outdoors": __language__(34011),
                "sights": __language__(34012),
                "trending": __language__(34013),
                "specials": __language__(34014),
                "nextVenues": __language__(34015)}
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
