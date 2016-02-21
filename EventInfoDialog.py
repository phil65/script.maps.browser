# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

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
            self.prop_list = EF.get_venue_info(self.eventful_id)
            self.event_list = self.prop_list["events"]["event"]
            prettyprint(self.event_list)
        elif self.foursquare_id:
            pass
        self.pin_string = ""
        self.itemlist = []

    def onInit(self):
        self.setControls()

    def setControls(self):
        self.getControl(self.C_TEXT_FIELD).setText(self.prop_list["description"])
        self.getControl(self.C_TITLE).setLabel(self.prop_list["name"])
        self.getControl(self.C_BIG_IMAGE).setImage(self.prop_list["thumb"])

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == self.C_ARTIST_LIST:
            self.close()

    def onFocus(self, controlID):
        pass
