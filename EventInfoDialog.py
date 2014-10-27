import xbmcgui
from Eventful import Eventful
from Utils import *


class EventInfoDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_TEXT_FIELD = 200
    C_TITLE = 201
    C_BIG_IMAGE = 211
    C_RIGHT_IMAGE = 210
    C_ARTIST_LIST = 500

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.eventful_id = kwargs.get('eventful_id')
        self.foursquare_id = kwargs.get('foursquare_id')
        if self.eventful_id:
            EF = Eventful()
            self.prop_list = EF.GetVenueInfo(self.eventful_id)
            self.event_list = self.prop_list["events"]["event"]
            prettyprint(self.event_list)
        elif self.foursquare_id:
            pass
        self.PinString = ""
        self.itemlist = []

    def onInit(self):
        self.setControls()

    def setControls(self):
        self.getControl(self.C_TEXT_FIELD).setText(self.prop_list["description"])
     #   self.getControl(202).setLabel(self.prop_list["date"])
        self.getControl(self.C_TITLE).setLabel(self.prop_list["name"])
        self.getControl(self.C_BIG_IMAGE).setImage(self.prop_list["thumb"])
    #    self.getControl(self.C_RIGHT_IMAGE).setImage(self.prop_list["venue_image"])
    #    self.getControl(204).setLabel(self.prop_list["street"])
    #    self.getControl(self.C_TITLE).setLabel(self.prop_list["eventname"])
    #    self.getControl(self.C_ARTIST_LIST).addItems(items=self.itemlist)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            self.close()

    def onFocus(self, controlID):
        pass
