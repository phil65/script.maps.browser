import xbmcgui
import xbmc
from LastFM import LastFM
from Utils import *
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'


class VenueInfoDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_TEXT_FIELD = 200
    C_TITLE = 201
    C_BIG_IMAGE = 211
    C_RIGHT_IMAGE = 210
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
        # prettyprint(results)
        self.event = LFM.GetEventInfo(self.eventid)["event"]
        prettyprint(self.event)
        results = LFM.GetVenueEvents(self.event["venue"]["id"])
        prettyprint(results)
        self.itemlist, PinString = LFM.CreateVenueList(results)
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
        self.googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
        self.setControls()
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def setControls(self):
        self.getControl(self.C_TEXT_FIELD).setText(cleanText(self.event["description"]))
        self.getControl(202).setLabel(self.event['startDate'][:-8])
        self.getControl(203).setLabel(self.event["venue"]["name"])
        self.getControl(self.C_BIG_IMAGE).setImage(self.event['venue']['image'][-1]['#text'])
        self.getControl(self.C_RIGHT_IMAGE).setImage(self.googlemap)
        self.getControl(204).setLabel(self.event['venue']['location']['street'])
        self.getControl(self.C_TITLE).setLabel(self.event["title"])
        self.getControl(self.C_ARTIST_LIST).addItems(items=self.itemlist)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            artist = self.getControl(self.C_ARTIST_LIST).getSelectedItem().getProperty("artists")
            self.close()
            LFM = LastFM()
            results = LFM.GetArtistEvents(artist)
            self.GetEventsitemlist, self.GetEventsPinString = LFM.CreateVenueList(results)
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
