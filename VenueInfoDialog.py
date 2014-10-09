import xbmcgui
import xbmc
from LastFM import LastFM
from Utils import *
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'


class VenueInfoDialog(xbmcgui.WindowXMLDialog):
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

    def onInit(self):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        LFM = LastFM()
        self.event = LFM.GetEventInfo(self.eventid)["event"]
        results = LFM.GetVenueEvents(self.event["venue"]["id"])
        self.itemlist, PinString = LFM.CreateVenueList(results)
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
            # gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).doModal()
            # artist = "65daysofstatic"
            # LFM = LastFM()
            # log("search for artist")
            # itemlist, self.PinString = LFM.GetArtistEvents(artist)
            # gui.c_places_list.reset()
            # gui.GetGoogleMapURLs()
            # gui.c_places_list.addItems(items=itemlist)
            xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (self.event["artists"]["headliner"]))


        elif controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
