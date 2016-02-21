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

    def get_venue_events(self, venue_id=""):
        url = '&method=venue.getevents&venue=%s' % (venue_id)
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
        super(LastFMDialog, self).__init__(*args, **kwargs)
        self.venue_id = kwargs.get('venue_id')
        self.event_id = kwargs.get('eventid')
        self.event = []
        self.events_pin_string = ""
        self.events_items = []
        self.event = self.LFM.get_event_info(self.event_id)["event"]
        self.results = self.LFM.get_venue_events(self.event["venue"]["id"])

    def onInit(self):
        self.set_labels()

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
        pass

    def onFocus(self, controlID):
        pass
