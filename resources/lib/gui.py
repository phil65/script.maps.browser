# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmcgui
import math

import googlemaps
import Utils
from Eventful import EF
import MapQuest
from GooglePlaces import GP
from FourSquare import FS

from kodi65 import utils
from kodi65 import addon
from kodi65 import slideshow
from kodi65.actionhandler import ActionHandler

ch = ActionHandler()

C_SEARCH = 101
C_STREET_VIEW = 102
C_ZOOM_IN = 103
C_ZOOM_OUT = 104
C_MODE_ROADMAP = 105
C_MODE_HYBRID = 106
C_MODE_SATELLITE = 107
C_MODE_TERRAIN = 108
C_NAV_MODE = 109
C_GOTO_PLACE = 111
C_SELECT_PROVIDER = 112
C_LEFT = 120
C_RIGHT = 121
C_UP = 122
C_DOWN = 123
C_LOOK_UP = 124
C_LOOK_DOWN = 125
C_PLACES_LIST = 200
C_MAPTYPE_TOGGLE = 126
C_BUTTON_NAV = 725


def get_window(*args, **kwargs):
    return MapsBrowser(u'script-%s-main.xml' % addon.NAME,
                       addon.PATH,
                       *args,
                       **kwargs)


class MapsBrowser(xbmcgui.WindowXML):

    @utils.busy_dialog
    def __init__(self, *args, **kwargs):
        self.items = []
        self.location = kwargs.get("location", "")
        self.type = kwargs.get("type", "roadmap")
        self.strlat = kwargs.get("lat", "")
        self.strlon = kwargs.get("lon", "")
        self.zoom = kwargs.get("zoom", 10)
        self.aspect = kwargs.get("aspect", "640x400")
        self.nav_mode_active = False
        self.street_view = False
        self.zoom_streetview = 0
        self.lat = 0.0
        self.lon = 0.0
        self.pitch = 0
        self.pins = ""
        self.saved_id = C_NAV_MODE
        self.radius = 50
        self.map_url = ""
        self.streetview_url = ""
        self.direction = kwargs.get("direction", 0)
        if kwargs.get("folder"):
            self.items = Utils.get_images(kwargs["folder"])
            self.pins = googlemaps.create_pins(self.items)
        if self.location == "geocode":
            self.lat, self.lon = Utils.parse_geotags(self.strlat, self.strlon)
        elif not self.location and not self.strlat:  # both empty
            self.lat, self.lon = Utils.get_coords_by_ip()
            self.zoom = 3
        elif self.location and self.strlat:  # latlon empty
            data = googlemaps.get_coords_by_location(False, self.location)
            if data:
                self.lat, self.lon, self.zoom = data
        else:
            self.lat = float(self.strlat)
            self.lon = float(self.strlon)

    def onInit(self):
        self.clearProperty('NavMode')
        self.clearProperty('streetview')
        self.venues = self.getControl(C_PLACES_LIST)
        self.update()
        self.venues.reset()
        self.venues.addItems(items=utils.create_listitems(self.items))
        self.clearProperty("index")
        if not addon.setting('firststart') == "true":
            addon.set_setting('firststart', 'true')
            xbmcgui.Dialog().ok(addon.LANG(32001), addon.LANG(32002), addon.LANG(32003))

    def onAction(self, action):
        # super(MapsBrowser, self).onAction(action)
        ch.serve_action(action, self.getFocusId(), self)
        self.update()

    @ch.action("previousmenu", "*")
    def close_script(self, control_id):
        self.close()

    @ch.action("close", "*")
    def previous_menu(self, control_id):
        if self.nav_mode_active or self.street_view:
            self.clearProperty('streetview')
            self.street_view = False
            if self.nav_mode_active:
                self.clearProperty('NavMode')
                self.nav_mode_active = False
                self.setFocusId(self.saved_id)
        else:
            self.close()

    def onClick(self, control_id):
        super(MapsBrowser, self).onClick(control_id)
        ch.serve(control_id, self)
        self.update()

    @ch.action("info", "*")
    def info_press(self, control_id):
        self.toggle_map_mode()

    @ch.action("up", "*")
    @ch.action("down", "*")
    @ch.action("left", "*")
    @ch.action("right", "*")
    def navigate(self, control_id):
        if not self.nav_mode_active:
            return None
        utils.log("lat: %s lon: %s" % (self.lat, self.lon))
        if not self.street_view:
            stepsize = 60.0 / math.pow(2, self.zoom)
            if self.action_id == xbmcgui.ACTION_MOVE_UP:
                self.lat += stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                self.lat -= stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_LEFT:
                self.lon -= 2.0 * stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_RIGHT:
                self.lon += 2.0 * stepsize
        else:
            stepsize = 0.0002
            radiantdirection = math.radians(self.direction)
            if self.action_id == xbmcgui.ACTION_MOVE_UP:
                self.lat += math.cos(radiantdirection) * stepsize
                self.lon += math.sin(radiantdirection) * stepsize
            elif self.action_id == xbmcgui.ACTION_MOVE_DOWN:
                self.lat -= math.cos(radiantdirection) * stepsize
                self.lon -= math.sin(radiantdirection) * stepsize
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

    @ch.click(C_GOTO_PLACE)
    def go_to_place(self, control_id):
        self.location = self.getProperty("Location")
        data = googlemaps.get_coords_by_location(False, self.location)
        if data:
            self.lat, self.lon, self.zoom = data

    @ch.click(C_PLACES_LIST)
    def list_click(self, control_id):
        item = self.venues.getSelectedItem()
        self.lat = float(item.getProperty("lat"))
        self.lon = float(item.getProperty("lon"))
        self.zoom = 12
        itemindex = item.getProperty("index")
        if itemindex != self.getProperty('index'):
            self.setProperty('index', itemindex)
            return None
        picture_path = item.getProperty("filepath")
        if picture_path:
            pos = slideshow.open(listitems=self.venues,
                                 index=self.getControl(control_id).getSelectedPosition())

    @ch.click(C_BUTTON_NAV)
    def quit_nav(self, control_id):
        self.previous_menu()

    @ch.click(C_ZOOM_IN)
    def zoom_in(self, control_id):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.street_view:
            if self.zoom_streetview <= 20:
                self.zoom_streetview += 1
        else:
            if self.zoom <= 20:
                self.zoom += 1

    @ch.click(C_ZOOM_OUT)
    def zoom_out(self, control_id):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.street_view:
            if self.zoom_streetview >= 1:
                self.zoom_streetview -= 1
        else:
            if self.zoom >= 1:
                self.zoom -= 1

    @ch.click(C_LOOK_UP)
    def pitch_up(self, control_id):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.pitch <= 80:
            self.pitch += 10

    @ch.click(C_LOOK_DOWN)
    def pitch_down(self, control_id):
        self.location = "%s,%s" % (self.lat, self.lon)
        if self.pitch >= -80:
            self.pitch -= 10

    @ch.click(C_NAV_MODE)
    @ch.action("contextmenu", "*")
    def toggle_nav_mode(self, control_id):
        if self.nav_mode_active:
            self.nav_mode_active = False
            self.clearProperty('NavMode')
            self.setFocusId(self.saved_id)
        else:
            self.saved_id = self.getFocusId()
            self.nav_mode_active = True
            self.setProperty('NavMode', 'True')
            self.setFocusId(C_BUTTON_NAV)

    @ch.click(C_MAPTYPE_TOGGLE)
    def toggle_map_mode(self, control_id):
        if self.type == "roadmap":
            self.type = "satellite"
        elif self.type == "satellite":
            self.type = "hybrid"
        elif self.type == "hybrid":
            self.type = "terrain"
        else:
            self.type = "roadmap"

    @ch.click(C_MODE_ROADMAP)
    def set_roadmap_type(self, control_id):
        self.type = "roadmap"

    @ch.click(C_MODE_HYBRID)
    def set_hybrid_type(self, control_id):
        self.type = "hybrid"

    @ch.click(C_MODE_SATELLITE)
    def set_satellite_type(self, control_id):
        self.type = "satellite"

    @ch.click(C_MODE_TERRAIN)
    def set_terrain_type(self, control_id):
        self.type = "terrain"

    @ch.click(C_STREET_VIEW)
    def toggle_street_mode(self, control_id):
        if self.street_view:
            self.clearProperty('streetview')
        else:
            self.clearProperty('map')
            self.setProperty('streetview', 'True')
        self.street_view = not self.street_view

    def search_location(self):
        self.location = xbmcgui.Dialog().input(heading=addon.LANG(32032),
                                               type=xbmcgui.INPUT_ALPHANUM)
        if not self.location:
            return None
        self.street_view = False
        data = googlemaps.get_coords_by_location(True, self.location)
        if data:
            self.lat, self.lon, self.zoom = data
        else:
            utils.notify("Error", "No Search results found.")

    @ch.click(C_SELECT_PROVIDER)
    def select_places_provider(self, control_id):
        self.clearProperty('index')
        items = None
        modeselect = [("geopics", addon.LANG(32027)),
                      ("eventful", addon.LANG(32028)),
                      ("foursquare", addon.LANG(32029)),
                      ("mapquest", addon.LANG(32030)),
                      ("googleplaces", addon.LANG(32031)),
                      ("reset", addon.LANG(32019))]
        listitems = [item[1] for item in modeselect]
        keys = [item[0] for item in modeselect]
        index = xbmcgui.Dialog().select(addon.LANG(32020), listitems)
        if index == -1:
            return None
        if keys[index] == "googleplaces":
            cat = GP.select_category()
            if cat is not None:
                items = GP.get_locations(self.lat, self.lon, self.radius * 1000, cat)
        elif keys[index] == "foursquare":
            section = FS.select_section()
            if not section:
                items = FS.get_places_by_section(self.lat, self.lon, section)
        elif keys[index] == "mapquest":
            items = MapQuest.get_incidents(self.lat, self.lon, self.zoom)
        elif keys[index] == "geopics":
            folder_path = xbmcgui.Dialog().browse(0, addon.LANG(32021), 'pictures')
            items = Utils.get_images(folder_path)
        elif keys[index] == "eventful":
            cat = EF.select_category()
            if cat is not None:
                items = EF.get_events(self.lat, self.lon, "", cat, self.radius)
        elif keys[index] == "reset":
            self.pins = ""
            items = []
        if items:
            self.pins = googlemaps.create_letter_pins(items)
            self.venues.reset()
            self.venues.addItems(items=utils.create_listitems(items))
            self.clearProperty("index")
        self.street_view = False

    @ch.click(C_SEARCH)
    def open_search_dialog(self, control_id):
        modeselect = [("googlemaps", addon.LANG(32024)),
                      ("foursquareplaces", addon.LANG(32004)),
                      ("reset", addon.LANG(32019))]
        KEYS = [item[0] for item in modeselect]
        VALUES = [item[1] for item in modeselect]
        index = xbmcgui.Dialog().select(addon.LANG(32026), VALUES)
        if index < 0:
            return None
        items = []
        if KEYS[index] == "googlemaps":
            self.search_location()
        elif KEYS[index] == "foursquareplaces":
            query = xbmcgui.Dialog().input(addon.LANG(32022), type=xbmcgui.INPUT_ALPHANUM)
            items = FS.get_places(self.lat, self.lon, query)
        elif KEYS[index] == "reset":
            self.pins = ""
        self.pins = googlemaps.create_letter_pins(items)
        self.venues.reset()
        self.venues.addItems(items=utils.create_listitems(items))
        self.clearProperty("index")
        self.street_view = False

    def update(self):
        googlemap = googlemaps.get_static_map(lat=self.lat,
                                              lon=self.lon,
                                              location=self.location,
                                              maptype=self.type,
                                              zoom=self.zoom,
                                              size="640x400")
        streetview_map = googlemaps.get_static_map(lat=self.lat,
                                                   lon=self.lon,
                                                   location=self.location,
                                                   maptype="roadmap",
                                                   zoom=15,
                                                   size="320x200")
        self.map_url = googlemap + self.pins
        self.streetview_url = googlemaps.get_streetview_image(lat=self.lat,
                                                              lon=self.lon,
                                                              location=self.location,
                                                              fov=120 - self.zoom_streetview * 6,
                                                              pitch=self.pitch,
                                                              heading=self.direction)
        props = {'location': self.location,
                 'lat': self.lat,
                 'lon': self.lon,
                 'zoomlevel': self.zoom,
                 'direction': self.direction / 18,
                 'type': self.type,
                 'aspect': self.aspect,
                 'map': self.map_url,
                 'streetview_map': streetview_map,
                 'streetview_image': self.streetview_url,
                 'streetview': "True" if self.street_view else "",
                 'NavMode': "True" if self.nav_mode_active else ""}
        for k, v in props.iteritems():
            self.setProperty(k, unicode(v))
        self.radius = Utils.get_radius(self.lat, self.lon, self.zoom, "640x400")
