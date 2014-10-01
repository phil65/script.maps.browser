import xbmcgui
import xbmc
from LastFM import LastFM
from Utils import *


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
        self.prop_list = []
        self.PinString = ""
        self.GetEventsPinString = ""
        self.itemlist = []
        self.GetEventsitemlist = []

    def onInit(self):
        LFM = LastFM()
        self.itemlist, PinString = LFM.GetVenueEvents(self.venueid)
        self.prop_list = simplejson.loads(self.itemlist[0].getProperty("item_info"))
        self.setControls()

    def setControls(self):
        self.getControl(self.C_TEXT_FIELD).setText(self.prop_list["description"])
        self.getControl(202).setLabel(self.prop_list["date"])
        self.getControl(203).setLabel(self.prop_list["name"])
        self.getControl(self.C_BIG_IMAGE).setImage(self.prop_list["thumb"])
        self.getControl(self.C_RIGHT_IMAGE).setImage(self.prop_list["venue_image"])
        self.getControl(204).setLabel(self.prop_list["street"])
        self.getControl(self.C_TITLE).setLabel(self.prop_list["eventname"])
        self.getControl(self.C_ARTIST_LIST).addItems(items=self.itemlist)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            artist = self.getControl(self.C_ARTIST_LIST).getSelectedItem().getProperty("artists")
            self.close()
            LFM = LastFM()
            self.GetEventsitemlist, self.GetEventsPinString = LFM.GetEvents(artist)
        elif controlID == 1001:
            self.close()
            log("show artist events on map")
            # gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).doModal()
            # artist = "65daysofstatic"
            # LFM = LastFM()
            # log("search for artist")
            # itemlist, self.PinString = LFM.GetEvents(artist)
            # gui.c_places_list.reset()
            # gui.GetGoogleMapURLs()
            # gui.c_places_list.addItems(items=itemlist)
            xbmc.executebuiltin("RunScript(script.maps.browser,artist=65daysofstatic)")


        elif controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
