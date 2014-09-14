    # code for FourSquare Scraping based on script.maps by a.a.alsaleh. credits to him.
import xbmc
import os
import sys
import time
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib
from default import dialog_select_UI
from ImageTags import *
from PIL import Image
from Utils import *
from math import cos, pow, pi
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
googlemaps_key_streetview = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'
googlemaps_key_places = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
foursquare_id = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
foursquare_secret = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
factual_key = 'n1yQsp5q68HLgKSYkBmRSWG710KI0IzlQS55hOIY'
factual_secret = '8kG0Khj87JfcNiabqmixuQYuGgDUvu1PnWN5IVca'
eventful_key = 'Nw3rh3mXn8RhMQNK'
wunderground_key = "xx"
max_limit = 25


# def GetRadarImage(self, lat, lon):
#     url = "http://api.wunderground.com/api/%s/animatedradar/image.gif?centerlat=%s&centerlon=%s&radius=100&width=280&height=280&newmaps=0" % (wunderground_key, str(self.lat), str(self.lon))
#     pass


def GetNearEvents(self, tag=False, festivalsonly=False):
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
    if tag:
        url = url + '&tag=%s' % (urllib.quote_plus(tag))
    if self.lat:
        url = url + '&lat=%s&long=%s&distance=30' % (self.lat, self.lon)  # &distance=60
    results = GetLastFMData(self, url)
    return self.CreateVenueList(results)


def CreateVenueList(self, results):
    PinString = ""
    letter = ord('A')
    count = 0
    events_list = list()
  #  prettyprint(results)
    if "events" in results:
        if "@attr" in results["events"]:
            if int(results["events"]["@attr"]["total"]) == 1:
                results['events']['event'] = [results['events']['event']]
            for event in results['events']['event']:
                artists = event['artists']['artist']
                if isinstance(artists, list):
                    my_arts = ' / '.join(artists)
                else:
                    my_arts = artists
                lat = ""
                lon = ""
                if event['venue']['location']['geo:point']['geo:long']:
                    lon = event['venue']['location']['geo:point']['geo:long']
                    lat = event['venue']['location']['geo:point']['geo:lat']
                    search_string = lat + "," + lon
                elif event['venue']['location']['street']:
                    search_string = event['venue']['location']['city'] + " " + event['venue']['location']['street']
                elif event['venue']['location']['city']:
                    search_string = event['venue']['location']['city'] + " " + event['venue']['name']
                else:
                    search_string = event['venue']['name']
                googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (
                    search_string, search_string, googlemaps_key_normal)
                item = xbmcgui.ListItem(event['venue']['name'])
                formattedAddress = event['venue']['location']['street'] + "[CR]" + event['venue']['location']['city'] + "[CR]" + event['venue']['location']['country']
                prop_list = {"date": event['startDate'],
                             "name": event['venue']['name'],
                             "id": event['startDate'],
                             "street": event['venue']['location']['street'],
                             "eventname": event['title'],
                             "website": event['website'],
                             "description": cleanText(event['description']),
                             "city": event['venue']['location']['city'],
                             "country": event['venue']['location']['country'],
                             "address": formattedAddress,
                             "lon": lon,
                             "lat": lat,
                             "index": str(count),
                             "artists": my_arts,
                             "sortletter": chr(letter),
                             "googlemap": googlemap,
                             "artist_image": event['image'][-1]['#text'],
                             "venue_image": event['venue']['image'][-1]['#text'],
                             "headliner": event['artists']['headliner'],
                             "thumb": event['venue']['image'][-1]['#text'],
                             "label": event['venue']['name'],
                             "label2": event['startDate']}
                for key, value in prop_list.iteritems():
                    item.setProperty(key, value)
                item.setProperty("item_info", simplejson.dumps(prop_list))
                item.setArt({'thumb': event['venue']['image'][-1]['#text']})
                item.setLabel(event['venue']['name'])
                item.setLabel2(event['startDate'])
                events_list.append(item)
                PinString = PinString + "&markers=color:blue%7Clabel:" + \
                    chr(letter) + "%7C" + lat + "," + lon
                count += 1
                letter += 1
                if count > max_limit:
                    break
        else:
            Notify("Error", "No concerts found")
    elif "error" in results:
        Notify("Error", results["message"])
    else:
        log("Error when handling LastFM results")
        prettyprint(results)
    return events_list, PinString


