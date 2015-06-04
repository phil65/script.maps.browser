#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2014 Philipp Temminghoff (philipptemminghoff@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import xbmc
import xbmcaddon
from Utils import *
from LastFM import LastFMDialog
from gui import GUI

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo('name')


if __name__ == '__main__':
    for arg in sys.argv:
        param = arg.lower()
        xbmc.log("param = " + param)
        if param.startswith('venueid='):
            venueid = (param[8:])
            dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, venueid=venueid)
            dialog.doModal()
            break
        if param.startswith('eventid='):
            eventid = (param[8:])
            dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, eventid=eventid)
            dialog.doModal()
            break
    else:
        gui = GUI(u'script-%s-main.xml' % ADDON_NAME, ADDON_PATH)
        gui.doModal()
        del gui
