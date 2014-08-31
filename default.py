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


    ################### code for FourSquare scraping based on script.maps by a.a.alsaleh. credits to him.


import os, re, sys, urllib, xbmc, xbmcaddon, xbmcgui
from Utils import *
from math import sin, cos, radians, pow
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
    CONTROL_LOOK_UP = 124
    CONTROL_LOOK_DOWN = 125
    CONTROL_PLACES_LIST = 200
    CONTROL_MODE_TOGGLE = 126

    ACTION_CONTEXT_MENU = [117]
    ACTION_OSD = [122]
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
        log('__init__')
            
    def onInit(self,startGUI = True):
        log('onInit')
        self.NavMode_active = False
        self.street_view = False
        self.search_string = ""
        self.zoom_level = 10
        self.zoom_level_saved = 10
        self.zoom_level_streetview = 0
        self.type = "roadmap"
        self.lat = 0.0
        self.strlat = ""
        self.lon = 0.0
        self.strlon = ""
        self.pitch = 0
        self.location = ""
        self.PinString = ""
        self.direction = 0
        self.saved_id = 100
        self.aspect = "normal"
        self.prefix = ""
        itemlist = []
        self.GoogleMapURL = ""
        self.GoogleStreetViewURL = ""
        self.GetLocationCoordinates()
        self.location = str(self.lat) + "," + str(self.lon)
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        log("window = " + str(self.window))
        self.setWindowProperty('NavMode', '')
        self.setWindowProperty('streetview', '')
        for arg in sys.argv:
            param = arg.lower()
            log("param = " + param)
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
            elif param.startswith('folder='):
                folder = (param[7:])
                itemlist = self.GetImages(folder)
            elif param.startswith('direction='):
                self.direction = (param[10:])
            elif param.startswith('prefix='):
                self.prefix = param[7:]
                if not self.prefix.endswith('.') and self.prefix <> "":
                    self.prefix = self.prefix + '.'
        if self.location == "geocode":
            self.lat,self.lon = ParseGeoTags()            
        self.GetGoogleMapURLs()
        if startGUI:
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
            self.getControls()
            self.c_places_list.reset()
            self.GetGoogleMapURLs()
            try:
                self.c_places_list.addItems(items=itemlist)
                self.c_map_image.setImage(self.GoogleMapURL)
                self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            except Exception,e:
                log("Error: Exception in onInit with message:")
                log(e)
            settings = xbmcaddon.Addon(id='script.maps.browser')
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            if not settings.getSetting('firststart') == "true":
                settings.setSetting(id='firststart', value='true')
                dialog = xbmcgui.Dialog()
                dialog.ok(__language__(34001), __language__(34002), __language__(34003))
        log('onInit finished')

    def getControls(self):
        self.c_map_image = self.getControl(self.CONTROL_MAP_IMAGE)
        self.c_streetview_image = self.getControl(self.CONTROL_STREETVIEW_IMAGE)
        self.c_places_list = self.getControl(self.CONTROL_PLACES_LIST)

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_SHOW_INFO:
            self.ToggleMapMode()      
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.ToggleNavMode()
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.NavMode_active == True or self.street_view == True:
                self.setWindowProperty('NavMode', '')
                self.setWindowProperty('streetview', '')
                self.NavMode_active = False
                self.street_view = False         
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif self.NavMode_active == True:
            log("lat: " + str(self.lat) + " lon: " + str(self.lon))
            if self.street_view == False:
                stepsize = 60.0 / pow(2, self.zoom_level)
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
        elif controlId == self.CONTROL_MODE_TOGGLE:
            self.ToggleMapMode()      
        elif controlId == self.CONTROL_STREET_VIEW:
            if not self.street_view:
                self.ToggleStreetMode()
                self.ToggleNavMode()
            else:
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
            self.lat, self.lon = self.GetGeoCodes(False, self.location)
            self.GetGoogleMapURLs()       
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
        elif controlId == self.CONTROL_SELECT_PROVIDER:
            self.setWindowProperty('index', "")
            modeselect= []
