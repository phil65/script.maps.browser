# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import xbmcgui
import urllib
import sys
import Utils
from Eventful import Eventful
from MapQuest import MapQuest
from GooglePlaces import GooglePlaces
from FourSquare import FourSquare
from SearchSelectDialog import SearchSelectDialog
from EventInfoDialog import EventInfoDialog
import math
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

    @Utils.busy_dialog
    def __init__(self, skin_file, ADDON_PATH, *args, **kwargs):
        self.items = []
        self.location = kwargs.get("location", "")
        self.type = kwargs.get("type", "roadmap")
        self.strlat = kwargs.get("lat", "")
        self.strlon = kwargs.get("lon", "")
        self.zoom = kwargs.get("zoom", 10)
        self.aspect = kwargs.get("aspect", "640x400")
        self.init_vars()
        for arg in sys.argv:
            param = arg.lower()
            if param.startswith('folder='):
                folder = param[7:]
                self.items, self.pins = self.get_images(folder)
            elif param.startswith('direction='):
                self.direction = param[10:]
        if self.location == "geocode":
            self.lat, self.lon = Utils.parse_geotags(self.strlat, self.strlon)
        elif not self.location and not self.strlat:  # both empty
            self.lat, self.lon = Utils.get_location_coords()
            self.zoom = 2
        elif self.location and self.strlat:  # latlon empty
            self.lat, self.lon = self.get_geocodes(False, self.location)
        else:
            self.lat = float(self.strlat)
            self.lon = float(self.strlon)

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.window.clearProperty('NavMode')
        self.window.clearProperty('streetview')
        if ADDON.getSetting("VenueLayout") == "1":
            self.window.setProperty('ListLayout', '1')
        else:
            self.window.setProperty('ListLayout', '0')
        self.venues = self.getControl(C_PLACES_LIST)
        self.get_map_urls()
        Utils.fill_list_control(self.venues, self.items)
        self.window.setProperty("map_image", self.map_url)
        self.window.setProperty("streetview_image", self.street_view_url)
        if not ADDON.getSetting('firststart') == "true":
            ADDON.setSetting(id='firststart', value='true')
            xbmcgui.Dialog().ok(ADDON_LANGUAGE(32001), ADDON_LANGUAGE(32002), ADDON_LANGUAGE(32003))

    def init_vars(self):
        self.nav_mode_active = False
        self.street_view = False
        self.center = ""
        self.zoom_saved = 10
        self.zoom_streetview = 0
        self.lat = 0.0
        self.lon = 0.0
        self.pitch = 0
        self.venue_id = None
        self.pins = ""
        self.direction = 0
        self.saved_id = 100
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
            self.window.clearProperty('NavMode')
            self.window.clearProperty('streetview')
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
        if not self.nav_mode_active:
            return None
        Utils.log("lat: %s lon: %s" % (self.lat, self.lon))
        if not self.street_view:
            stepsize = 60.0 / math.pow(2, self.zoom)
            if self.action_id == xbmcgui.ACTION_MOVE_UP:
                self.lat = self.lat + stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                self.lat = self.lat - stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_LEFT:
                self.lon = self.lon - 2.0 * stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_RIGHT:
                self.lon = self.lon + 2.0 * stepsize
        else:
            stepsize = 0.0002
            radiantdirection = math.radians(self.direction)
            if self.action_id == xbmcgui.ACTION_MOVE_UP:
                self.lat = self.lat + math.cos(radiantdirection) * stepsize
                self.lon = self.lon + math.sin(radiantdirection) * stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                self.lat = self.lat - math.cos(radiantdirection) * stepsize
                self.lon = self.lon - math.sin(radiantdirection) * stepsize
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
        self.location = "%s,%s" % (self.lat, self.lon)

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
        item = self.venues.getSelectedItem()
        self.lat = float(item.getProperty("lat"))
        self.lon = float(item.getProperty("lon"))
        self.zoom = 12
        itemindex = item.getProperty("index")
        if itemindex != self.window.getProperty('index'):
            self.window.setProperty('index', itemindex)
            return None
        foursquare_id = item.getProperty("foursquare_id")
        eventful_id = item.getProperty("eventful_id")
        picture_path = item.getProperty("filepath")
        if picture_path:
            dialog = Utils.PictureDialog(u'script-%s-picturedialog.xml' % ADDON_NAME,
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

    @ch.click(C_ZOOM_IN)
    def zoom_in(self):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.street_view:
            if self.zoom_streetview <= 20:
                self.zoom_streetview += 1
        else:
            if self.zoom <= 20:
                self.zoom += 1

    @ch.click(C_ZOOM_OUT)
    def zoom_out(self):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.street_view:
            if self.zoom_streetview >= 1:
                self.zoom_streetview -= 1
        else:
            if self.zoom >= 1:
                self.zoom -= 1

    @ch.click(C_LOOK_UP)
    def pitch_up(self):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.pitch <= 80:
            self.pitch += 10

    @ch.click(C_LOOK_DOWN)
    def pitch_down(self):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.pitch >= -80:
            self.pitch -= 10

    @ch.action("contextmenu", "*")
    def toggle_nav_mode(self):
        if self.nav_mode_active:
            self.nav_mode_active = False
            self.window.clearProperty('NavMode')
            self.window.setFocusId(self.saved_id)
        else:
            self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
            self.nav_mode_active = True
            self.window.setProperty('NavMode', 'True')
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
            self.zoom = self.zoom_saved
            self.window.clearProperty('streetview')
        else:
            self.street_view = True
            self.zoom_saved = self.zoom
            self.zoom = 15
            self.window.setProperty('streetview', 'True')

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
                Utils.notify("Error", "No Search results found.")

    @ch.click(C_SELECT_PROVIDER)
    def select_places_provider(self):
        self.window.clearProperty('index')
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
                self.pins, items = GP.get_locations(self.lat, self.lon, self.radius * 1000, category)
        elif keys[index] == "foursquare":
            FS = FourSquare()
            section = FS.select_section()
            if section:
                items, self.pins = FS.get_places_by_section(self.lat, self.lon, section)
        elif keys[index] == "mapquest":
            MQ = MapQuest()
            items, self.pins = MQ.get_incidents(self.lat, self.lon, self.zoom)
        elif keys[index] == "geopics":
            folder_path = xbmcgui.Dialog().browse(0, ADDON_LANGUAGE(32021), 'pictures')
            self.window.setProperty('imagepath', folder_path)
            items, self.pins = Utils.get_images(folder_path)
        elif keys[index] == "eventful":
            EF = Eventful()
            category = EF.select_category()
            if category:
                items, self.pins = EF.get_eventlist(self.lat, self.lon, "", category, self.radius)
        elif keys[index] == "reset":
            self.pins = ""
            items = []
        if items is not None:
            Utils.fill_list_control(self.venues, items)
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
            items, self.pins = FS.get_places(self.lat, self.lon, query)
        elif KEYS[index] == "reset":
            self.pins = ""
            items = []
        Utils.fill_list_control(self.venues, items)
        self.street_view = False

    def get_map_urls(self):
        size = "320x200" if self.street_view else "640x400"
        self.center = "%s,%s" % (self.lat, self.lon) if self.lat else self.location.replace('"', '')
        params = {"sensor": "false",
                  "scale": 2,
                  "format": ADDON.getSetting("ImageFormat"),
                  "language": xbmc.getLanguage(xbmc.ISO_639_1),
                  "maptype": self.type,
                  "center": self.center,
                  "zoom": self.zoom,
                  "markers": self.center,
                  "size": size,
                  "key": GOOGLE_MAPS_KEY}
        base_url = "http://maps.googleapis.com/maps/api/staticmap?&" + urllib.urlencode(params)
        self.map_url = base_url + self.pins
        params = {"sensor": "false",
                  "format": ADDON.getSetting("ImageFormat"),
                  "language": xbmc.getLanguage(xbmc.ISO_639_1),
                  "fov": 120 - int(self.zoom_streetview) * 6,
                  "location": self.center,
                  "heading": self.direction,
                  "pitch": self.pitch,
                  "size": "640x400",
                  "key": GOOGLE_STREETVIEW_KEY}
        self.street_view_url = "http://maps.googleapis.com/maps/api/streetview?&" + urllib.urlencode(params)
        self.window.setProperty('location', self.location)
        self.window.setProperty('lat', str(self.lat))
        self.window.setProperty('lon', str(self.lon))
        self.window.setProperty('zoomlevel', str(self.zoom))
        self.window.setProperty('direction', str(self.direction / 18))
        self.window.setProperty('type', self.type)
        self.window.setProperty('aspect', self.aspect)
        self.window.setProperty('map_image', self.map_url)
        self.window.setProperty('streetview_image', self.street_view_url)
        if self.street_view:
            self.window.setProperty('streetview', "True")
        else:
            self.window.clearProperty('streetview')
        if self.nav_mode_active:
            self.window.setProperty('NavMode', "True")
        else:
            self.window.clearProperty('NavMode')
        if self.lat:
            hor_px = int(size.split("x")[0])
            ver_px = int(size.split("x")[1])
            mx, my = Utils.latlon_to_meters(self.lat, self.lon)
            px, py = Utils.meters_to_pixels(mx, my, self.zoom)
            mx2, my2 = Utils.pixels_to_meters(px + hor_px / 2, py + ver_px / 2, self.zoom)
            self.radius = min(abs((my - my2) / 2000), 500)

    def get_geocodes(self, show_dialog, search_string):
        search_string = urllib.quote_plus(search_string)
        base_url = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false"
        url = "&address=%s" % (search_string)
        results = Utils.get_JSON_response(base_url + url)
        places = []
        for item in results["results"]:
            locationinfo = item["geometry"]["location"]
            lat = str(locationinfo["lat"])
            lon = str(locationinfo["lng"])
            search_string = lat + "," + lon
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=1&maptype=roadmap&center=%s&zoom=13&markers=%s&size=320x320&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
            props = {'label': item['formatted_address'],
                     'lat': lat,
                     'lon': lon,
                     'thumb': googlemap,
                     'id': item['formatted_address']}
            places.append(props)
        first_hit = results["results"][0]["geometry"]["location"]
        if show_dialog:
            if len(results["results"]) > 1:  # open dialog when more than one hit
                w = SearchSelectDialog('DialogSelect.xml',
                                       ADDON_PATH,
                                       listing=Utils.create_listitems(places))
                w.doModal()
                if w.lat:
                    self.zoom = 12
                    return (float(w.lat), float(w.lon))
                else:
                    return (self.lat, self.lon)
            elif len(results["results"]) == 1:
                self.zoom = 12
                return (first_hit["lat"], first_hit["lng"])  # no window when only 1 result
            else:
                return (self.lat, self.lon)  # old values when no hit
        else:
            self.zoom = 12
            return (first_hit["lat"], first_hit["lng"])
