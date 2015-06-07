import xbmcgui
import xbmc
from LastFM import LastFM
from Utils import *
LFM = LastFM()


class VenueInfoDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_TEXT_FIELD = 200
    C_TITLE = 201
    C_BIG_IMAGE = 211
    C_RIGHT_IMAGE = 210
    C_ARTIST_LIST = 500

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.venue_id = kwargs.get('venueid')
        self.prop_list = []
        self.pin_string = ""
        self.events_pin_string = ""
        self.item_list = []
        self.events_items = []
        self.item_list, self.pin_string = LFM.get_venue_events(self.venue_id)

    def onInit(self):
        self.prop_list = simplejson.loads(self.item_list[0].getProperty("item_info"))
        self.set_controls()

    def set_controls(self):
        self.getControl(self.C_TEXT_FIELD).setText(self.prop_list["description"])
        self.getControl(202).setLabel(self.prop_list["date"])
        self.getControl(203).setLabel(self.prop_list["name"])
        self.getControl(self.C_BIG_IMAGE).setImage(self.prop_list["thumb"])
        self.getControl(self.C_RIGHT_IMAGE).setImage(self.prop_list["venue_image"])
        self.getControl(204).setLabel(self.prop_list["street"])
        self.getControl(self.C_TITLE).setLabel(self.prop_list["eventname"])
        self.getControl(self.C_ARTIST_LIST).addItems(items=self.item_list)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            artist = self.getControl(self.C_ARTIST_LIST).getSelectedItem().getProperty("artists")
            self.close()
            results = LFM.get_artist_events(artist)
            self.events_items, self.events_pin_string = LFM.create_venue_list(results)
        elif controlID == 1001:
            self.close()
            log("show artist events on map")
            if xbmc.getInfoLabel("Window.IsActive()"):
                pass
            else:
                xbmc.executebuiltin("RunScript(script.maps.browser,artist=%s)" % (xbmc.getInfoLabel("Window(home).Property(headliner)")))
        elif controlID == 1002:
            pass

    def onFocus(self, controlID):
        pass
