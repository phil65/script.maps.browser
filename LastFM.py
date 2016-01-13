import xbmcgui
from ImageTags import *
from Utils import *
import urllib

GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
LASTFM_KEY = 'd942dd5ca4c9ee5bd821df58cf8130d4'
BASE_URL = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json' % (LASTFM_KEY)


class LastFM():

    def __init__(self):
        self.pin_string = ""

    def create_venue_list(self, results, return_proplist=False):
        letter = ord('A')
        count = 0
        events_list = []
        if "events" in results:
            if "@attr" in results["events"]:
                if not isinstance(results['events']['event'], list):
                    results['events']['event'] = [results['events']['event']]
                for event in results['events']['event']:
                    artists = event['artists']['artist']
                    if isinstance(artists, list):
                        my_arts = ' / '.join(artists)
                    else:
                        my_arts = artists
                    location = event['venue']['location']
                    lat = location['geo:point'].get('geo:lat')
                    lon = location['geo:point'].get('geo:long')
                    if lat and lon:
                        search_string = lat + "," + lon
                    elif location['street']:
                        search_string = location['city'] + " " + location['street']
                    elif location['city']:
                        search_string = location['city'] + " " + event['venue']['name']
                    else:
                        search_string = event['venue']['name']
                    google_map = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
                    address_formatted = location['street'] + "[CR]" + location['city'] + "[CR]" + location['country']
                    description = unicode(cleanText(event['description']))
                    if my_arts != event['artists']['headliner']:
                        description = "[B]" + my_arts + "[/B][CR]" + description
                    prop_list = {"date": event['startDate'][:-8],
                                 "name": event['venue']['name'],
                                 "venue_id": event['venue']['id'],
                                 "event_id": event['id'],
                                 "street": location['street'],
                                 "eventname": event['title'],
                                 "website": event['website'],
                                 "description": description,
                                 "city": location['city'],
                                 "country": location['country'],
                                 "address": address_formatted,
                                 "lon": lon,
                                 "lat": lat,
                                 "index": str(count),
                                 "artists": my_arts,
                                 "sortletter": chr(letter),
                                 "googlemap": google_map,
                                 "artist_image": event['image'][-1]['#text'],
                                 "venue_image": event['venue']['image'][-1]['#text'],
                                 "headliner": event['artists']['headliner'],
                                 "thumb": event['venue']['image'][-1]['#text'],
                                 "label": event['venue']['name'],
                                 "label2": event['startDate'][:-8]}
                    events_list.append(prop_list)
                    if count < 26:
                        self.pin_string = self.pin_string + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                    else:
                        self.pin_string = self.pin_string + "&markers=color:blue%7C" + lat + "," + lon
                    count += 1
                    letter += 1
            else:
                Notify("Error", "No concerts found")
        elif "error" in results:
            Notify("Error", results["message"])
        else:
            log("Error when handling LastFM results")
            prettyprint(results)
        return events_list, self.pin_string

    def get_artist_events(self, artist, pastevents=False):
        if pastevents:
            # url = 'method=artist.getpastevents&mbid=%s&page=1&limit=26' % (id)
            url = '&method=artist.getpastevents&autocorrect=1&artist=%s&page=1&limit=26' % (urllib.quote(artist))
        else:
            # url = 'method=artist.getevents&mbid=%s' % (id)
            url = '&method=artist.getevents&autocorrect=1&artist=%s&limit=26' % (urllib.quote(artist))
        return Get_JSON_response(BASE_URL + url)

    def get_near_events(self, lat="", lon="", radius=30, tag="", only_festivals=False):
        if only_festivals:
            only_festivals = "1"
        else:
            only_festivals = "0"
        url = '&method=geo.getevents&festivalsonly=%s&page=1&limit=26' % (only_festivals)
        if tag:
            url = url + '&tag=%s' % (urllib.quote_plus(tag))
        if lat:
            url = url + '&lat=%s&long=%s&distance=%i' % (lat, lon, radius)  # &distance=60
        return Get_JSON_response(BASE_URL + url)

    def select_category(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        url = '&method=tag.getTopTags'
        results = Get_JSON_response(BASE_URL + url, 7)
        modeselect = ["All Categories"]
        for item in results["toptags"]["tag"]:
            modeselect.append(cleanText(item["name"]))
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        index = xbmcgui.Dialog().select("Choose Category", modeselect)
        if index > 0:
            return results["toptags"]["tag"][index - 1]["name"]
        elif index == 0:
            return ""
        else:
            return None

    def get_venue_events(self, venueid=""):
        url = '&method=venue.getevents&venue=%s' % (venueid)
        return Get_JSON_response(BASE_URL + url)

    def get_event_info(self, eventid=""):
        url = '&method=event.getinfo&event=%s' % (eventid)
        return Get_JSON_response(BASE_URL + url)

    def get_venue_id(self, venuename=""):
        url = '&method=venue.search&venue=%s' % (urllib.quote_plus(venuename))
        results = Get_JSON_response(BASE_URL + url)
        matches = results["results"]["venuematches"]
        if isinstance(matches["venue"], list):
            return matches["venue"][0]["id"]
        else:
            return matches["venue"]["id"]


class LastFMDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_ARTIST_LIST = 500
    LFM = LastFM()

    @busy_dialog
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.venue_id = kwargs.get('venueid')
        self.event_id = kwargs.get('eventid')
        self.event = []
        self.pin_string = ""
        self.events_pin_string = ""
        self.item_list = []
        self.events_items = []
        self.event = self.LFM.get_event_info(self.event_id)["event"]
        self.results = self.LFM.get_venue_events(self.event["venue"]["id"])
        self.item_list, self.pin_string = self.LFM.create_venue_list(self.results)

    def onInit(self):
        self.set_labels()
        self.getControl(self.C_ARTIST_LIST).addItems(items=create_listitems(self.item_list))

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def set_labels(self):
        if isinstance(self.event['artists']['artist'], list):
            artists = ' / '.join(self.event['artists']['artist'])
        else:
            artists = self.event['artists']['artist']
        description = "[B]Artists:[/B][CR]%s[CR][CR]%s" % (artists, cleanText(self.event["description"]))
        location = self.event['venue']['location']
        if location['geo:point']['geo:long']:
            lon = location['geo:point']['geo:long']
            lat = location['geo:point']['geo:lat']
            search_string = lat + "," + lon
        elif location['street']:
            search_string = location['city'] + " " + location['street']
        elif location['city']:
            search_string = location['city'] + " " + self.event['venue']['name']
        else:
            search_string = self.event['venue']['name']
        if "tags" in self.event:
            tags = " / ".join(self.event['tags']['tag'])
        self.google_map = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
        self.getControl(200).setText(description)
        self.getControl(202).setLabel(self.event['startDate'][:-8])
        self.getControl(203).setLabel(self.event["venue"]["name"])
        self.getControl(210).setImage(self.event['venue']['image'][-1]['#text'])
        self.getControl(212).setImage(self.event['image'][-1]['#text'])
        self.getControl(211).setImage(self.google_map)
        self.getControl(204).setLabel(location['street'])
        self.getControl(201).setLabel(self.event["title"])

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            artist = self.getControl(self.C_ARTIST_LIST).getSelectedItem().getProperty("headliner")
            self.close()
            if xbmc.getCondVisibility("Window.IsActive(script-Maps Browser-main.xml)"):
                results = self.LFM.get_artist_events(artist)
                self.events_items, self.events_pin_string = self.LFM.create_venue_list(results)
            else:
                xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (artist))
        elif controlID == 1001:
            self.close()
            log("show artist events on map")
            if xbmc.getCondVisibility("Window.IsActive(script-Maps Browser-main.xml)"):
                results = self.LFM.get_artist_events(self.event["artists"]["headliner"])
                self.events_items, self.events_pin_string = self.LFM.create_venue_list(results)
            else:
                xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (self.event["artists"]["headliner"]))
        elif controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
