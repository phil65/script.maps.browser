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
