# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import xbmcgui
import urllib
import sys
from Utils import *
from LastFM import LastFM, LastFMDialog
from Eventful import Eventful
from MapQuest import MapQuest
from GooglePlaces import GooglePlaces
from FourSquare import FourSquare
from Search_Select_Dialog import Search_Select_Dialog
from EventInfoDialog import EventInfoDialog
from math import sin, cos, radians, pow
from ActionHandler import ActionHandler

ch = ActionHandler()


ADDON = xbmcaddon.Addon()
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo('name')

C_SEARCH = 101
C_STREET_VIEW = 102
C_ZOOM_IN = 103
C_ZOOM_OUT = 104
C_MODE_ROADMAP = 105
C_MODE_HYBRID = 106
C_MODE_SATELLITE = 107
C_MODE_TERRAIN = 108
C_GOTO_PLACE = 111
C_SELECT_PROVIDER = 112
C_LEFT = 120
C_RIGHT = 121
C_UP = 122
C_DOWN = 123
C_LOOK_UP = 124
C_LOOK_DOWN = 125
C_PLACES_LIST = 200
C_MODE_TOGGLE = 126

GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
GOOGLE_STREETVIEW_KEY = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'


class GUI(xbmcgui.WindowXML):

    ACTION_CONTEXT_MENU = [117]
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    ACTION_EXIT_SCRIPT = [13]
    ACTION_0 = [58, 18]

    @busy_dialog
    def __init__(self, skin_file, ADDON_PATH, *args, **kwargs):
        self.items = []
        self.location = kwargs.get("location", "")
        self.type = kwargs.get("type", "roadmap")
        self.strlat = kwargs.get("lat", "")
        self.strlon = kwargs.get("lon", "")
        self.zoom_level = kwargs.get("zoom_level", 10)
        self.aspect = kwargs.get("aspect", "640x400")
        self.init_vars()
        for arg in sys.argv:
            param = arg.lower()
            log("param = " + param)
            if param.startswith('folder='):
                folder = param[7:]
                self.items, self.pin_string = self.get_images(folder)
            elif param.startswith('direction='):
                self.direction = param[10:]
            elif param.startswith('prefix='):
                self.prefix = param[7:]
                if not self.prefix.endswith('.') and self.prefix != "":
                    self.prefix = self.prefix + '.'
            # get lat / lon values
        if self.location == "geocode":
            self.lat, self.lon = parse_geotags(self.strlat, self.strlon)
        elif (self.location == "") and (self.strlat == ""):  # both empty
            self.lat, self.lon = get_location_coords()
            self.zoom_level = 2
        elif (not self.location == "") and (self.strlat == ""):  # latlon empty
            self.lat, self.lon = self.get_geocodes(False, self.location)
        else:
            self.lat = float(self.strlat)
            self.lon = float(self.strlon)

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        set_window_prop(self.window, 'NavMode', '')
        set_window_prop(self.window, 'streetview', '')
        if ADDON.getSetting("VenueLayout") == "1":
            set_window_prop(self.window, 'ListLayout', '1')
        else:
            set_window_prop(self.window, 'ListLayout', '0')
        self.venue_list = self.getControl(C_PLACES_LIST)
        self.get_map_urls()
        fill_list_control(self.venue_list, self.items)
        self.window.setProperty("map_image", self.map_url)
        self.window.setProperty("streetview_image", self.street_view_url)
        if not ADDON.getSetting('firststart') == "true":
            ADDON.setSetting(id='firststart', value='true')
            xbmcgui.Dialog().ok(ADDON_LANGUAGE(32001), ADDON_LANGUAGE(32002), ADDON_LANGUAGE(32003))
        log('onInit finished')

    def init_vars(self):
        self.nav_mode_active = False
        self.street_view = False
        self.search_string = ""
        self.zoom_level_saved = 10
        self.zoom_level_streetview = 0
        self.lat = 0.0
        self.lon = 0.0
        self.pitch = 0
        self.venue_id = None
        self.pin_string = ""
        self.direction = 0
        self.saved_id = 100
        self.prefix = ""
        self.radius = 50
        self.map_url = ""
        self.street_view_url = ""

    def onAction(self, action):
        super(GUI, self).onAction(action)
        ch.serve_action(action, self.getFocusId(), self)
        self.get_map_urls()
        self.window.setProperty("streetview_image", self.street_view_url)
        self.window.setProperty("map_image", self.map_url)

    @ch.action("close", "*")
    def close_script(self):
        self.close()

    @ch.action("previousmenu", "*")
    def previous_menu(self):
        if self.nav_mode_active or self.street_view:
            set_window_prop(self.window, 'NavMode', '')
            set_window_prop(self.window, 'streetview', '')
            self.nav_mode_active = False
            self.street_view = False
            self.window.setFocusId(self.saved_id)
        else:
            self.close()

    def onClick(self, control_id):
        super(GUI, self).onClick(control_id)
        ch.serve(control_id, self)
        self.get_map_urls()
        self.window.setProperty("streetview_image", self.street_view_url)
        self.window.setProperty("map_image", self.map_url)

    @ch.action("info", "*")
    def info_press(self):
        if ADDON.getSetting("InfoButtonAction") == "1":
            self.toggle_map_mode()
        else:
            if not self.street_view:
                self.toggle_street_mode()
                self.toggle_nav_mode()
            else:
                self.toggle_street_mode()

    @ch.action("up", "*")
    @ch.action("down", "*")
    @ch.action("left", "*")
    @ch.action("right", "*")
    def navigate(self):
        if self.nav_mode_active:
            log("lat: " + str(self.lat) + " lon: " + str(self.lon))
            if not self.street_view:
                stepsize = 60.0 / pow(2, self.zoom_level)
                if self.action_id == xbmcgui.ACTION_MOVE_UP:
                    self.lat = float(self.lat) + stepsize
                elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                    self.lat = float(self.lat) - stepsize
                elif self.action_id == xbmcgui.ACTION_MOVE_LEFT:
                    self.lon = float(self.lon) - 2.0 * stepsize
                elif self.action_id == xbmcgui.ACTION_MOVE_RIGHT:
                    self.lon = float(self.lon) + 2.0 * stepsize
            else:
                stepsize = 0.0002
                radiantdirection = float(radians(self.direction))
                if self.action_id == xbmcgui.ACTION_MOVE_UP:
                    self.lat = float(self.lat) + cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) + sin(radiantdirection) * float(stepsize)
                elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                    self.lat = float(self.lat) - cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) - sin(radiantdirection) * float(stepsize)
                elif self.action_id == xbmcgui.ACTION_MOVE_LEFT:
                    if self.direction <= 0:
                        self.direction = 360
                    self.direction -= 18
                elif self.action_id == xbmcgui.ACTION_MOVE_RIGHT:
                    if self.direction >= 348:
                        self.direction = 0
                    self.direction += 18
            if self.lat > 90.0:
                self.lat -= 180.0
            if self.lat < -90.0:
                self.lat += 180.0
            if self.lon > 180.0:
                self.lon -= 360.0
            if self.lon < -180.0:
                self.lon += 180.0
            self.location = str(self.lat) + "," + str(self.lon)

    @ch.click(C_STREET_VIEW)
    def toggle_street_view(self):
        if not self.street_view:
            self.toggle_street_mode()
            self.toggle_nav_mode()
        else:
            self.toggle_street_mode()

    @ch.click(C_GOTO_PLACE)
    def go_to_place(self):
        self.location = self.window.getProperty("Location")
        self.lat, self.lon = self.get_geocodes(False, self.location)

    @ch.click(C_PLACES_LIST)
    def list_click(self):
        item = self.venue_list.getSelectedItem()
        self.lat = float(item.getProperty("lat"))
        self.lon = float(item.getProperty("lon"))
        self.zoom_level = 12
        itemindex = item.getProperty("index")
        if itemindex != self.window.getProperty('index'):
            set_window_prop(self.window, 'index', itemindex)
        else:
            event_id = item.getProperty("event_id")
            venue_id = item.getProperty("venue_id")
            foursquare_id = item.getProperty("foursquare_id")
            eventful_id = item.getProperty("eventful_id")
            picture_path = item.getProperty("filepath")
            if event_id:
                dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME,
                                      ADDON_PATH,
                                      eventid=event_id)
            elif venue_id:
                dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME,
                                      ADDON_PATH,
                                      venue_id=venue_id)
            elif picture_path:
                dialog = PictureDialog(u'script-%s-picturedialog.xml' % ADDON_NAME,
                                       ADDON_PATH,
                                       picture_path=picture_path)
            elif foursquare_id:
                dialog = EventInfoDialog(u'script-%s-dialog.xml' % ADDON_NAME,
                                         ADDON_PATH,
                                         foursquare_id=foursquare_id)
            elif eventful_id:
                dialog = EventInfoDialog(u'script-%s-dialog.xml' % ADDON_NAME,
                                         ADDON_PATH,
                                         eventful_id=eventful_id)
            dialog.doModal()
            if dialog.events_items:
                self.pin_string = dialog.events_pin_string
                fill_list_control(self.venue_list, dialog.events_items)

    @ch.click(C_ZOOM_IN)
    def zoom_in(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview <= 20:
                self.zoom_level_streetview += 1
        else:
            if self.zoom_level <= 20:
                self.zoom_level += 1

    @ch.click(C_ZOOM_OUT)
    def zoom_out(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview >= 1:
                self.zoom_level_streetview -= 1
        else:
            if self.zoom_level >= 1:
                self.zoom_level -= 1

    @ch.click(C_LOOK_UP)
    def pitch_up(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch <= 80:
            self.pitch += 10

    @ch.click(C_LOOK_DOWN)
    def pitch_down(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch >= -80:
            self.pitch -= 10

    @ch.action("contextmenu", "*")
    def toggle_nav_mode(self):
        if self.nav_mode_active:
            self.nav_mode_active = False
            set_window_prop(self.window, 'NavMode', '')
            self.window.setFocusId(self.saved_id)
        else:
            self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
            self.nav_mode_active = True
            set_window_prop(self.window, 'NavMode', 'True')
            self.window.setFocusId(725)

    @ch.click(C_MODE_TOGGLE)
    def toggle_map_mode(self):
        if self.type == "roadmap":
            self.type = "satellite"
        elif self.type == "satellite":
            self.type = "hybrid"
        elif self.type == "hybrid":
            self.type = "terrain"
        else:
            self.type = "roadmap"

    @ch.click(C_MODE_ROADMAP)
    def set_roadmap_type(self):
        self.type = "roadmap"

    @ch.click(C_MODE_HYBRID)
    def set_hybrid_type(self):
        self.type = "hybrid"

    @ch.click(C_MODE_SATELLITE)
    def set_satellite_type(self):
        self.type = "satellite"

    @ch.click(C_MODE_TERRAIN)
    def set_terrain_type(self):
        self.type = "terrain"

    def toggle_street_mode(self):
        if self.street_view:
            self.street_view = False
            self.zoom_level = self.zoom_level_saved
            set_window_prop(self.window, 'streetview', '')
        else:
            self.street_view = True
            self.zoom_level_saved = self.zoom_level
            self.zoom_level = 15
            set_window_prop(self.window, 'streetview', 'True')

    def search_location(self):
        self.location = xbmcgui.Dialog().input(ADDON_LANGUAGE(32032),
                                               type=xbmcgui.INPUT_ALPHANUM)
        if not self.location == "":
            self.street_view = False
            lat, lon = self.get_geocodes(True, self.location)
            if lat:
                self.lat = lat
                self.lon = lon
            else:
                Notify("Error", "No Search results found.")

    @ch.click(C_SELECT_PROVIDER)
    def select_places_provider(self):
        set_window_prop(self.window, 'index', "")
        items = None
        modeselect = [("geopics", ADDON_LANGUAGE(32027)),
                      ("eventful", ADDON_LANGUAGE(32028)),
                      ("foursquare", ADDON_LANGUAGE(32029)),
                      ("mapquest", ADDON_LANGUAGE(32030)),
                      ("googleplaces", ADDON_LANGUAGE(32031)),
                      ("reset", ADDON_LANGUAGE(32019))]
        listitems = [item[1] for item in modeselect]
        keys = [item[0] for item in modeselect]
        index = xbmcgui.Dialog().select(ADDON_LANGUAGE(32020), listitems)
        if index == -1:
            return None
        if keys[index] == "googleplaces":
            GP = GooglePlaces()
            category = GP.select_category()
            if category:
                self.pin_string, items = GP.GetGooglePlacesList(self.lat, self.lon, self.radius * 1000, category)
        elif keys[index] == "foursquare":
            FS = FourSquare()
            section = FS.select_section()
            if section:
                items, self.pin_string = FS.get_places_by_section(self.lat, self.lon, section)
        elif keys[index] == "mapquest":
            MQ = MapQuest()
            items, self.pin_string = MQ.get_incidents(self.lat, self.lon, self.zoom_level)
        elif keys[index] == "geopics":
            folder_path = xbmcgui.Dialog().browse(0, ADDON_LANGUAGE(32021), 'pictures')
            set_window_prop(self.window, 'imagepath', folder_path)
            items, self.pin_string = get_images(folder_path)
        elif keys[index] == "eventful":
            EF = Eventful()
            category = EF.select_category()
            if category:
                items, self.pin_string = EF.get_eventlist(self.lat, self.lon, "", category, self.radius)
        elif keys[index] == "reset":
            self.pin_string = ""
            items = []
        if items is not None:
            fill_list_control(self.venue_list, items)
        self.street_view = False

    @ch.click(C_SEARCH)
    def open_search_dialog(self):
        modeselect = [("googlemaps", ADDON_LANGUAGE(32024)),
                      ("foursquareplaces", ADDON_LANGUAGE(32004)),
                      ("reset", ADDON_LANGUAGE(32019))]
        KEYS = [item[0] for item in modeselect]
        VALUES = [item[1] for item in modeselect]
        index = xbmcgui.Dialog().select(ADDON_LANGUAGE(32026), VALUES)
        if index < 0:
            return None
        if KEYS[index] == "googlemaps":
            self.search_location()
            items = []
        elif KEYS[index] == "foursquareplaces":
            query = xbmcgui.Dialog().input(ADDON_LANGUAGE(32022), type=xbmcgui.INPUT_ALPHANUM)
            FS = FourSquare()
            items, self.pin_string = FS.get_places(self.lat, self.lon, query)
        elif KEYS[index] == "reset":
            self.pin_string = ""
            items = []
        fill_list_control(self.venue_list, items)
        self.street_view = False

    def get_map_urls(self):
        size = "320x200" if self.street_view else "640x400"
        if self.lat and self.lon:
            self.search_string = str(self.lat) + "," + str(self.lon)
        else:
            self.search_string = urllib.quote_plus(self.location.replace('"', ''))
        base_url = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&format=%s&language=%s&' % (ADDON.getSetting("ImageFormat"), xbmc.getLanguage(xbmc.ISO_639_1))
        url = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (self.type, self.search_string, self.zoom_level, self.search_string, size, GOOGLE_MAPS_KEY)
        self.map_url = url + self.pin_string
        zoom = 120 - int(self.zoom_level_streetview) * 6
        base_url = 'http://maps.googleapis.com/maps/api/streetview?&sensor=false&format=%s&' % (ADDON.getSetting("ImageFormat"))
        self.street_view_url = base_url + 'location=%s&size=640x400&fov=%s&key=%s&heading=%s&pitch=%s' % (self.search_string, str(zoom), GOOGLE_STREETVIEW_KEY, str(self.direction), str(self.pitch))
        set_window_prop(self.window, self.prefix + 'location', self.location)
        set_window_prop(self.window, self.prefix + 'lat', str(self.lat))
        set_window_prop(self.window, self.prefix + 'lon', str(self.lon))
        set_window_prop(self.window, self.prefix + 'zoomlevel', str(self.zoom_level))
        set_window_prop(self.window, self.prefix + 'direction', str(self.direction / 18))
        set_window_prop(self.window, self.prefix + 'type', self.type)
        set_window_prop(self.window, self.prefix + 'aspect', self.aspect)
        set_window_prop(self.window, self.prefix + 'map_image', self.map_url)
        set_window_prop(self.window, self.prefix + 'streetview_image', self.street_view_url)
        hor_px = int(size.split("x")[0])
        ver_px = int(size.split("x")[1])
        mx, my = latlon_to_meters(self.lat, self.lon)
        px, py = meters_to_pixels(mx, my, self.zoom_level)
        mx2, my2 = pixels_to_meters(px + hor_px / 2, py + ver_px / 2, self.zoom_level)
        self.radiusx = abs((mx - mx2) / 2000)
        self.radius = abs((my - my2) / 2000)
        self.radius = min(self.radius, 500)
        cache_path = xbmc.getCacheThumbName(self.map_url)
        log(cache_path)
        if self.prefix == "":
            if self.street_view:
                set_window_prop(self.window, self.prefix + 'streetview', "True")
            else:
                set_window_prop(self.window, self.prefix + 'streetview', "")
            if self.nav_mode_active:
                set_window_prop(self.window, self.prefix + 'NavMode', "True")
            else:
                set_window_prop(self.window, self.prefix + 'NavMode', "")

    def get_geocodes(self, show_dialog, search_string):
        search_string = urllib.quote_plus(search_string)
        base_url = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false"
        url = "&address=%s" % (search_string)
        log("Google Geocodes Search:" + url)
        results = Get_JSON_response(base_url + url)
        places = []
        for item in results["results"]:
            locationinfo = item["geometry"]["location"]
            lat = str(locationinfo["lat"])
            lon = str(locationinfo["lng"])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=1&maptype=roadmap&center=%s&zoom=13&markers=%s&size=320x320&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
            prop_list = {'label': item['formatted_address'],
                         'lat': lat,
                         'lon': lon,
                         'thumb': googlemap,
                         'id': item['formatted_address']}
            places.append(prop_list)
        first_hit = results["results"][0]["geometry"]["location"]
        if show_dialog:
            if len(results["results"]) > 1:  # open dialog when more than one hit
                w = Search_Select_Dialog('DialogSelect.xml',
                                         ADDON_PATH,
                                         listing=create_listitems(places))
                w.doModal()
                if w.lat is not "":
                    self.zoom_level = 12
                    return (float(w.lat), float(w.lon))
                else:
                    return (self.lat, self.lon)
            elif len(results["results"]) == 1:
                self.zoom_level = 12
                return (first_hit["lat"], first_hit["lng"])  # no window when only 1 result
            else:
                return (self.lat, self.lon)  # old values when no hit
        else:
            self.zoom_level = 12
            return (first_hit["lat"], first_hit["lng"])
