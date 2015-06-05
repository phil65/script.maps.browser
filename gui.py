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
        self.init_vars()
        for arg in sys.argv:
            param = arg.lower()
            log("param = " + param)
            if param.startswith('aspect='):
                self.aspect = param[7:]
            elif param.startswith('folder='):
                folder = param[7:]
                self.itemlist, self.PinString = self.GetImages(folder)
            elif param.startswith('artist='):
                artist = param[7:]
                LFM = LastFM()
                results = LFM.GetArtistEvents(artist)
                self.itemlist, self.PinString = LFM.CreateVenueList(results)
            elif param.startswith('list='):
                listtype = param[5:]
                self.zoom_level = 14
                if listtype == "nearfestivals":
                    LFM = LastFM()
                    results = LFM.GetNearEvents(self.lat, self.lon, self.radius, "", True)
                    self.itemlist, self.PinString = LFM.CreateVenueList(results)
                elif listtype == "nearconcerts":
                    LFM = LastFM()
                    results = LFM.GetNearEvents(self.lat, self.lon, self.radius)
                    self.itemlist, self.PinString = LFM.CreateVenueList(results)
            elif param.startswith('direction='):
                self.direction = param[10:]
            elif param.startswith('prefix='):
                self.prefix = param[7:]
                if not self.prefix.endswith('.') and self.prefix != "":
                    self.prefix = self.prefix + '.'
            # get lat / lon values
        if self.location == "geocode":
            self.lat, self.lon = ParseGeoTags(self.strlat, self.strlon)
        elif (self.location == "") and (self.strlat == ""):  # both empty
            self.lat, self.lon = GetLocationCoordinates()
            self.zoom_level = 2
        elif (not self.location == "") and (self.strlat == ""):  # latlon empty
            self.lat, self.lon = self.GetGeoCodes(False, self.location)
        else:
            self.lat = float(self.strlat)
            self.lon = float(self.strlon)
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        setWindowProperty(self.window, 'NavMode', '')
        setWindowProperty(self.window, 'streetview', '')
        if ADDON.getSetting("VenueLayout") == "1":
            setWindowProperty(self.window, 'ListLayout', '1')
        else:
            setWindowProperty(self.window, 'ListLayout', '0')
        self.venuelist = self.getControl(self.C_PLACES_LIST)
        self.GetGoogleMapURLs()
        FillListControl(self.venuelist, self.itemlist)
        self.window.setProperty("map_image", self.GoogleMapURL)
        self.window.setProperty("streetview_image", self.GoogleStreetViewURL)
        settings = xbmcaddon.Addon(id='script.maps.browser')
        if not settings.getSetting('firststart') == "true":
            settings.setSetting(id='firststart', value='true')
            dialog = xbmcgui.Dialog()
            dialog.ok(ADDON_LANGUAGE(32001), ADDON_LANGUAGE(32002), ADDON_LANGUAGE(32003))
        log('onInit finished')

    def init_vars(self):
        self.NavMode_active = False
        self.street_view = False
        self.search_string = ""
        self.zoom_level_saved = 10
        self.zoom_level_streetview = 0
        self.lat = 0.0
        self.lon = 0.0
        self.pitch = 0
        self.venueid = None
        self.PinString = ""
        self.direction = 0
        self.saved_id = 100
        self.aspect = "640x400"
        self.prefix = ""
        self.radius = 50
        self.GoogleMapURL = ""
        self.GoogleStreetViewURL = ""

    def onAction(self, action):
        action_id = action.getId()
        if action_id == xbmcgui.ACTION_SHOW_INFO:
            if ADDON.getSetting("InfoButtonAction") == "1":
                self.ToggleMapMode()
            else:
                if not self.street_view:
                    self.ToggleStreetMode()
                    self.ToggleNavMode()
                else:
                    self.ToggleStreetMode()
        elif action_id in self.ACTION_CONTEXT_MENU:
            self.ToggleNavMode()
        elif action_id in self.ACTION_PREVIOUS_MENU:
            if self.NavMode_active or self.street_view:
                setWindowProperty(self.window, 'NavMode', '')
                setWindowProperty(self.window, 'streetview', '')
                self.NavMode_active = False
                self.street_view = False
                xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
            else:
                self.close()
        elif action_id in self.ACTION_EXIT_SCRIPT:
            self.close()
        elif self.NavMode_active:
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
        self.GetGoogleMapURLs()
        self.window.setProperty("streetview_image", self.GoogleStreetViewURL)
        self.window.setProperty("map_image", self.GoogleMapURL)

    def onClick(self, controlId):
        if controlId == self.C_ZOOM_IN:
            self.ZoomIn()
        elif controlId == self.C_ZOOM_OUT:
            self.ZoomOut()
        elif controlId == self.C_SEARCH:
            self.SearchDialog()
        elif controlId == self.C_MODE_TOGGLE:
            self.ToggleMapMode()
        elif controlId == self.C_STREET_VIEW:
            if not self.street_view:
                self.ToggleStreetMode()
                self.ToggleNavMode()
            else:
                self.ToggleStreetMode()
        elif controlId == self.C_MODE_ROADMAP:
            self.type = "roadmap"
        elif controlId == self.C_MODE_SATELLITE:
            self.type = "satellite"
        elif controlId == self.C_MODE_HYBRID:
            self.type = "hybrid"
        elif controlId == self.C_MODE_TERRAIN:
            self.type = "terrain"
        elif controlId == self.C_GOTO_PLACE:
            self.location = self.window.getProperty("Location")
            self.lat, self.lon = self.GetGeoCodes(False, self.location)
        elif controlId == self.C_SELECT_PROVIDER:
            self.SelectPlacesProvider()
        elif controlId == self.C_LEFT:
            pass
        elif controlId == self.C_RIGHT:
            pass
        elif controlId == self.C_UP:
            pass
        elif controlId == self.C_DOWN:
            pass
        elif controlId == self.C_LOOK_UP:
            self.PitchUp()
        elif controlId == self.C_LOOK_DOWN:
            self.PitchDown()
        elif controlId == self.C_PLACES_LIST:
            selecteditem = self.venuelist.getSelectedItem()
            self.lat = float(selecteditem.getProperty("lat"))
            self.lon = float(selecteditem.getProperty("lon"))
            self.zoom_level = 12
            itemindex = selecteditem.getProperty("index")
            if not itemindex == self.window.getProperty('index'):
                setWindowProperty(self.window, 'index', itemindex)
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
                if len(dialog.GetEventsitemlist) > 0:
                    self.PinString = dialog.GetEventsPinString
                    FillListControl(self.venuelist, dialog.GetEventsitemlist)
                del dialog
        self.GetGoogleMapURLs()
        self.window.setProperty("streetview_image", self.GoogleStreetViewURL)
        self.window.setProperty("map_image", self.GoogleMapURL)

    def ZoomIn(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview <= 20:
                self.zoom_level_streetview += 1
        else:
            if self.zoom_level <= 20:
                self.zoom_level += 1

    def ZoomOut(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.street_view:
            if self.zoom_level_streetview >= 1:
                self.zoom_level_streetview -= 1
        else:
            if self.zoom_level >= 1:
                self.zoom_level -= 1

    def PitchUp(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch <= 80:
            self.pitch += 10

    def PitchDown(self):
        self.location = str(self.lat) + "," + str(self.lon)
        if self.pitch >= -80:
            self.pitch -= 10

    def ToggleNavMode(self):
        if self.NavMode_active:
            self.NavMode_active = False
            setWindowProperty(self.window, 'NavMode', '')
            xbmc.executebuiltin("SetFocus(" + str(self.saved_id) + ")")
        else:
            self.saved_id = xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId()
            self.NavMode_active = True
            setWindowProperty(self.window, 'NavMode', 'True')
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

    def ToggleStreetMode(self):
        if self.street_view:
            self.street_view = False
            log("StreetView Off")
            self.zoom_level = self.zoom_level_saved
            setWindowProperty(self.window, 'streetview', '')
        else:
            self.street_view = True
            log("StreetView On")
            self.zoom_level_saved = self.zoom_level
            self.zoom_level = 15
            setWindowProperty(self.window, 'streetview', 'True')

    def SearchLocation(self):
        self.location = xbmcgui.Dialog().input(ADDON_LANGUAGE(32032), type=xbmcgui.INPUT_ALPHANUM)
        if not self.location == "":
            self.street_view = False
            lat, lon = self.GetGeoCodes(True, self.location)
            if lat is not None:
                self.lat = lat
                self.lon = lon
            else:
                Notify("Error", "No Search results found.")

    def SelectPlacesProvider(self):
        setWindowProperty(self.window, 'index', "")
        itemlist = None
        modeselect = [ADDON_LANGUAGE(32016),  # concerts
                      ADDON_LANGUAGE(32017),  # festivals
                      ADDON_LANGUAGE(32027),  # geopics
                      ADDON_LANGUAGE(32028),  # eventful
                      ADDON_LANGUAGE(32029),  # FourSquare
                      ADDON_LANGUAGE(32030),  # MapQuest
                      ADDON_LANGUAGE(32031),  # Google Places
                      ADDON_LANGUAGE(32019)]  # reset
        dialogSelection = xbmcgui.Dialog()
        provider_index = dialogSelection.select(ADDON_LANGUAGE(32020), modeselect)
        if not provider_index < 0:
            if modeselect[provider_index] == ADDON_LANGUAGE(32031):
                GP = GooglePlaces()
                category = GP.SelectCategory()
                if category is not None:
                    self.PinString, itemlist = GP.GetGooglePlacesList(self.lat, self.lon, self.radius * 1000, category)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32029):
                FS = FourSquare()
                section = FS.SelectSection()
                if section is not None:
                    itemlist, self.PinString = FS.GetPlacesListExplore(self.lat, self.lon, section)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32016):
                LFM = LastFM()
                category = LFM.SelectCategory()
                if category is not None:
                    results = LFM.GetNearEvents(self.lat, self.lon, self.radius, category)
                    itemlist, self.PinString = LFM.CreateVenueList(results)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32030):
                MQ = MapQuest()
                itemlist, self.PinString = MQ.GetItemList(self.lat, self.lon, self.zoom_level)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32017):
                LFM = LastFM()
                category = LFM.SelectCategory()
                if category is not None:
                    results = LFM.GetNearEvents(self.lat, self.lon, self.radius, category, True)
                    itemlist, self.PinString = LFM.CreateVenueList(results)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32027):
                folder_path = xbmcgui.Dialog().browse(0, ADDON_LANGUAGE(32021), 'pictures')
                setWindowProperty(self.window, 'imagepath', folder_path)
                itemlist, self.PinString = GetImages(folder_path)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32028):
                EF = Eventful()
                category = EF.SelectCategory()
                if category is not None:
                    itemlist, self.PinString = EF.GetEventfulEventList(self.lat, self.lon, "", category, self.radius)
            elif modeselect[provider_index] == ADDON_LANGUAGE(32019):
                self.PinString = ""
                itemlist = []
            if itemlist is not None:
                FillListControl(self.venuelist, itemlist)
            self.street_view = False

    def SearchDialog(self):
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
            self.SearchLocation()
            itemlist = []
        elif KEYS[index] == "foursquareplaces":
            query = xbmcgui.Dialog().input(ADDON_LANGUAGE(32022), type=xbmcgui.INPUT_ALPHANUM)
            FS = FourSquare()
            itemlist, self.PinString = FS.GetPlacesList(self.lat, self.lon, query)
        elif KEYS[index] == "lastfmconcerts":
            artist = xbmcgui.Dialog().input(ADDON_LANGUAGE(32025), type=xbmcgui.INPUT_ALPHANUM)
            LFM = LastFM()
            results = LFM.GetArtistEvents(artist)
            itemlist, self.PinString = LFM.CreateVenueList(results)
        elif KEYS[index] == "lastfmvenues":
            venue = xbmcgui.Dialog().input(ADDON_LANGUAGE(32025), type=xbmcgui.INPUT_ALPHANUM)
            LFM = LastFM()
            venueid = LFM.GetVenueID(venue)
            results = LFM.GetVenueEvents(venueid)
            itemlist, self.PinString = LFM.CreateVenueList(results)
        elif KEYS[index] == "reset":
            self.PinString = ""
            itemlist = []
        FillListControl(self.venuelist, itemlist)
        self.street_view = False

    def toggleInfo(self):
        self.show_info = not self.show_info
        self.info_controller.setVisible(self.show_info)

    def GetGoogleMapURLs(self):
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
        self.GoogleMapURL = url + self.PinString
        zoom = 120 - int(self.zoom_level_streetview) * 6
        base_url = 'http://maps.googleapis.com/maps/api/streetview?&sensor=false&format=%s&' % (ADDON.getSetting("ImageFormat"))
        self.GoogleStreetViewURL = base_url + 'location=%s&size=640x400&fov=%s&key=%s&heading=%s&pitch=%s' % (self.search_string, str(zoom), GOOGLE_STREETVIEW_KEY, str(self.direction), str(self.pitch))
        setWindowProperty(self.window, self.prefix + 'location', self.location)
        setWindowProperty(self.window, self.prefix + 'lat', str(self.lat))
        setWindowProperty(self.window, self.prefix + 'lon', str(self.lon))
        setWindowProperty(self.window, self.prefix + 'zoomlevel', str(self.zoom_level))
        setWindowProperty(self.window, self.prefix + 'direction', str(self.direction / 18))
        setWindowProperty(self.window, self.prefix + 'type', self.type)
        setWindowProperty(self.window, self.prefix + 'aspect', self.aspect)
        setWindowProperty(self.window, self.prefix + 'map_image', self.GoogleMapURL)
        setWindowProperty(self.window, self.prefix + 'streetview_image', self.GoogleStreetViewURL)
        hor_px = int(size.split("x")[0])
        ver_px = int(size.split("x")[1])
        mx, my = LatLonToMeters(self.lat, self.lon)
        px, py = MetersToPixels(mx, my, self.zoom_level)
        mx2, my2 = PixelsToMeters(px + hor_px / 2, py + ver_px / 2, self.zoom_level)
        self.radiusx = abs((mx - mx2) / 2000)
        self.radius = abs((my - my2) / 2000)
        if self.radius > 500:
            self.radius = 500
        cache_path = xbmc.getCacheThumbName(self.GoogleMapURL)
        log(cache_path)
        if self.prefix == "":
            if self.street_view:
                setWindowProperty(self.window, self.prefix + 'streetview', "True")
            else:
                setWindowProperty(self.window, self.prefix + 'streetview', "")
            if self.NavMode_active:
                setWindowProperty(self.window, self.prefix + 'NavMode', "True")
            else:
                setWindowProperty(self.window, self.prefix + 'NavMode', "")

    def GetGeoCodes(self, show_dialog, search_string):
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
                    w = Search_Select_Dialog('DialogSelect.xml', ADDON_PATH, listing=CreateListItems(places_list))
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
            log("Exception in GetGeoCodes")
            log(e)
            return (None, None)