def GetImages(self, path=""):
    PinString = "&markers=color:blue"
    letter = ord('A')
    count = 0
    images_list = list()
    prettyprint(xbmcvfs.listdir(path))
    for filename in xbmcvfs.listdir(path)[-1]:
        try:
            img = Image.open(path + filename)
            exif_data = get_exif_data(img)
            lat, lon = get_lat_lon(exif_data)
            if lat:
                prop_list = {"name": filename,
                             "lat": str(lat),
                             "lon": str(lon),
                             "thumb": path + filename,
                             "index": path + str(count),
                             "sortletter": chr(letter),
                             }
                item = xbmcgui.ListItem(filename)
                item.setLabel(filename)
                item.setProperty("name", filename)
                item.setProperty("lat", str(lat))
                item.setProperty("lon", str(lon))
                item.setProperty("index", str(count))
                item.setArt({'thumb': path + filename})
                if len(PinString) < 1850:
                    PinString = PinString + "%7C" + str(lat) + "," + str(lon)
                    item.setProperty("sortletter", chr(letter))
                    letter += 1
                images_list.append(item)
                count += 1
        except Exception as e:
            log("Error when handling GetImages results")
            log(e)
    return images_list, PinString


def GetLastFMData(self, url="", cache_days=1):
    from base64 import b64encode
    filename = b64encode(url).replace("/", "XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&%s' % (lastfm_apikey, url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
        save_to_file(results, filename, Addon_Data_Path)
        return results


def GetEvents(self, id, pastevents=False):
    id = urllib.quote(id)
    if pastevents:
 #       url = 'method=artist.getpastevents&mbid=%s' % (id)
        url = 'method=artist.getpastevents&autocorrect=1&artist=%s' % (id)
    else:
  #      url = 'method=artist.getevents&mbid=%s' % (id)
        url = 'method=artist.getevents&autocorrect=1&artist=%s' % (id)
    results = GetLastFMData(self, url)
  #  prettyprint(results)
    return self.CreateVenueList(results)


def GetGoogleMapURLs(self):
    try:
        if self.street_view is True:
            size = "320x200"
        else:
            size = "640x400"
        if self.lat and self.lon:
            self.search_string = str(self.lat) + "," + str(self.lon)
        else:
            self.search_string = urllib.quote_plus(self.location.replace('"', ''))
        base_url = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&format=%s&' % (__addon__.getSetting("ImageFormat"))
        self.GoogleMapURL = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (self.type, self.search_string, self.zoom_level, self.search_string, size, googlemaps_key_normal) + self.PinString
        zoom = 120 - int(self.zoom_level_streetview) * 6
        base_url = 'http://maps.googleapis.com/maps/api/streetview?&sensor=false&format=%s&' % (__addon__.getSetting("ImageFormat"))
        self.GoogleStreetViewURL = base_url + 'location=%s&size=640x400&fov=%s&key=%s&heading=%s&pitch=%s' % (self.search_string, str(zoom), googlemaps_key_streetview, str(self.direction), str(self.pitch))
        setWindowProperty(self.window, self.prefix + 'location', self.location)
        setWindowProperty(self.window, self.prefix + 'lat', str(self.lat))
        setWindowProperty(self.window, self.prefix + 'lon', str(self.lon))
        setWindowProperty(self.window, self.prefix + 'zoomlevel', str(self.zoom_level))
        setWindowProperty(self.window, self.prefix + 'direction', str(self.direction / 18))
        setWindowProperty(self.window, self.prefix + 'type', self.type)
        setWindowProperty(self.window, self.prefix + 'aspect', self.aspect)
        setWindowProperty(self.window, self.prefix + 'map_image', self.GoogleMapURL)
        setWindowProperty(self.window, self.prefix + 'streetview_image', self.GoogleStreetViewURL)
        setWindowProperty(self.window, self.prefix + 'NavMode', "")
        setWindowProperty(self.window, self.prefix + 'streetview', "")
        hor_px = int(size.split("x")[0])
        ver_px = int(size.split("x")[1])
        dLongitude = (hor_px / 256) * (360 / pow(2, self.zoom_level))
        pixels_per_kilometer = (ver_px * 1000) / ((cos(self.lat * pi / 180) * 2 * pi * 6378137) / (256 * pow(2, self.zoom_level)) * 600)
        log("dLongitude: " + str(dLongitude) + "  pixels_per_kilometer: " + str(pixels_per_kilometer))
        # import MercatorProjection
        # centerPoint = MercatorProjection.G_LatLng(self.lat, self.lon)
        # corners = MercatorProjection.getCorners(centerPoint, zoom, mapWidth, mapHeight)
        # prettyprint(corners)
        if self.street_view:
            setWindowProperty(self.window, self.prefix + 'streetview', "True")
        if self.NavMode_active:
            setWindowProperty(self.window, self.prefix + 'NavMode', "True")
    except Exception as e:
        log(e)

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
            search_string = str(locationinfo["lat"]) + "," + str(locationinfo["lng"])
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=1&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (
                search_string, search_string, googlemaps_key_normal)
            event = {'generalinfo': item['formatted_address'],
                     'lat': str(locationinfo["lat"]),
                     'lon': str(locationinfo["lng"]),
                     'map': str(locationinfo["lng"]),
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


def GetLocationCoordinates(self):
    try:
        url = 'http://www.telize.com/geoip'
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
        self.lat = results["latitude"]
        self.lon = results["longitude"]
    except Exception as e:
        log(e)


def HandleFourSquarePlacesResult(self, results):
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
                     "GoogleMap": icon,
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


def HandleEventfulEventResult(self, results):
    places_list = list()
    letter = ord('A')
    count = 0
    prettyprint(results)
    for venue in results:
        formattedAddress = venue["venue_address"]
        lat = str(venue['latitude'])
        lon = str(venue['longitude'])
        if venue["image"] is not None:
            photo = venue["image"]["large"]["url"]
        else:
            photo = ""
        if (venue["start_time"] == venue["stop_time"]) or (venue["stop_time"] is None):
            date = venue["start_time"]
        else:
            date = venue["start_time"] + " - " + venue["stop_time"]
        prop_list = {"id": str(venue['id']),
                     "eventname": venue['title'],
                     "description": cleanText(venue['description']),
                     "name": venue['venue_name'],
                     "photo": photo,
                     "date": date,
                     "address": formattedAddress,
                     "Venue_Image": photo,
                     "venue_id": venue['venue_id'],
                     "GoogleMap": photo,
                     "index":  str(count),
                     "sortletter": chr(letter),
                     "lat": lat,
                     "lon": lon}
        item = xbmcgui.ListItem(venue['venue_name'])
        for key, value in prop_list.iteritems():
            item.setProperty(key, value)
        item.setProperty("item_info", simplejson.dumps(prop_list))
        item.setArt({'thumb': photo})
        item.setLabel(venue['venue_name'])
        item.setLabel2(date)
        self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
        places_list.append(item)
        count += 1
        letter += 1
        if count > max_limit:
            break
    return places_list


def GetPlacesList(self, query=""):
    if query is not "":
        url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=25&query=%s&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, query, foursquare_id, foursquare_secret)
    else:
        url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=25&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, foursquare_id, foursquare_secret)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
    self.PinString = ""
    response = GetStringFromUrl(url)
    results = simplejson.loads(response)
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


