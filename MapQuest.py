from Utils import *

MAPQUEST_KEY = "Fmjtd%7Cluur2hu829%2C75%3Do5-9wasd4"
GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
MAX_LIMIT = 25
BASE_URL = 'http://www.mapquestapi.com/traffic/v2/'


class MapQuest():

    def __init__(self):
        pass

    def GetItemList(self, lat, lon, zoom):
        mx, my = LatLonToMeters(lat, lon)
        px, py = MetersToPixels(mx, my, zoom)
        mxhigh, myhigh = PixelsToMeters(px + 320, py + 200, zoom)
        mxlow, mylow = PixelsToMeters(px - 320, py - 200, zoom)
        lathigh, lonhigh = MetersToLatLon(mxhigh, myhigh)
        latlow, lonlow = MetersToLatLon(mxlow, mylow)
        boundings = str(lathigh) + "," + str(lonhigh) + "," + str(latlow) + "," + str(lonlow)
        url = '%sincidents?key=%s&inFormat=kvp&boundingBox=%s' % (BASE_URL, MAPQUEST_KEY, boundings)
        results = Get_JSON_response(url)
        places_list = []
        PinString = ""
        letter = ord('A')
        count = 0
        if results['info']['statuscode'] == 400:
            Notify("Error", " - ".join(results['info']['messages']))
            return [], ""
        elif "incidents" in results:
            for place in results['incidents']:
                lat = str(place['lat'])
                lon = str(place['lng'])
                url = "flow?key=%s&mapLat=%s&mapLng=%s&mapHeight=400&mapWidth=400&mapScale=433342" % (MAPQUEST_KEY, lat, lon)
                image = base_url + url
                search_string = lat + "," + lon
                googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
                if place['type'] == 1:
                    incidenttype = "Construction"
                elif place['type'] == 2:
                    incidenttype = "Event"
                elif place['type'] == 3:
                    incidenttype = "Congestion / Flow"
                elif place['type'] == 4:
                    incidenttype = "Incident / Accident"
                prop_list = {'name': place['shortDesc'],
                             'label': place['shortDesc'],
                             'label2': place['startTime'],
                             'description': place['fullDesc'],
                             'distance': str(place['distance']),
                             'delaytypical': str(place['delayFromTypical']),
                             'delayfreeflow': str(place['delayFromFreeFlow']),
                             "GoogleMap": googlemap,
                             "venue_image": image,
                             "thumb": image,
                             "icon": place['iconURL'],
                             'date': place['startTime'],
                             'severity': str(place['severity']),
                             'type': incidenttype,
                             "sortletter": chr(letter),
                             "lat": lat,
                             "lon": lon,
                             "index": str(count)}
                PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(prop_list)
                count += 1
                letter += 1
                if count > MAX_LIMIT:
                    break
            FillArea = "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|%s,%s|%s,%s|%s,%s|%s,%s" % (lathigh, lonhigh, lathigh, lonlow, latlow, lonlow, latlow, lonhigh)
            PinString = PinString + FillArea.replace("|", "%7C")
            return places_list, PinString
        else:
            Notify("Error", "Could not fetch results")
            return [], ""
