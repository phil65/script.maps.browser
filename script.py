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
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
addon_name = addon.getAddonInfo('name')
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
googlemaps_key_streetview = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'

class URLBuilder(object):

    def __init__(self):
        self.log('URLBuilder: __init__')

    def GetGoogleMapURL(self, search_string, zoom_level, type, aspect, lat, lon):
        self.log('URLBuilder: GetGoogleMapURL')
        try:
            if not type:
                type="roadmap"
            if aspect == "square":
                size = "640x640"
            else:
                size = "640x400"
            if lat and lon:
                search_string = str(lat) + "," + str(lon)
                log("Location: " + search_string)
            else:
                search_string = urllib.quote_plus(search_string.replace('"',''))
            base_url='http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&'
            url = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (type, search_string, zoom_level, search_string, size, googlemaps_key_normal)
            self.log("Google Maps Search:" + url)
            return url
        except Exception,e:
            self.log(e)
            return "Building Maps URL failed"
            
    def GetGoogleMapStreetViewURL(self, search_string, zoom_level, aspect, lat, lon, direction):
        self.log('URLBuilder: GetGoogleMapStreetViewURL')
        try:
            if aspect == "square":
                size = "640x640"
            else:
                size = "640x400"
            if lat and lon:
                search_string = str(lat) + "," + str(lon)
                log("Location: " + search_string)
            else:
                search_string = urllib.quote_plus(search_string.replace('"',''))
            zoom = 130 - int(zoom_level) * 6
            base_url='http://maps.googleapis.com/maps/api/streetview?&sensor=false&'
            url = base_url + 'location=%s&size=%s&fov=%s&key=%s&heading=%s' % (search_string, size, str(zoom), googlemaps_key_streetview, str(direction))        
            self.log("Google Maps Search (Street View):" + url)
            return url
        except Exception,e:
            self.log(e)
            return "Building Street View URL failed"
        
    def log(self, msg):
        xbmc.log('Maps Browser: %s' % msg)




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

    ACTION_CONTEXT_MENU = [117]
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    ACTION_SHOW_INFO = [11]
    ACTION_EXIT_SCRIPT = [13]
    ACTION_DOWN = [4]
    ACTION_UP = [3]
    ACTION_0 = [58, 18]
    ACTION_PLAY = [79]

    def __init__(self, skin_file, addon_path):
        self.log('__init__')

    def onInit(self):
        self.log('onInit')
        self.NavBar_active = True
        self.StreetView = False
        self.getControls()
        self.setFocus(self.c_street_view)
        self.search_string = ""
        self.zoom_level = "15"
        self.type = "normal"
        self.lat = "0.0"
        self.lon = "0.0"
        self.direction = "0"
        self.log('onInit finished')

    def getControls(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.c_search = self.getControl(self.CONTROL_SEARCH)
        self.c_street_view = self.getControl(self.CONTROL_STREET_VIEW)
        self.c_zoom_in = self.getControl(self.CONTROL_ZOOM_IN)
        self.c_zoom_out = self.getControl(self.CONTROL_ZOOM_OUT)
        self.c_zoom_out = self.getControl(self.CONTROL_ZOOM_OUT)
        self.c_mode_roadmap = self.getControl(self.CONTROL_MODE_ROADMAP)
        self.c_mode_hybrid = self.getControl(self.CONTROL_MODE_HYBRID)
        self.c_mode_satellite = self.getControl(self.CONTROL_MODE_SATELLITE)
        self.c_mode_terrain = self.getControl(self.CONTROL_MODE_TERRAIN)

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_SHOW_INFO:
            self.log("NavBar toggle")
            if self.NavBar_active == True:
                self.setWindowProperty('NavBar', 'False')
            else:
                self.setWindowProperty('NavBar', 'True')
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.log("context menu")
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.getWindowProperty('NavBar') == 'True':
                self.setWindowProperty('NavBar', 'False')
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        
            
    def onClick(self, controlId):
        if controlId == self.CONTROL_ZOOM_IN:
            self.log("show_context")
        elif controlId == self.CONTROL_ZOOM_OUT:
            self.log("show_context")
        elif controlId == self.CONTROL_SEARCH:
            self.SearchLocation()
        elif controlId == self.CONTROL_STREET_VIEW:
            self.log("StreetView toggle")
            if self.street_view == True:
                self.setWindowProperty('StreetView', 'False')
            else:
                self.setWindowProperty('StreetView', 'True')
            
    def SearchLocation(self):
        self.location=xbmcgui.Dialog().input("Enter Search String", type=xbmcgui.INPUT_ALPHANUM)
        if self.location=="":
            sys.exit()
        urlbuilder = URLBuilder()
        mapURL = urlbuilder.GetGoogleMapURL(self.location, "15", "terrain", "normal", "", "")       
        del urlbuilder
        self.log("right here: " + mapURL)
        self.getControl(self.CONTROL_MAP_IMAGE).setImage(mapURL)
                    
    def GetGeoCodes(self, search_string):
        try:
            search_string = urllib.quote_plus(search_string)
            base_url='https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&'
            url = base_url + 'address=%s' % (search_string)
            log("Google Geocodes Search:" + url)
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            log(results)
            location = results["results"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        except Exception,e:
            log(e)
            return ("","")
            
    def string2deg(self, string):
        import re
        string = string.strip().replace('"','').replace("'","") # trim leading/trailing whitespace
        log("String:" + string)
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
    
            
            
           # elif info == 'getgooglemap' or info == 'getgooglestreetviewmap':
                # direction = ""
                # if self.location == "geocode": # convert Image Coordinates to float values
                    # if not self.lon == "":
                        # self.lat = string2deg(self.lat)
                        # log("Lat: " + self.lat)
                        # self.lon = string2deg(self.lon)
                        # log("Lon: " + self.lon)
                    # else:
                        # log("splitting string")
                        # coords = self.lat.split(",lon=")
                        # log("Lat: " + coords[0])
                        # log("Lon: " + coords[1])
                        # self.lat = string2deg(coords[0])
                        # self.lon = string2deg(coords[1])
                        
                # elif self.location=="search":
                     # SearchLocation()
                # if info == 'getgooglemap':  # request normal map                   
                    # image = GetGoogleMap(mode = "normal",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = self.direction)
                    # overview = ""
                # else: # request streetview
                    # direction = str(int(self.direction) * 18)
                    # image = GetGoogleMap(mode = "streetview",search_string = self.location,aspect = self.aspect,type = self.type, lat = self.lat,lon = self.lon,zoomlevel = self.zoomlevel,direction = direction)                    
                    # overview = GetGoogleMap(mode = "normal",search_string = self.location,aspect = self.aspect,type = "roadmap", lat = self.lat,lon = self.lon,zoomlevel = "17",direction = direction)                    
                # wnd.setProperty('%sgooglemap' % self.prop_prefix, image) # set properties 
                # wnd.setProperty('%sgooglemapoverview' % self.prop_prefix, overview)
                # wnd.setProperty('%sDirection' % self.prop_prefix, str(self.direction))
                # wnd.setProperty('%sDirection2' % self.prop_prefix, str(direction))
                # if not self.lat or self.location=="geocode": # set properties for lat / lon (after JSON call for speed)
                    # lat = self.lat
                    # lon = self.lon
                    # if not self.location=="geocode":
                        # lat, lon = GetGeoCodes(self.location)
                    # wnd.setProperty('%slat' % self.prop_prefix, str(lat))
                    # wnd.setProperty('%slon' % self.prop_prefix, str(lon))
                    # wnd.setProperty('%sLocation' % self.prop_prefix, "")
            # elif "move" in info and "google" in info:
                # from MiscScraper import GetGoogleMap
                # wnd = xbmcgui.Window(Window)
                # lat = wnd.getProperty('%slat' % self.prop_prefix)
                # lon = wnd.getProperty('%slon' % self.prop_prefix)
                # direction = int(self.direction) * 18
                # if lat and lon:
                    # if "street" in info:
                        # from math import sin, cos, radians
                        # stepsize = 0.0002
                        # radiantdirection = radians(float(direction))
                        # if "up" in info:
                            # lat = float(lat) + cos(radiantdirection) * stepsize
                            # lon = float(lon) + sin(radiantdirection) * stepsize
                        # elif "down" in info:
                            # lat = float(lat) - cos(radiantdirection) * stepsize
                            # lon = float(lon) - sin(radiantdirection) * stepsize      
                        # elif "left" in info:
                            # lat = float(lat) - sin(radiantdirection) * stepsize
                            # lon = float(lon) - cos(radiantdirection) * stepsize
                        # elif "right" in info:
                            # lat = float(lat) + sin(radiantdirection) * stepsize
                            # lon = float(lon) + cos(radiantdirection) * stepsize
                    # else:
                        # stepsize = 200.0 / float(self.zoomlevel) / float(self.zoomlevel) / float(self.zoomlevel) / float(self.zoomlevel)
                        # if "up" in info:
                            # lat = float(lat) + stepsize
                        # elif "down" in info:
                            # lat = float(lat) - stepsize           
                        # elif "left" in info:
                            # lon = float(lon) - 2.0 * stepsize  
                        # elif "right" in info:
                            # lon = float(lon) + 2.0 * stepsize
                # self.location = str(lat) + "," + str(lon)
                # if "street" in info:
                    # image = GetGoogleMap(mode = "streetview",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = direction)
                    # overview = GetGoogleMap(mode = "normal",search_string = self.location,aspect = self.aspect,type = "roadmap", lat = self.lat,lon = self.lon,zoomlevel = "17",direction = self.direction)                    
                # else:
                    # image = GetGoogleMap(mode = "normal",search_string = self.location,zoomlevel = self.zoomlevel,type = self.type,aspect = self.aspect, lat=self.lat,lon=self.lon,direction = self.direction)
                    # overview = ""
                # wnd.setProperty('%sgooglemap' % self.prop_prefix, image)
                # wnd.setProperty('%sgooglemapoverview' % self.prop_prefix, overview)
                # wnd.setProperty('%slat' % self.prop_prefix, str(lat))
                # wnd.setProperty('%sDirection' % self.prop_prefix, self.direction)
                # wnd.setProperty('%slon' % self.prop_prefix, str(lon))

            
            
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
