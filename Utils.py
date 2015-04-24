import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import urllib2
import os
import re
import time
import math
from PIL import Image
import hashlib
from ImageTags import *
import simplejson

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID).decode("utf-8"))
TILESIZE = 256
INITIAL_RESOLUTION = 2 * math.pi * 6378137 / TILESIZE
# 156543.03392804062 for tileSize 256 pixels
ORIGIN_SHIFT = 2 * math.pi * 6378137 / 2.0
# 20037508.342789244


def LatLonToMeters(lat, lon):
    "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"
    if not lon:
        return None
    mx = lon * ORIGIN_SHIFT / 180.0
    my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    my = my * ORIGIN_SHIFT / 180.0
    return mx, my


def FillListControl(listcontrol, listitem_dict):
    listcontrol.reset()
    listitems = CreateListItems(listitem_dict)
    listcontrol.addItems(items=listitems)
    setWindowProperty(xbmcgui.Window(xbmcgui.getCurrentWindowId()), 'index', "")


def MetersToPixels(mx, my, zoom):
    "Converts EPSG:900913 to pyramid pixel coordinates in given zoom level"

    res = INITIAL_RESOLUTION / (2 ** zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py


def PixelsToMeters(px, py, zoom):
    "Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"

    res = INITIAL_RESOLUTION / (2 ** zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    return mx, my


def MetersToLatLon(mx, my):
    "Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum"

    lon = (mx / ORIGIN_SHIFT) * 180.0
    lat = (my / ORIGIN_SHIFT) * 180.0

    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon


def setWindowProperty(window, key, value):
    return window.setProperty(key, value)


def GetStringFromUrl(encurl):
    succeed = 0
    while (succeed < 5) and (not xbmc.abortRequested):
        try:
            request = urllib2.Request(encurl)
            request.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
           # request.add_header('Accept-encoding', 'gzip')
            response = urllib2.urlopen(request)
           # if response.info().get('Content-Encoding') == 'gzip':
           #     buf = StringIO(response.read())
           #     compr = gzip.GzipFile(fileobj=buf)
           #     data = compr.read()
           # else:
            data = response.read()
            return data
        except:
            Notify("Error", "Could not download data. Internet connection OK?")
            log("GetStringFromURL: could not get data from %s" % encurl)
            xbmc.sleep(1000)
            succeed += 1
    return ""


def Get_JSON_response(base_url="", custom_url="", cache_days=0.5):
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    filename = hashlib.md5(custom_url).hexdigest()
    path = xbmc.translatePath(ADDON_DATA_PATH + "/" + filename + ".txt")
    cache_seconds = int(cache_days * 86400.0)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < cache_seconds):
        results = read_from_file(path)
    else:
        url = base_url + custom_url
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
        save_to_file(results, filename, ADDON_DATA_PATH)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    return results


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDON_ID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def GetImages(path=""):
    PinString = "&markers=color:blue"
    letter = ord('A')
    count = 0
    images_list = list()
    for filename in xbmcvfs.listdir(path)[-1]:
        try:
            img = Image.open(path + filename)
            exif_data = get_exif_data(img)
            lat, lon = get_lat_lon(exif_data)
            if "DateTimeOriginal" in exif_data:
                date = exif_data["DateTimeOriginal"]
            elif "DateTime" in exif_data:
                date = exif_data["DateTime"]
            else:
                date = ""
            if lat:
                prop_list = {"name": filename,
                             "label": filename,
                             "lat": str(lat),
                             "lon": str(lon),
                             "date": date,
                             "description": date,
                             "thumb": path + filename,
                             "filepath": path + filename,
                             "index": str(count),
                             "sortletter": chr(letter),
                             }
                if len(PinString) < 1850:
                    PinString = PinString + "%7C" + str(lat) + "," + str(lon)
                    letter += 1
                images_list.append(prop_list)
                count += 1
        except Exception as e:
            log("Error when handling GetImages results")
            log(e)
    return images_list, PinString


def string2deg(string):
    string = string.strip().replace('"', '').replace("'", "")
    log("String:" + string)
    if string[0].lower() == "w" or string[0].lower() == "s":
        negative = True
    else:
        negative = False
    string = string[1:]
    string = string.replace("d", "")
    string = string.replace("  ", " ")
    div = '[|:|\s]'  # allowable field delimiters "|", ":", whitespace
    sdec = '(\d{1,3})' + div + '(\d{1,2})' + div + '(\d{1,2}\.?\d+?)'
    co_re = re.compile(sdec)
    co_search = co_re.search(string)
    if co_search is None:
        raise ValueError("Invalid input string: %s" % string)
    elems = co_search.groups()
    degrees = float(elems[0])
    arcminutes = float(elems[1])
    arcseconds = float(elems[2])
    decDegrees = degrees + arcminutes / 60.0 + arcseconds / 3600.0
    if negative:
        decDegrees = -1.0 * decDegrees
    return decDegrees


def ParseGeoTags(lat, lon):
    if not lon == "":
        lat = float(string2deg(lat))
        lon = float(string2deg(lon))
    else:
        coords = lat.split(",lon=")
        lat = float(string2deg(coords[0]))
        lon = float(string2deg(coords[1]))
    return lat, lon


def CreateListItem(json_array):
    item = xbmcgui.ListItem("Undefined")
    for key, value in json_array.iteritems():
        item.setProperty(key, value)
        if key in ["thumb", "poster", "banner", "icon"]:
            item.setArt({key: value})
        elif key == "label":
            item.setLabel(value)
        elif key == "label2":
            item.setLabel2(value)
    item.setProperty("item_info", simplejson.dumps(json_array))
    return item


def CreateListItems(data):
    itemlist = []
    if data:
        for (count, result) in enumerate(data):
            listitem = xbmcgui.ListItem('%s' % (str(count)))
            itempath = ""
            for (key, value) in result.iteritems():
                if str(key).lower() in ["name", "label", "title"]:
                    listitem.setLabel(unicode(value))
                if str(key).lower() in ["thumb"]:
                    listitem.setThumbnailImage(unicode(value))
                if str(key).lower() in ["icon"]:
                    listitem.setIconImage(unicode(value))
                if str(key).lower() in ["thumb", "poster", "banner", "fanart", "clearart", "clearlogo", "landscape", "discart", "characterart", "tvshow.fanart", "tvshow.poster", "tvshow.banner", "tvshow.clearart", "tvshow.characterart"]:
                    listitem.setArt({str(key).lower(): unicode(value)})
                if str(key).lower() in ["path"]:
                    itempath = unicode(value)
                listitem.setProperty('%s' % (str(key)), unicode(value))
            listitem.setPath(path=itempath)
            listitem.setProperty("target_url", itempath)
            listitem.setProperty("node:target_url", itempath)
            listitem.setProperty("node.target_url", itempath)
            listitem.setProperty("item_info", simplejson.dumps(unicode(result)))
            itemlist.append(listitem)
    return itemlist


def GetLocationCoordinates():
    url = 'http://www.telize.com/geoip'
    response = GetStringFromUrl(url)
    results = simplejson.loads(response)
    lat = results["latitude"]
    lon = results["longitude"]
    return lat, lon


def save_to_file(content, filename, path=""):
    if path == "":
        text_file_path = get_browse_dialog() + filename + ".txt"
    else:
        if not xbmcvfs.exists(path):
            xbmcvfs.mkdir(path)
        text_file_path = os.path.join(path, filename + ".txt")
    log("save to textfile:")
    log(text_file_path)
    text_file = xbmcvfs.File(text_file_path, "w")
    simplejson.dump(content, text_file)
    text_file.close()
    return True


def read_from_file(path=""):
    log("trying to load " + path)
    # Set path
    if path == "":
        path = get_browse_dialog(dlg_type=1)
    # Check to see if file exists
    if xbmcvfs.exists(path):
        f = open(path)
        fc = simplejson.load(f)
        log("loaded textfile " + path)
        try:
            return fc
        except:
            Notify("Exception in read_from_file()")
            log(fc)
            return []
    else:
        return False


def cleanText(text):
    import re
    if text:
        text = re.sub('<br \/>', '[CR]', text)
        text = re.sub('<br\/>', '[CR]', text)
        text = re.sub('<(.|\n|\r)*?>', '', text)
        text = re.sub('&quot;', '"', text)
        text = re.sub('<*>', '', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('&gt;', '>', text)
        text = re.sub('&lt;', '<', text)
        text = re.sub('&#;', "'", text)
        text = re.sub('&#39;', "'", text)
        text = re.sub('<i>', '[I]', text)
        text = re.sub('<\/i>', '[/I]', text)
        text = re.sub('<strong>', '[B]', text)
        text = re.sub('<\/strong>', '[/B]', text)
        text = re.sub('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.', '', text)
        return text.strip()
    else:
        return ""


class PictureDialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]
    C_ARTIST_LIST = 500

    def __init__(self, *args, **kwargs):
        self.picture_path = kwargs.get('picture_path')

    def onInit(self):
        self.getControl(100).setImage(self.picture_path)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        pass

    def onFocus(self, controlID):
        pass


def Notify(header="", message="", icon=ADDON_ICON, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    dialog.notification(heading=header, message=message, icon=icon, time=time, sound=sound)


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))
