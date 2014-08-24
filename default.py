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

import os, re, sys, urllib, xbmc, xbmcaddon, xbmcgui
from math import sin, cos, radians
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
    
__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__language__     = __addon__.getLocalizedString

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
addon_name = addon.getAddonInfo('name')
bing_key =  'Ai8sLX5R44tf24_2CGmbxTYiIX6w826dsCVh36oBDyTmH21Y6CxYEqtrV9oYoM6O'


class GUI(xbmcgui.WindowXML):
    from Utils import *
    from Scraper import *
    CONTROL_SEARCH = 101
    CONTROL_STREET_VIEW = 102
    CONTROL_ZOOM_IN = 103
    CONTROL_ZOOM_OUT = 104
    CONTROL_MODE_ROADMAP = 105
    CONTROL_MODE_HYBRID = 106
    CONTROL_MODE_SATELLITE = 107
    CONTROL_MODE_TERRAIN = 108
    CONTROL_MAP_IMAGE = 109
    CONTROL_STREETVIEW_IMAGE = 110
    CONTROL_GOTO_PLACE = 111
    CONTROL_SELECT_PROVIDER = 112
    CONTROL_LEFT = 120
    CONTROL_RIGHT = 121
    CONTROL_UP = 122
    CONTROL_DOWN = 123
    CONTROL_PLACES_LIST = 200

    ACTION_CONTEXT_MENU = [117]
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    ACTION_SHOW_INFO = [11]
    ACTION_EXIT_SCRIPT = [13]
    ACTION_DOWN = [4]
    ACTION_UP = [3]
    ACTION_LEFT = [1]
    ACTION_RIGHT = [2]
    ACTION_0 = [58, 18]
    ACTION_PLAY = [79]
    ACTION_SELECT_ITEM = [7]

    def __init__(self, skin_file, addon_path):
        self.log('__init__')
            
    def onInit(self,startGUI = True):
        self.log('onInit')
        self.NavMode_active = False
        self.street_view = False
        self.search_string = ""
        self.zoom_level = 10
        self.zoom_level_streetview = 0
        self.type = "roadmap"
        self.lat = 0.0
        self.strlat = ""
        self.lon = 0.0
        self.strlon = ""
        self.location = ""
        self.PinString = ""
        self.direction = 0
        self.saved_id = 100
        self.aspect = "normal"
        self.prefix = ""
        self.GoogleMapURL = ""
        self.GoogleStreetViewURL = ""
        self.GetLocationCoordinates()
        self.location = str(self.lat) + "," + str(self.lon)
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.log("window = " + str(self.window))
        self.setWindowProperty('NavMode', '')
        self.setWindowProperty('streetview', '')
        for arg in sys.argv:
            param = arg.lower()
            self.log("param = " + param)
            if param.startswith('location='):
                self.location = (param[9:])
            elif param.startswith('lat='):
                self.strlat = (param[4:])
            elif param.startswith('lon='):
                self.strlon = (param[4:])
            elif param.startswith('type='):
                self.type = (param[5:])
            elif param.startswith('zoom='):
                self.zoom_level = (param[5:])
            elif param.startswith('aspect='):
                self.aspect = (param[7:])
            elif param.startswith('direction='):
                self.direction = (param[10:])
            elif param.startswith('prefix='):
                self.prefix = param[7:]
                if not self.prefix.endswith('.') and self.prefix <> "":
                    self.prefix = self.prefix + '.'
        if self.location == "geocode":
            self.ParseGeoTags()            
        self.GetGoogleMapURLs()
        if startGUI:
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
            self.getControls()
            self.c_places_list.reset()
            itemlist = self.GetPlacesList()
            self.GetGoogleMapURLs()
            try:
                self.c_places_list.addItems(items=itemlist)
                self.c_map_image.setImage(self.GoogleMapURL)
                self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            except Exception,e:
                self.log("Error: Exception in onInit with message:")
                self.log(e)
            settings = xbmcaddon.Addon(id='script.extendedinfo')
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            if not settings.getSetting('firststart') == "true":
                settings.setSetting(id='firststart', value='true')
                dialog = xbmcgui.Dialog()
                dialog.ok("Welcome to Maps Browser", " Press Menu button to toggle navigation mode", "Press Info button to change map type")
        self.log('onInit finished')

    def getControls(self):
        self.c_map_image = self.getControl(self.CONTROL_MAP_IMAGE)
        self.c_streetview_image = self.getControl(self.CONTROL_STREETVIEW_IMAGE)
        self.c_places_list = self.getControl(self.CONTROL_PLACES_LIST)

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_SHOW_INFO:
            if self.type == "roadmap":
                self.type = "satellite"
            elif self.type == "satellite":
                self.type = "hybrid"
            elif self.type == "hybrid":
                self.type = "terrain"
            else:
                self.type = "roadmap"
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)            
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.ToggleNavMode()
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.NavMode_active == True:
                self.setWindowProperty('NavMode', '')
                self.NavMode_active = False                
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif self.NavMode_active == True:
            self.log("lat: " + str(self.lat) + " lon: " + str(self.lon))
            if self.street_view == False:
                stepsize = 200.0 / float(self.zoom_level) / float(self.zoom_level) / float(self.zoom_level) / float(self.zoom_level)
                if action_id in self.ACTION_UP:
                    self.lat = float(self.lat) + stepsize
                elif action_id in self.ACTION_DOWN:
                    self.lat = float(self.lat) - stepsize           
                elif action_id in self.ACTION_LEFT:
                    self.lon = float(self.lon) - 2.0 * stepsize  
                elif action_id in self.ACTION_RIGHT:
                    self.lon = float(self.lon) + 2.0 * stepsize
                self.location = str(self.lat) + "," + str(self.lon)
                self.GetGoogleMapURLs()       
                self.c_map_image.setImage(self.GoogleMapURL)
                self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            else:
                stepsize = 0.0002
                radiantdirection = float(radians(self.direction))
                if action_id in self.ACTION_UP and self.street_view == True:
                    self.lat = float(self.lat) + cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) + sin(radiantdirection) * float(stepsize)
                elif action_id in self.ACTION_DOWN and self.street_view == True:
                    self.lat = float(self.lat) - cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) - sin(radiantdirection) * float(stepsize)     
                elif action_id in self.ACTION_LEFT and self.street_view == True:
                    if self.direction <= 0:
                        self.direction = 360
                    self.direction -= 18
                elif action_id in self.ACTION_RIGHT and self.street_view == True:
                    if self.direction >= 348:
                        self.direction = 0
                    self.direction += 18
                self.location = str(self.lat) + "," + str(self.lon)
                self.GetGoogleMapURLs()       
                self.c_streetview_image.setImage(self.GoogleStreetViewURL)
                self.c_map_image.setImage(self.GoogleMapURL)
              
    def onClick(self, controlId):
        if controlId == self.CONTROL_ZOOM_IN:
            self.ZoomIn()
        elif controlId == self.CONTROL_ZOOM_OUT:
            self.ZoomOut()
        elif controlId == self.CONTROL_SEARCH:
            self.SearchLocation()
        elif controlId == self.CONTROL_STREET_VIEW:
            self.ToggleStreetMode()
        elif controlId == self.CONTROL_MODE_ROADMAP:
            self.type ="roadmap"
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_MODE_SATELLITE:
            self.type ="satellite"
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_MODE_HYBRID:
            self.type ="hybrid"
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_MODE_TERRAIN:
            self.type ="terrain"
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_GOTO_PLACE:
            self.location = self.getWindowProperty("Location")
            self.lat, self.lon = self.GetGeoCodes(self.location)
            self.GetGoogleMapURLs()       
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_SELECT_PROVIDER:
            modeselect= []
            modeselect.append( "FourSquare" )
            modeselect.append( "Concerts" )
            modeselect.append( "Festivals" )
            modeselect.append( "Concert Search" )
            modeselect.append( "Reset" )
            dialogSelection = xbmcgui.Dialog()
            provider_index = dialogSelection.select( "Choose Places", modeselect )
            if provider_index == 0:
                self.c_places_list.reset()
                itemlist = self.GetPlacesList()
                self.c_places_list.addItems(items=itemlist)
            elif provider_index == 1:
                self.c_places_list.reset()
                self.c_places_list.addItems(items=self.GetNearEvents())
            elif provider_index == 2:
                self.c_places_list.reset()
                self.c_places_list.addItems(items=self.GetNearEvents(False,True))
            elif provider_index == 3:
                self.c_places_list.reset()
                search_string=xbmcgui.Dialog().input("Enter Search String", type=xbmcgui.INPUT_ALPHANUM)
                self.c_places_list.addItems(items=self.GetNearEvents(search_string,False))
            elif provider_index == 4:
                self.c_places_list.reset()
                self.PinString = ""
            self.GetGoogleMapURLs()       
            self.c_map_image.setImage(self.GoogleMapURL)
            
            
        elif controlId == self.CONTROL_LEFT:
            pass
        elif controlId == self.CONTROL_RIGHT:
            pass
        elif controlId == self.CONTROL_UP:
            pass
        elif controlId == self.CONTROL_DOWN:
            pass
        elif controlId == self.CONTROL_PLACES_LIST:
            self.lat = self.c_places_list.getSelectedItem().getProperty("lat")
            self.lon = self.c_places_list.getSelectedItem().getProperty("lon")
            self.GetGoogleMapURLs()       
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)           


    def ZoomIn(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view == True:
            if self.zoom_level_streetview <= 20:
                self.zoom_level_streetview += 1        
        else:
            if self.zoom_level <= 20:
                self.zoom_level += 1
        self.GetGoogleMapURLs()       
        self.c_streetview_image.setImage(self.GoogleStreetViewURL)
        self.c_map_image.setImage(self.GoogleMapURL)    
        
    def ZoomOut(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view == True:
            if self.zoom_level_streetview >= 1:
                self.zoom_level_streetview -= 1
        else:
            if self.zoom_level >= 1:
                self.zoom_level -= 1
        self.GetGoogleMapURLs()       
        self.c_streetview_image.setImage(self.GoogleStreetViewURL)
        self.c_map_image.setImage(self.GoogleMapURL)
        
    def ToggleNavMode(self):
        if self.NavMode_active == True:
            self.NavMode_active = False
            self.setWindowProperty('NavMode', '')
            xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
        else:
            self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
            self.NavMode_active = True
            self.setWindowProperty('NavMode', 'True')
            xbmc.executebuiltin("SetFocus(725)")
        
    def ToggleStreetMode(self):
        if self.street_view == True:
            self.street_view = False
            self.log("StreetView Off")
            self.GetGoogleMapURLs()       
            self.log("URL: " + self.GoogleMapURL)
            self.c_map_image.setImage(self.GoogleMapURL)
            self.setWindowProperty('streetview', '')
        else:
            self.street_view = True
            self.log("StreetView On")
            self.zoom_level = 17
            self.GetGoogleMapURLs()
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
            self.setWindowProperty('streetview', 'True') 
            

            
    def SearchLocation(self):
        self.location=xbmcgui.Dialog().input("Enter Search String", type=xbmcgui.INPUT_ALPHANUM)
        if not self.location=="":
            self.lat, self.lon = self.GetGeoCodes(self.location)
            self.GetGoogleMapURLs()       
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
        
                        
    def getItemProperty(self, key):
        return self.image_list.getSelectedItem().getProperty(key)

    def getWindowProperty(self, key):
        return self.window.getProperty(key)

    def setWindowProperty(self, key, value):
        self.log("Key: " + key + " value:" + value)
        return self.window.setProperty(key, value)

    def toggleInfo(self):
        self.show_info = not self.show_info
        self.info_controller.setVisible(self.show_info)

    def log(self, msg):
        if isinstance(msg, str):
            msg = msg.decode("utf-8")
        message = u'%s: %s' % (__addonid__, msg)
        xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


if __name__ == '__main__':
    startGUI = True
    for arg in sys.argv:
        param = arg.lower()
        xbmc.log("param = " + param)
        if param.startswith('prefix='):
            startGUI = False
    if startGUI == True:
        gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).doModal()
    else:
        gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).onInit(startGUI)
    del gui
    sys.modules.clear()