#            modeselect.append( __language__(34004) )
            modeselect.append( "Google Places" )
            modeselect.append(__language__(34005) )
            modeselect.append(__language__(34006) )
            modeselect.append(__language__(34007) )
            modeselect.append(__language__(34008) )
            modeselect.append( __language__(34009) )
            modeselect.append( __language__(34010) )
            modeselect.append( __language__(34011) )
            modeselect.append( __language__(34012) )
            modeselect.append( __language__(34013) )
            modeselect.append( __language__(34014) )
            modeselect.append( __language__(34015) )
            modeselect.append( __language__(34016) )
            modeselect.append( __language__(34017) )
            modeselect.append( __language__(34018) )
            modeselect.append( __language__(34021) )
            modeselect.append( "Concert Search (by artist)" )
            modeselect.append( __language__(34019) )

            dialogSelection = xbmcgui.Dialog()
            provider_index = dialogSelection.select( __language__(34020), modeselect )
            self.c_places_list.reset()
            if provider_index == 0:
                itemlist = self.GetGooglePlacesList("food")
            elif provider_index == 1:
                itemlist = self.GetPlacesListExplore("topPicks")
            elif provider_index == 2:
                itemlist = self.GetPlacesListExplore("food")
            elif provider_index == 3:
                itemlist = self.GetPlacesListExplore("drinks")
            elif provider_index == 4:
                itemlist = self.GetPlacesListExplore("coffee")
            elif provider_index == 5:
                itemlist = self.GetPlacesListExplore("shops")
            elif provider_index == 6:
                itemlist = self.GetPlacesListExplore("arts")
            elif provider_index == 7:
                itemlist = self.GetPlacesListExplore("outdoors")
            elif provider_index == 8:
                itemlist = self.GetPlacesListExplore("sights")
            elif provider_index == 9:
                itemlist = self.GetPlacesListExplore("trending")
            elif provider_index == 10:
                itemlist = self.GetPlacesListExplore("specials")
            elif provider_index == 11:
                itemlist = self.GetPlacesListExplore("nextVenues")
            elif provider_index == 12:
                itemlist,self.PinString = self.GetNearEvents()
            elif provider_index == 13:
                self.c_places_list.addItems(items=self.GetNearEvents(False,True))
            elif provider_index == 14:
                search_string=xbmcgui.Dialog().input(__language__(34022), type=xbmcgui.INPUT_ALPHANUM)
                itemlist = self.GetNearEvents(search_string,False)
            elif provider_index == 15:
                folder_path = xbmcgui.Dialog().browse(0,__language__(34021) , 'pictures')
                self.setWindowProperty('imagepath', folder_path)
                itemlist = self.GetImages(folder_path)               
       #     elif provider_index == 16:
       #         itemlist = self.GetPlacesList()               
            elif provider_index == 16:
                search_string = xbmcgui.Dialog().input("Type in artist name", type=xbmcgui.INPUT_ALPHANUM)
                itemlist,self.PinString = self.GetEvents(search_string)
            elif provider_index == 17:
                self.PinString = ""
                itemlist = []
            if not provider_index == -1:
                self.c_places_list.addItems(items=itemlist)
                self.street_view = False
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
        elif controlId == self.CONTROL_LOOK_UP:
            self.PitchUp()
        elif controlId == self.CONTROL_LOOK_DOWN:
            self.PitchDown()
        elif controlId == self.CONTROL_PLACES_LIST:
            self.lat = float(self.c_places_list.getSelectedItem().getProperty("lat"))
            self.lon = float(self.c_places_list.getSelectedItem().getProperty("lon"))
            if not self.c_places_list.getSelectedItem().getProperty("index") == self.getWindowProperty('index'):
                self.setWindowProperty('index', self.c_places_list.getSelectedItem().getProperty("index"))
            else:
                xbmc.executebuiltin("SetFocus(9023)")
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

    def PitchUp(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch <= 80:
            self.pitch += 10       
        self.GetGoogleMapURLs()       
        self.c_streetview_image.setImage(self.GoogleStreetViewURL)
        self.c_map_image.setImage(self.GoogleMapURL)    

    def PitchDown(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch >= -80:
            self.pitch -= 10   
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

    def ToggleMapMode(self):
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
        
    def ToggleStreetMode(self):
        if self.street_view == True:
            self.street_view = False
            log("StreetView Off")
            self.zoom_level = self.zoom_level_saved
            self.GetGoogleMapURLs()       
            log("URL: " + self.GoogleMapURL)
            self.c_map_image.setImage(self.GoogleMapURL)
            self.setWindowProperty('streetview', '')
        else:
            self.street_view = True
            log("StreetView On")
            self.zoom_level_saved = self.zoom_level
            self.zoom_level = 17
            self.GetGoogleMapURLs()
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
            self.setWindowProperty('streetview', 'True') 
            

            
    def SearchLocation(self):
        self.location=xbmcgui.Dialog().input("Enter Search String", type=xbmcgui.INPUT_ALPHANUM)
        if not self.location=="":
            self.street_view = False
            self.lat, self.lon = self.GetGeoCodes(True, self.location)
            self.PinString = ""
            self.GetGoogleMapURLs()       
            self.c_streetview_image.setImage(self.GoogleStreetViewURL)
            self.c_map_image.setImage(self.GoogleMapURL)
        
                        
    def getItemProperty(self, key):
        return self.image_list.getSelectedItem().getProperty(key)

    def getWindowProperty(self, key):
        return self.window.getProperty(key)

    def setWindowProperty(self, key, value):
      #  log("Key: " + key + " value:" + value)
        return self.window.setProperty(key, value)

    def toggleInfo(self):
        self.show_info = not self.show_info
        self.info_controller.setVisible(self.show_info)

    def log(self, msg):
        if isinstance(msg, str):
            msg = msg.decode("utf-8")
        message = u'%s: %s' % (__addonid__, msg)
        xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

class dialog_select_UI(xbmcgui.WindowXMLDialog):
    from Utils import *
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listing = kwargs.get('listing')
        self.selected_id = ''
        self.lon = ''
        self.lat = ''

    def onInit(self):
        if True :
            self.img_list = self.getControl(6)
            self.img_list.controlLeft(self.img_list)
            self.img_list.controlRight(self.img_list)
            self.getControl(3).setVisible(False)
        else :
           # print_exc()
            self.img_list = self.getControl(3)

        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(__language__(32015))

        for entry in self.listing:
            listitem = xbmcgui.ListItem('%s' %(entry['generalinfo']))
            listitem.setIconImage(entry['preview'])
            listitem.setLabel2(entry['id'])
            listitem.setProperty("lat",entry['lat'])
            listitem.setProperty("lon",entry['lon'])
            self.img_list.addItem(listitem)
        self.setFocus(self.img_list)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
      #  log('# GUI control: %s' % controlID)
        if controlID == 6 or controlID == 3: 
            num = self.img_list.getSelectedPosition()
       #     log('# GUI position: %s' % num)
            self.selected_id = self.img_list.getSelectedItem().getLabel2()
            self.lat = float(self.img_list.getSelectedItem().getProperty("lat"))
            self.lon = float(self.img_list.getSelectedItem().getProperty("lon"))
            xbmc.log('# GUI selected lat: %s' % self.selected_id)
            self.close()

    def onFocus(self, controlID):
        pass
        
        
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
