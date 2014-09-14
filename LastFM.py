import sys
import xbmcgui
import xbmcaddon
import xbmcvfs
from ImageTags import *
from Utils import *
import urllib
import time
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
__addonpath__ = __addon__.getAddonInfo('path')

googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
max_limit = 25


class LastFM():

    def __init__(self):
        pass

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
                    googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
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
        results = self.GetLastFMData(url)
      #  prettyprint(results)
        return self.CreateVenueList(results)

    def GetNearEvents(self, lat="", lon="", tag=False, festivalsonly=False):
        if festivalsonly:
            festivalsonly = "1"
        else:
            festivalsonly = "0"
        url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
        if tag:
            url = url + '&tag=%s' % (urllib.quote_plus(tag))
        if lat:
            url = url + '&lat=%s&long=%s&distance=30' % (lat, lon)  # &distance=60
        results = self.GetLastFMData(url)
        return self.CreateVenueList(results)
