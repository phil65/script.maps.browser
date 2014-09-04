import xbmc
import xbmcaddon
import xbmcvfs
import urllib2
import os
import sys
import re
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString


Addon_Data_Path = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % __addonid__).decode("utf-8"))


def getWindowProperty(window, key):
    return window.getProperty(key)


def setWindowProperty(window, key, value):
  #  log("Key: " + key + " value:" + value)
    return window.setProperty(key, value)


def GetStringFromUrl(encurl):
    succeed = 0
    while succeed < 5:
        try:
            req = urllib2.Request(encurl)
            req.add_header('User-agent', 'XBMC/13.2 ( ptemming@gmx.net )')
            res = urllib2.urlopen(req)
            html = res.read()
       #     log("URL String: " + html)
            return html
        except:
            log("could not get data from %s" % encurl)
            xbmc.sleep(1000)
            succeed += 1
    return ""


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


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
            log("error when loading file")
            log(fc)
            return []
    else:
        return False


def cleanText(text):
    import re
    text = re.sub('<br \/>', '[CR]', text)
    text = re.sub('<(.|\n|\r)*?>', '', text)
    text = re.sub('&quot;', '"', text)
    text = re.sub('&amp;', '&', text)
    text = re.sub('&gt;', '>', text)
    text = re.sub('&lt;', '<', text)
    text = re.sub('User-contributed text is available under the Creative Commons By-SA License and may also be available under the GNU FDL.', '', text)
    return text.strip()


def Notify(header, line='', line2='', line3=''):
    xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (header, line, line2, line3))


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))
