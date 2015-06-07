# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from Utils import *
from LastFM import LastFMDialog
from gui import GUI


def StartInfoActions(infos, params):
    if "artistname" in params:
        params["artistname"] = params.get("artistname", "").split(" feat. ")[0].strip()
        params["artist_mbid"] = fetch_musicbrainz_id(params["artistname"])
    prettyprint(params)
    prettyprint(infos)
    if "prefix" in params and (not params["prefix"].endswith('.')) and (params["prefix"] is not ""):
        params["prefix"] = params["prefix"] + '.'
    # NOTICE: compatibility
    for info in infos:
        # data = []
        if info == 'venueinfo':
            HOME.setProperty('infodialogs.active', "true")
            dialog = LastFMDialog(u'script-%s-dialog.xml' % (ADDON_NAME), ADDON_PATH, venueid=params.get("id", ""), name=params.get("name", ""))
            dialog.doModal()
            HOME.clearProperty('infodialogs.active')
        elif info == 'eventinfo':
            HOME.setProperty('infodialogs.active', "true")
            dialog = LastFMDialog(u'script-%s-dialog.xml' % (ADDON_NAME), ADDON_PATH, eventid=params.get("id", ""), name=params.get("name", ""))
            dialog.doModal()
            HOME.clearProperty('infodialogs.active')
        elif info == "map":
            gui = GUI(u'script-%s-main.xml' % ADDON_NAME, ADDON_PATH)
            gui.doModal()
            del gui
