import sys
import xbmcgui
import xbmcaddon
from ImageTags import *
from Utils import *
import urllib
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
base_url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json' % (lastfm_apikey)


class LastFM():

    def __init__(self):
        self.PinString = ""

    def CreateVenueList(self, results, return_proplist=False):
        letter = ord('A')
        count = 0
        events_list = list()
      #  prettyprint(results)
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
                    formattedAddress = event['venue']['location']['street'] + "[CR]" + event['venue']['location']['city'] + "[CR]" + event['venue']['location']['country']
                    description = cleanText(event['description'])
                    if my_arts != event['artists']['headliner']:
                        description = "[B]" + my_arts + "[/B][CR]" + description
                    prop_list = {"date": event['startDate'][:-8],
                                 "name": event['venue']['name'],
                                 "venue_id": event['venue']['id'],
                                 "event_id": event['id'],
                                 "street": event['venue']['location']['street'],
                                 "eventname": event['title'],
                                 "website": event['website'],
                                 "description": description,
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
                                 "label2": event['startDate'][:-8]}
                    item = CreateListItem(prop_list)
                    if return_proplist is True:
                        events_list.append(prop_list)
                    else:
                        events_list.append(item)
                    if count < 26:
                        self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                    else:
                        self.PinString = self.PinString + "&markers=color:blue%7C" + lat + "," + lon
                    count += 1
                    letter += 1
            else:
                Notify("Error", "No concerts found")
        elif "error" in results:
            Notify("Error", results["message"])
        else:
            log("Error when handling LastFM results")
            prettyprint(results)
        return events_list, self.PinString

    def GetArtistEvents(self, artist, pastevents=False):
        artist = urllib.quote(artist)
        if pastevents:
     #       url = 'method=artist.getpastevents&mbid=%s' % (id)
            url = '&method=artist.getpastevents&autocorrect=1&artist=%s&page=1&limit=26' % (artist)
        else:
      #      url = 'method=artist.getevents&mbid=%s' % (id)
            url = '&method=artist.getevents&autocorrect=1&artist=%s&limit=26' % (artist)
        results = Get_JSON_response(base_url, url)
        return results

    def GetNearEvents(self, lat="", lon="", radius=30, tag="", festivalsonly=False):
        if festivalsonly:
            festivalsonly = "1"
        else:
            festivalsonly = "0"
        url = '&method=geo.getevents&festivalsonly=%s&page=1&limit=26' % (festivalsonly)
        if (tag is not "") and (tag is not None):
            url = url + '&tag=%s' % (urllib.quote_plus(tag))
        if lat:
            url = url + '&lat=%s&long=%s&distance=%i' % (lat, lon, radius)  # &distance=60
        results = Get_JSON_response(base_url, url)
        return results

    def SelectCategory(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        url = '&method=tag.getTopTags'
        results = Get_JSON_response(base_url, url, 7)
        modeselect = []
        modeselect.append("All Categories")
        for item in results["toptags"]["tag"]:
            modeselect.append(cleanText(item["name"]))
        categorydialog = xbmcgui.Dialog()
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        provider_index = categorydialog.select("Choose Category", modeselect)
        if provider_index > 0:
            return results["toptags"]["tag"][provider_index - 1]["name"]
        elif provider_index > -1:
            return ""
        else:
            return None

    def GetVenueEvents(self, venueid=""):
        url = '&method=venue.getevents&venue=%s' % (venueid)
        results = Get_JSON_response(base_url, url)
        return results

    def GetEventInfo(self, eventid=""):
        url = '&method=event.getinfo&event=%s' % (eventid)
        results = Get_JSON_response(base_url, url)
        return results

    def GetVenueID(self, venuename=""):
        url = '&method=venue.search&venue=%s' % (urllib.quote_plus(venuename))
        results = Get_JSON_response(base_url, url)
  #     prettyprint(results["results"]["venuematches"])
        if len(results["results"]["venuematches"]) > 0:
            return results["results"]["venuematches"]["venue"][0]["id"]
        else:
            return None


class LastFMDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_ARTIST_LIST = 500

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.venueid = kwargs.get('venueid')
        self.eventid = kwargs.get('eventid')
        self.event = []
        self.PinString = ""
        self.GetEventsPinString = ""
        self.itemlist = []
        self.GetEventsitemlist = []
        LFM = LastFM()
        self.event = LFM.GetEventInfo(self.eventid)["event"]
        self.results = LFM.GetVenueEvents(self.event["venue"]["id"])
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.itemlist, self.PinString = LFM.CreateVenueList(self.results)

    def onInit(self):
        self.setLabels()
        self.getControl(self.C_ARTIST_LIST).addItems(items=self.itemlist)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def updateLabels(self, eventid):
        self.event = LFM.GetEventInfo(eventid)["event"]
        self.setLabels()

    def setLabels(self):
        if isinstance(self.event['artists']['artist'], list):
            artists = ' / '.join(self.event['artists']['artist'])
        else:
            artists = self.event['artists']['artist']
        website = ""
        description = "[B]Artists:[/B][CR]%s[CR][CR]%s" % (artists, cleanText(self.event["description"]))
        if self.event['venue']['location']['geo:point']['geo:long']:
            lon = self.event['venue']['location']['geo:point']['geo:long']
            lat = self.event['venue']['location']['geo:point']['geo:lat']
            search_string = lat + "," + lon
        elif self.event['venue']['location']['street']:
            search_string = self.event['venue']['location']['city'] + " " + self.event['venue']['location']['street']
        elif self.event['venue']['location']['city']:
            search_string = self.event['venue']['location']['city'] + " " + self.event['venue']['name']
        else:
            search_string = self.event['venue']['name']
        if "tags" in self.event:
            tags = " / ".join(self.event['tags']['tag'])
        self.googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
        self.getControl(200).setText(description)
        self.getControl(202).setLabel(self.event['startDate'][:-8])
        self.getControl(203).setLabel(self.event["venue"]["name"])
        self.getControl(210).setImage(self.event['venue']['image'][-1]['#text'])
        self.getControl(212).setImage(self.event['image'][-1]['#text'])
        self.getControl(211).setImage(self.googlemap)
        self.getControl(204).setLabel(self.event['venue']['location']['street'])
        self.getControl(201).setLabel(self.event["title"])

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            artist = self.getControl(self.C_ARTIST_LIST).getSelectedItem().getProperty("headliner")
            self.close()
            if xbmc.getCondVisibility("Window.IsActive(script-Maps Browser-main.xml)"):
                LFM = LastFM()
                results = LFM.GetArtistEvents(artist)
                self.GetEventsitemlist, self.GetEventsPinString = LFM.CreateVenueList(results)
            else:
                xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (artist))
        elif controlID == 1001:
            self.close()
            log("show artist events on map")
            if xbmc.getCondVisibility("Window.IsActive(script-Maps Browser-main.xml)"):
                # gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).doModal()
                # artist = "65daysofstatic"
                # LFM = LastFM()
                # log("search for artist")
                # itemlist, self.PinString = LFM.GetArtistEvents(artist)
                # gui.c_places_list.reset()
                # gui.GetGoogleMapURLs()
                # gui.c_places_list.addItems(items=itemlist)
                LFM = LastFM()
                results = LFM.GetArtistEvents(self.event["artists"]["headliner"])
                self.GetEventsitemlist, self.GetEventsPinString = LFM.CreateVenueList(results)
            else:
                xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (self.event["artists"]["headliner"]))


        elif controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
