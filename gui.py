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

ADDON = xbmcaddon.Addon()
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_NAME = ADDON.getAddonInfo('name')


GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
GOOGLE_STREETVIEW_KEY = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'


class GUI(xbmcgui.WindowXML):
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

    ACTION_CONTEXT_MENU = [117]
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    ACTION_EXIT_SCRIPT = [13]
    ACTION_0 = [58, 18]

    def __init__(self, skin_file, ADDON_PATH, *args, **kwargs):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.itemlist = []
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
                self.itemlist, self.pin_string = self.get_images(folder)
            elif param.startswith('artist='):
                artist = param[7:]
                LFM = LastFM()
                results = LFM.get_artist_events(artist)
                self.itemlist, self.pin_string = LFM.create_venue_list(results)
            elif param.startswith('list='):
                listtype = param[5:]
                self.zoom_level = 14
                if listtype == "nearfestivals":
                    LFM = LastFM()
                    results = LFM.get_near_events(self.lat, self.lon, self.radius, "", True)
                    self.itemlist, self.pin_string = LFM.create_venue_list(results)
                elif listtype == "nearconcerts":
                    LFM = LastFM()
                    results = LFM.get_near_events(self.lat, self.lon, self.radius)
                    self.itemlist, self.pin_string = LFM.create_venue_list(results)
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
            self.lat, self.lon = GetLocationCoordinates()
            self.zoom_level = 2
        elif (not self.location == "") and (self.strlat == ""):  # latlon empty
            self.lat, self.lon = self.get_geocodes(False, self.location)
        else:
            self.lat = float(self.strlat)
            self.lon = float(self.strlon)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        set_window_prop(self.window, 'NavMode', '')
        set_window_prop(self.window, 'streetview', '')
        if ADDON.getSetting("VenueLayout") == "1":
            set_window_prop(self.window, 'ListLayout', '1')
        else:
            set_window_prop(self.window, 'ListLayout', '0')
        self.venue_list = self.getControl(self.C_PLACES_LIST)
        self.get_map_urls()
        fill_list_control(self.venue_list, self.itemlist)
        self.window.setProperty("map_image", self.map_url)
        self.window.setProperty("streetview_image", self.street_view_url)
        settings = xbmcaddon.Addon(id='script.maps.browser')
        if not settings.getSetting('firststart') == "true":
            settings.setSetting(id='firststart', value='true')
            dialog = xbmcgui.Dialog()
            dialog.ok(ADDON_LANGUAGE(32001), ADDON_LANGUAGE(32002), ADDON_LANGUAGE(32003))
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
        self.venueid = None
        self.pin_string = ""
        self.direction = 0
        self.saved_id = 100
        self.prefix = ""
        self.radius = 50
        self.map_url = ""
        self.street_view_url = ""

    def onAction(self, action):
        action_id = action.getId()
        if action_id == xbmcgui.ACTION_SHOW_INFO:
            if ADDON.getSetting("InfoButtonAction") == "1":
                self.toggle_map_mode()
            else:
                if not self.street_view:
                    self.toggle_street_mode()
                    self.toggle_nav_mode()
                else:
                    self.toggle_street_mode()
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.toggle_nav_mode()
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.nav_mode_active or self.street_view:
                set_window_prop(self.window, 'NavMode', '')
                set_window_prop(self.window, 'streetview', '')
                self.nav_mode_active = False
                self.street_view = False
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif self.nav_mode_active:
            log("lat: " + str(self.lat) + " lon: " + str(self.lon))
            if not self.street_view:
                stepsize = 60.0 / pow(2, self.zoom_level)
                if action_id == xbmcgui.ACTION_MOVE_UP:
                    self.lat = float(self.lat) + stepsize
                elif action_id == xbmcgui.ACTION_MOVE_DOWN:
                    self.lat = float(self.lat) - stepsize
                elif action_id == xbmcgui.ACTION_MOVE_LEFT:
                    self.lon = float(self.lon) - 2.0 * stepsize
                elif action_id == xbmcgui.ACTION_MOVE_RIGHT:
                    self.lon = float(self.lon) + 2.0 * stepsize
            else:
                stepsize = 0.0002
                radiantdirection = float(radians(self.direction))
                if action_id == xbmcgui.ACTION_MOVE_UP:
                    self.lat = float(self.lat) + cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) + sin(radiantdirection) * float(stepsize)
                elif action_id == xbmcgui.ACTION_MOVE_DOWN:
                    self.lat = float(self.lat) - cos(radiantdirection) * float(stepsize)
                    self.lon = float(self.lon) - sin(radiantdirection) * float(stepsize)
                elif action_id == xbmcgui.ACTION_MOVE_LEFT:
                    if self.direction <= 0:
                        self.direction = 360
                    self.direction -= 18
                elif action_id == xbmcgui.ACTION_MOVE_RIGHT:
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
        self.get_map_urls()
        self.window.setProperty("streetview_image", self.street_view_url)
        self.window.setProperty("map_image", self.map_url)

    def onClick(self, control_id):
        if control_id == self.C_ZOOM_IN:
            self.zoom_in()
        elif control_id == self.C_ZOOM_OUT:
            self.zoom_out()
        elif control_id == self.C_SEARCH:
            self.open_search_dialog()
        elif control_id == self.C_MODE_TOGGLE:
            self.toggle_map_mode()
        elif control_id == self.C_STREET_VIEW:
            if not self.street_view:
                self.toggle_street_mode()
                self.toggle_nav_mode()
            else:
                self.toggle_street_mode()
        elif control_id == self.C_MODE_ROADMAP:
            self.type = "roadmap"
        elif control_id == self.C_MODE_SATELLITE:
            self.type = "satellite"
        elif control_id == self.C_MODE_HYBRID:
            self.type = "hybrid"
        elif control_id == self.C_MODE_TERRAIN:
            self.type = "terrain"
        elif control_id == self.C_GOTO_PLACE:
            self.location = self.window.getProperty("Location")
            self.lat, self.lon = self.get_geocodes(False, self.location)
        elif control_id == self.C_SELECT_PROVIDER:
            self.select_places_provider()
        elif control_id == self.C_LEFT:
            pass
        elif control_id == self.C_RIGHT:
            pass
        elif control_id == self.C_UP:
            pass
        elif control_id == self.C_DOWN:
            pass
        elif control_id == self.C_LOOK_UP:
            self.pitch_up()
        elif control_id == self.C_LOOK_DOWN:
            self.pitch_down()
        elif control_id == self.C_PLACES_LIST:
            selecteditem = self.venue_list.getSelectedItem()
            self.lat = float(selecteditem.getProperty("lat"))
            self.lon = float(selecteditem.getProperty("lon"))
            self.zoom_level = 12
            itemindex = selecteditem.getProperty("index")
            if not itemindex == self.window.getProperty('index'):
                set_window_prop(self.window, 'index', itemindex)
            else:
                event_id = selecteditem.getProperty("event_id")
                venue_id = selecteditem.getProperty("venue_id")
                foursquare_id = selecteditem.getProperty("foursquare_id")
                eventful_id = selecteditem.getProperty("eventful_id")
                picture_path = selecteditem.getProperty("filepath")
                if event_id:
                    dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, eventid=event_id)
                elif venue_id:
                    dialog = LastFMDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, venueid=venue_id)
                elif picture_path:
                    dialog = PictureDialog(u'script-%s-picturedialog.xml' % ADDON_NAME, ADDON_PATH, picture_path=picture_path)
                elif foursquare_id:
                    dialog = EventInfoDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, foursquare_id=foursquare_id)
                elif eventful_id:
                    dialog = EventInfoDialog(u'script-%s-dialog.xml' % ADDON_NAME, ADDON_PATH, eventful_id=eventful_id)
                dialog.doModal()
                if len(dialog.events_items) > 0:
                    self.pin_string = dialog.events_pin_string
                    fill_list_control(self.venue_list, dialog.events_items)
                del dialog
        self.get_map_urls()
        self.window.setProperty("streetview_image", self.street_view_url)
        self.window.setProperty("map_image", self.map_url)

    def zoom_in(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview <= 20:
                self.zoom_level_streetview += 1
        else:
            if self.zoom_level <= 20:
                self.zoom_level += 1

    def zoom_out(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview >= 1:
                self.zoom_level_streetview -= 1
        else:
            if self.zoom_level >= 1:
                self.zoom_level -= 1

    def pitch_up(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch <= 80:
            self.pitch += 10

    def pitch_down(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch >= -80:
            self.pitch -= 10

    def toggle_nav_mode(self):
        if self.nav_mode_active:
            self.nav_mode_active = False
            set_window_prop(self.window, 'NavMode', '')
            xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
        else:
            self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
            self.nav_mode_active = True
            set_window_prop(self.window, 'NavMode', 'True')
            xbmc.executebuiltin("SetFocus(725)")

    def toggle_map_mode(self):
        if self.type == "roadmap":
            self.type = "satellite"
        elif self.type == "satellite":
            self.type = "hybrid"
        elif self.type == "hybrid":
            self.type = "terrain"
        else:
            self.type = "roadmap"

    def toggle_street_mode(self):
        if self.street_view:
            self.street_view = False
            log("StreetView Off")
            self.zoom_level = self.zoom_level_saved
            set_window_prop(self.window, 'streetview', '')
        else:
            self.street_view = True
            log("StreetView On")
            self.zoom_level_saved = self.zoom_level
            self.zoom_level = 15
            set_window_prop(self.window, 'streetview', 'True')

    def search_location(self):
        self.location = xbmcgui.Dialog().input(ADDON_LANGUAGE(32032), type=xbmcgui.INPUT_ALPHANUM)
        if not self.location == "":
            self.street_view = False
            lat, lon = self.get_geocodes(True, self.location)
            if lat is not None:
                self.lat = lat
                self.lon = lon
            else:
                Notify("Error", "No Search results found.")

    def select_places_provider(self):
        set_window_prop(self.window, 'index', "")
        itemlist = None
        modeselect = [ADDON_LANGUAGE(32016),  # concerts
                      ADDON_LANGUAGE(32017),  # festivals
                      ADDON_LANGUAGE(32027),  # geopics
                      ADDON_LANGUAGE(32028),  # eventful
                      ADDON_LANGUAGE(32029),  # FourSquare
                      ADDON_LANGUAGE(32030),  # MapQuest
                      ADDON_LANGUAGE(32031),  # Google Places
                      ADDON_LANGUAGE(32019)]  # reset
        dialog = xbmcgui.Dialog()
        index = dialog.select(ADDON_LANGUAGE(32020), modeselect)
        if not index < 0:
            if modeselect[index] == ADDON_LANGUAGE(32031):
                GP = GooglePlaces()
                category = GP.select_category()
                if category is not None:
                    self.pin_string, itemlist = GP.GetGooglePlacesList(self.lat, self.lon, self.radius * 1000, category)
            elif modeselect[index] == ADDON_LANGUAGE(32029):
                FS = FourSquare()
                section = FS.SelectSection()
                if section is not None:
                    itemlist, self.pin_string = FS.GetPlacesListExplore(self.lat, self.lon, section)
            elif modeselect[index] == ADDON_LANGUAGE(32016):
                LFM = LastFM()
                category = LFM.select_category()
                if category is not None:
                    results = LFM.get_near_events(self.lat, self.lon, self.radius, category)
                    itemlist, self.pin_string = LFM.create_venue_list(results)
            elif modeselect[index] == ADDON_LANGUAGE(32030):
                MQ = MapQuest()
                itemlist, self.pin_string = MQ.GetItemList(self.lat, self.lon, self.zoom_level)
            elif modeselect[index] == ADDON_LANGUAGE(32017):
                LFM = LastFM()
                category = LFM.select_category()
                if category is not None:
                    results = LFM.get_near_events(self.lat, self.lon, self.radius, category, True)
                    itemlist, self.pin_string = LFM.create_venue_list(results)
            elif modeselect[index] == ADDON_LANGUAGE(32027):
                folder_path = xbmcgui.Dialog().browse(0, ADDON_LANGUAGE(32021), 'pictures')
                set_window_prop(self.window, 'imagepath', folder_path)
                itemlist, self.pin_string = get_images(folder_path)
            elif modeselect[index] == ADDON_LANGUAGE(32028):
                EF = Eventful()
                category = EF.select_category()
                if category is not None:
                    itemlist, self.pin_string = EF.GetEventfulEventList(self.lat, self.lon, "", category, self.radius)
            elif modeselect[index] == ADDON_LANGUAGE(32019):
                self.pin_string = ""
                itemlist = []
            if itemlist is not None:
                fill_list_control(self.venue_list, itemlist)
            self.street_view = False

    def open_search_dialog(self):
        modeselect = {"googlemaps": ADDON_LANGUAGE(32024),
                      "foursquareplaces": ADDON_LANGUAGE(32004),
                      "lastfmconcerts": ADDON_LANGUAGE(32023),
                      "lastfmvenues": ADDON_LANGUAGE(32033),
                      "reset": ADDON_LANGUAGE(32019)}
        KEYS = [item for item in modeselect.keys()]
        VALUES = [item for item in modeselect.values()]
        dialog = xbmcgui.Dialog()
        index = dialog.select(ADDON_LANGUAGE(32026), VALUES)
        if index < 0:
            return None
        if KEYS[index] == "googlemaps":
            self.search_location()
            itemlist = []
        elif KEYS[index] == "foursquareplaces":
            query = xbmcgui.Dialog().input(ADDON_LANGUAGE(32022), type=xbmcgui.INPUT_ALPHANUM)
            FS = FourSquare()
            itemlist, self.pin_string = FS.GetPlacesList(self.lat, self.lon, query)
        elif KEYS[index] == "lastfmconcerts":
            artist = xbmcgui.Dialog().input(ADDON_LANGUAGE(32025), type=xbmcgui.INPUT_ALPHANUM)
            LFM = LastFM()
            results = LFM.get_artist_events(artist)
            itemlist, self.pin_string = LFM.create_venue_list(results)
        elif KEYS[index] == "lastfmvenues":
            venue = xbmcgui.Dialog().input(ADDON_LANGUAGE(32025), type=xbmcgui.INPUT_ALPHANUM)
            LFM = LastFM()
            venueid = LFM.get_venue_id(venue)
            results = LFM.get_venue_events(venueid)
            itemlist, self.pin_string = LFM.create_venue_list(results)
        elif KEYS[index] == "reset":
            self.pin_string = ""
            itemlist = []
        fill_list_control(self.venue_list, itemlist)
        self.street_view = False

    def toggle_info(self):
        self.show_info = not self.show_info
        self.info_controller.setVisible(self.show_info)

    def get_map_urls(self):
        if self.street_view is True:
            size = "320x200"
        else:
            size = "640x400"
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
        if self.radius > 500:
            self.radius = 500
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
        try:
            search_string = urllib.quote_plus(search_string)
            base_url = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false"
            url = "&address=%s" % (search_string)
            log("Google Geocodes Search:" + url)
            results = Get_JSON_response(base_url + url)
            places_list = []
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
                places_list.append(prop_list)
            first_hit = results["results"][0]["geometry"]["location"]
            if show_dialog:
                if len(results["results"]) > 1:  # open dialog when more than one hit
                    w = Search_Select_Dialog('DialogSelect.xml', ADDON_PATH, listing=create_listitems(places_list))
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
        except Exception as e:
            log("Exception in get_geocodes")
            log(e)
            return (None, None)
