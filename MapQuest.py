from Utils import *
import xbmcgui
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString

mapquest_key = "Fmjtd%7Cluur2hu829%2C75%3Do5-9wasd4"
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
max_limit = 25


class MapQuest():

    def __init__(self):
        pass

    def GetItemList(self, lat, lon, zoom):
        base_url = 'http://www.mapquestapi.com/traffic/v2/incidents?key=%s&inFormat=kvp' % (mapquest_key)
        mx, my = LatLonToMeters(lat, lon)
        px, py = MetersToPixels(mx, my, zoom)
        mxhigh, myhigh = PixelsToMeters(px + 320, py + 200, zoom)
        mxlow, mylow = PixelsToMeters(px - 320, py - 200, zoom)
        lathigh, lonhigh = MetersToLatLon(mxhigh, myhigh)
        latlow, lonlow = MetersToLatLon(mxlow, mylow)
        boundings = str(lathigh) + "," + str(lonhigh) + "," + str(latlow) + "," + str(lonlow)
        url = '&boundingBox=%s' % (boundings)
        log(base_url + url)
        results = Get_JSON_response(base_url, url)
        prettyprint(results)
        places_list = list()
        PinString = ""
        letter = ord('A')
        count = 0
        if results['info']['statuscode'] == 400:
            Notify("Error", " - ".join(results['info']['messages']))
            return [], ""
        elif "incidents" in results:
            for place in results['incidents']:
                if place['type'] == 1:
                    incidenttype = "Construction"
                elif place['type'] == 2:
                    incidenttype = "Event"
                elif place['type'] == 3:
                    incidenttype = "Congestion/Flow"
                elif place['type'] == 4:
                    incidenttype = "Incident/accident"
                item = xbmcgui.ListItem(place['shortDesc'])
                item.setArt({'thumb': place['iconURL']})
                item.setArt({'icon': place['iconURL']})
                item.setLabel(place['shortDesc'])
                item.setProperty('name', place['shortDesc'])
                item.setProperty('description', place['fullDesc'])
                item.setProperty('date', place['startTime'])
                item.setProperty('severity', str(place['severity']))
                item.setProperty('type', incidenttype)
                item.setLabel2(place['startTime'])
                item.setProperty("sortletter", chr(letter))
                item.setProperty("index", str(count))
                lat = str(place['lat'])
                lon = str(place['lng'])
                item.setProperty("lat", lat)
                item.setProperty("lon", lon)
                item.setProperty("index", str(count))
                PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(item)
                count += 1
                letter += 1
                if count > max_limit:
                    break
            FillArea = "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|%s,%s|%s,%s|%s,%s|%s,%s" % (lathigh, lonhigh, lathigh, lonlow, latlow, lonlow, latlow, lonhigh)
            PinString = PinString + FillArea.replace("|", "%7C")
            return places_list, PinString
          #  difference_lat = results['response']['suggestedBounds']['ne']['lat'] - results['response']['suggestedBounds']['sw']['lat']
           # difference_lon = results['response']['suggestedBounds']['ne']['lng'] - results['response']['suggestedBounds']['sw']['lng']
           # log(difference_lat)
        else:
            Notify("Error", "Could not fetch results")
            return [], ""
