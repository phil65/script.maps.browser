import xbmcgui
from Utils import *

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString
__addonpath__ = __addon__.getAddonInfo('path')


class Search_Select_Dialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.items = kwargs.get('listing')
        self.lon = ''
        self.lat = ''

    def onInit(self):
        self.list = self.getControl(6)
        self.list.controlLeft(self.list)
        self.list.controlRight(self.list)
        self.getControl(3).setVisible(False)
        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(__language__(32015))
        self.list.addItems(self.items)
        self.setFocus(self.list)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID == 6 or controlID == 3:
            self.lat = self.list.getSelectedItem().getProperty("lat")
            self.lon = self.list.getSelectedItem().getProperty("lon")
            self.close()

    def onFocus(self, controlID):
        pass
