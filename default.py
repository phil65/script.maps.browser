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

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
addon_name = addon.getAddonInfo('name')
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
googlemaps_key_streetview = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'
bing_key =  'Ai8sLX5R44tf24_2CGmbxTYiIX6w826dsCVh36oBDyTmH21Y6CxYEqtrV9oYoM6O'


class GUI(xbmcgui.WindowXML):

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

    def onInit(self):
        self.log('onInit')
        self.NavMode_active = False
        self.street_view = False
        self.search_string = ""
        self.zoom_level = 15
        self.type = "roadmap"
        self.lat = 0.0
        self.strlat = ""
        self.lon = 0.0
        self.strlon = ""
        self.location = ""
        self.direction = 0
        self.saved_id = 100
        self.aspect = "normal"
        self.lat,self.lon = self.GetLocationCoordinates()
        self.location = str(self.lat) + "," + str(self.lon)
        for arg in sys.argv:
            param = arg.lower()
            self.log("param = " + param)
            if param.startswith('location='):
                self.location = (param[9:])
            elif param.startswith('lat='):
                self.strlat = (param[4:])
            elif param.startswith('lon='):
                self.strlon = (param[4:])
            elif param.startswith('prefix='):
                self.prop_prefix = param[7:]
                if not self.prop_prefix.endswith('.') and self.prop_prefix <> "":
                    self.prop_prefix = self.prop_prefix + '.'
        
        if self.location == "geocode":
            self.ParseGeoTags()            
        self.getControls()
        mapURL = self.GetGoogleMapURL()       
        self.log("URL: " + mapURL)
        self.c_map_image.setImage(mapURL)
        self.setFocus(self.c_streetview_image)
        self.log('onInit finished')

    def getControls(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.c_map_image = self.getControl(self.CONTROL_MAP_IMAGE)
        self.c_streetview_image = self.getControl(self.CONTROL_STREETVIEW_IMAGE)

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_SHOW_INFO:
            if self.NavMode_active == True:
                self.NavMode_active = False
                self.setWindowProperty('NavMode', '')
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
                self.NavMode_active = True
                self.setWindowProperty('NavMode', 'True')
                xbmc.executebuiltin("SetFocus(725)")
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.log("context menu")
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.NavMode_active == True:
                self.setWindowProperty('NavMode', '')
                self.NavMode_active = False                
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif self.NavMode_active == True: # navigation is conditional
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
                mapURL = self.GetGoogleMapURL()       
                self.c_map_image.setImage(mapURL)
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
                    if self.direction >= 18:
                        self.direction -= 18
                    else:
                        self.direction = 360
                elif action_id in self.ACTION_RIGHT and self.street_view == True:
                    if self.direction <= 360:
                        self.direction += 18
                    else:
                        self.direction = 0
                self.location = str(self.lat) + "," + str(self.lon)
                streetviewURL = self.GetGoogleStreetViewURL()       
                mapURL = self.GetGoogleMapURL()       
                self.c_streetview_image.setImage(streetviewURL)
                self.c_map_image.setImage(mapURL)
        self.SetProperties()
              
    def onClick(self, controlId):
        if controlId == self.CONTROL_ZOOM_IN:
            self.location = str(self.lat) + "," + str(self.lon)
            if self.zoom_level <= 20:
                self.zoom_level += 1
            streetviewURL = self.GetGoogleStreetViewURL()       
            mapURL = self.GetGoogleMapURL()       
            self.c_streetview_image.setImage(streetviewURL)
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_ZOOM_OUT:
            self.location = str(self.lat) + "," + str(self.lon)
            if self.zoom_level >= 1:
                self.zoom_level -= 1
            streetviewURL = self.GetGoogleStreetViewURL()       
            mapURL = self.GetGoogleMapURL()       
            self.c_streetview_image.setImage(streetviewURL)
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_SEARCH:
            self.SearchLocation()
        elif controlId == self.CONTROL_STREET_VIEW:
            if self.street_view == True:
                self.street_view = False
                self.log("StreetView Off")
                mapURL = self.GetGoogleMapURL()       
                self.log("URL: " + mapURL)
                self.c_map_image.setImage(mapURL)
                self.setWindowProperty('streetview', '')
            else:
                self.street_view = True
                self.log("StreetView On")
                streetviewURL = self.GetGoogleStreetViewURL()       
                mapURL = self.GetGoogleMapURL()       
                self.c_streetview_image.setImage(streetviewURL)
                self.c_map_image.setImage(mapURL)
                self.setWindowProperty('streetview', 'True')
        elif controlId == self.CONTROL_MODE_ROADMAP:
            self.type ="roadmap"
            mapURL = self.GetGoogleMapURL()       
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_MODE_SATELLITE:
            self.type ="satellite"
            mapURL = self.GetGoogleMapURL()       
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_MODE_HYBRID:
            self.type ="hybrid"
            mapURL = self.GetGoogleMapURL()       
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_MODE_TERRAIN:
            self.type ="terrain"
            mapURL = self.GetGoogleMapURL()       
            self.c_map_image.setImage(mapURL)
        elif controlId == self.CONTROL_GOTO_PLACE:
            self.location = self.getWindowProperty("Location")
            self.lat, self.lon = self.GetGeoCodes(self.location)
            streetviewURL = self.GetGoogleStreetViewURL()       
            mapURL = self.GetGoogleMapURL()       
            self.c_streetview_image.setImage(streetviewURL)
            self.c_map_image.setImage(mapURL)

        self.SetProperties()

    def SearchLocation(self):
        self.location=xbmcgui.Dialog().input("Enter Search String", type=xbmcgui.INPUT_ALPHANUM)
        if self.location=="":
            sys.exit()
        self.lat, self.lon = self.GetGeoCodes(self.location)
        streetviewURL = self.GetGoogleStreetViewURL()       
        mapURL = self.GetGoogleMapURL()       
        self.c_streetview_image.setImage(streetviewURL)
        self.c_map_image.setImage(mapURL)
        
    def GetGoogleMapURL(self):
        try:
            if not self.type:
                self.type="roadmap"
            if self.aspect == "square":
                size = "640x640"
            else:
                size = "640x400"
            if self.lat and self.lon:
                self.search_string = str(self.lat) + "," + str(self.lon)
            else:
                self.search_string = urllib.quote_plus(self.search_string.replace('"',''))
            base_url='http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&'
            url = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (self.type, self.search_string, self.zoom_level, self.search_string, size, googlemaps_key_normal)
            self.log("Google Maps Search:" + url)
            return url
        except Exception,e:
            self.log(e)
            return "Building Maps URL failed"
            
    # def GetBingMap(self):
        # try:
            # self.location = str(self.lat) + "," + str(self.lon)
            # self.log(urllib.quote(self.search_string))
            # self.log(urllib.quote_plus(self.search_string))
           # # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s?mapSize=800,600&key=%s' % (urllib.quote(self.search_string),bing_key)
            # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s/5?key=%s' % (urllib.quote_plus(self.location),bing_key)
            # self.log(url)
            # return url
        # except:
            # self.log("Error when fetching Bing data from net")
            # return ""    
            
    def GetGoogleStreetViewURL(self):
        try:
            if self.aspect == "square":
                size = "640x640"
            else:
                size = "640x400"
            if self.lat and self.lon:
                self.search_string = str(self.lat) + "," + str(self.lon)
            else:
                self.search_string = urllib.quote_plus(self.search_string.replace('"',''))
            zoom = 120 - int(self.zoom_level) * 6
            base_url='http://maps.googleapis.com/maps/api/streetview?&sensor=false&'
            url = base_url + 'location=%s&size=%s&fov=%s&key=%s&heading=%s' % (self.search_string, size, str(zoom), googlemaps_key_streetview, str(self.direction))        
            self.log("Google Maps Search (Street View):" + url)
            return url
        except Exception,e:
            self.log(e)
            return "Building Street View URL failed"
                              
    def GetGeoCodes(self, search_string):
        try:
            search_string = urllib.quote_plus(search_string)
            url = 'https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&address=%s' % (search_string)
            self.log("Google Geocodes Search:" + url)
            response = self.GetStringFromUrl(url)
            results = simplejson.loads(response)
            location = results["results"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        except Exception,e:
            self.log(e)
            return ("","")
            
    def GetLocationCoordinates(self):
        try:
            url = 'http://www.telize.com/geoip'
            response = self.GetStringFromUrl(url)
            results = simplejson.loads(response)
            return (results["latitude"], results["longitude"])
        except Exception,e:
            self.log(e)
            return ("","")
            
    def GetStringFromUrl(self,encurl):
        doc = ""
        succeed = 0
        while succeed < 5:
            try: 
                import urllib2
                req = urllib2.Request(encurl)
                req.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
                res = urllib2.urlopen(req)
                html = res.read()
                return html
            except:
                self.log("could not get data from %s" % encurl)
                xbmc.sleep(1000)
                succeed += 1
        return ""
            
    def string2deg(self, string):
        string = string.strip().replace('"','').replace("'","") # trim leading/trailing whitespace
        self.log("String:" + string)
        if string[0].lower() == "w" or string[0].lower() == "s":
           negative = True
        else:
            negative = False
        string = string[1:]
        string = string.replace("d","")
        string = string.replace("  "," ")
        div = '[|:|\s]' # allowable field delimiters "|", ":", whitespace
        sdec = '(\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}\.?\d+?)'
        co_re= re.compile(sdec)
        co_search= co_re.search(string)
        if co_search is None:
            raise ValueError("Invalid input string: %s" % string)
        elems = co_search.groups()
        degrees = float(elems[0])
        arcminutes = float(elems[1])
        arcseconds = float(elems[2])
        decDegrees = degrees + arcminutes/60.0 + arcseconds/3600.0
        if negative:
            decDegrees = -1.0 * decDegrees
        return decDegrees   

    def SetProperties(self):
        self.setWindowProperty('location', self.location)
        self.setWindowProperty('lat', str(self.lat))
        self.setWindowProperty('lon', str(self.lon))
        self.setWindowProperty('zoomlevel', str(self.zoom_level))
        self.setWindowProperty('direction', str(self.direction/18))
        self.setWindowProperty('type', self.type)
        self.setWindowProperty('aspect', self.aspect)
    
    def ParseGeoTags(self):
        if not self.strlon == "":
            self.lat = self.string2deg(self.strlat)
            self.lon = self.string2deg(self.strlon)
        else:
            coords = self.strlat.split(",lon=")
            self.lat = self.string2deg(coords[0])
            self.lon = self.string2deg(coords[1])
            
            
    def getItemProperty(self, key):
        return self.image_list.getSelectedItem().getProperty(key)

    def getWindowProperty(self, key):
        return self.window.getProperty(key)

    def setWindowProperty(self, key, value):
        return self.window.setProperty(key, value)

    def toggleInfo(self):
        self.show_info = not self.show_info
        self.info_controller.setVisible(self.show_info)

    def log(self, msg):
        xbmc.log('Maps Browser: %s' % msg)


if __name__ == '__main__':
    gui = GUI(u'script-%s-main.xml' % addon_name, addon_path).doModal()
    del gui
    sys.modules.clear()