def GetEventfulList(self, query=""):
    if query is not "":
        url = 'http://api.eventful.com/json/events/search?where=%.8f,%.8f&image_sizes=large&include=price&page_size=25date&sort_order=date&within=30&date=Future&query=%s&app_key=%s' % (self.lat, self.lon, query, eventful_key)
    else:
        url = 'http://api.eventful.com/json/events/search?where=%.8f,%.8f&image_sizes=large&include=price&page_size=25date&sort_order=date&within=30&date=Future&app_key=%s' % (self.lat, self.lon, eventful_key)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
    self.PinString = ""
    response = GetStringFromUrl(url)
    results = simplejson.loads(response)
    return self.HandleEventfulEventResult(results['events']['event'])


def GetPlacesListExplore(self, placetype):
   # url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, foursquare_id, foursquare_secret)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
    url = 'https://api.foursquare.com/v2/venues/explore?ll=%.8f,%.8f&section=%s&limit=25&venuePhotos=1&client_id=%s&client_secret=%s&v=20130815' % (
        self.lat, self.lon, placetype, foursquare_id, foursquare_secret)
    response = GetStringFromUrl(url)
    results = simplejson.loads(response)
    self.PinString = ""
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


def GetGooglePlacesList(self, locationtype):
    location = str(self.lat) + "," + str(self.lon)
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s&types=%s&radius=500&key=%s' % (location, locationtype, googlemaps_key_places)
 #   log(url)
    response = GetStringFromUrl(url)
    results = simplejson.loads(response)
    places_list = list()
    PinString = ""
    letter = ord('A')
    count = 0
    if "results" in results:
        for v in results['results']:
            item = xbmcgui.ListItem(v['name'])
            try:
                photo_ref = v['photos'][0]['photo_reference']
                photo = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s' % (photo_ref, googlemaps_key_places)
            except:
                photo = ""
            typestring = ""
            typestring = " / ".join(v['types'])
            item.setArt({'thumb': photo})
            item.setArt({'icon': v['icon']})
            item.setLabel(v['name'])
            item.setProperty('name', v['name'])
            item.setProperty('description', v['vicinity'])
            item.setLabel2(typestring)
            item.setProperty("sortletter", chr(letter))
            item.setProperty("index", str(count))
            lat = str(v['geometry']['location']['lat'])
            lon = str(v['geometry']['location']['lng'])
            item.setProperty("lat", lat)
            item.setProperty("lon", lon)
            item.setProperty("index", str(count))
            if "rating" in v:
                rating = str(v['rating'] * 2.0)
                item.setProperty("rating", rating)
            PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places_list.append(item)
            count += 1
            letter += 1
            if count > max_limit:
                break
      #  difference_lat = results['response']['suggestedBounds']['ne']['lat'] - results['response']['suggestedBounds']['sw']['lat']
       # difference_lon = results['response']['suggestedBounds']['ne']['lng'] - results['response']['suggestedBounds']['sw']['lng']
       # log(difference_lat)
    elif results['meta']['code'] == 400:
        log("LIMIT EXCEEDED")
    else:
        log("ERROR")
    return PinString, places_list
