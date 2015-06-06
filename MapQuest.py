from Utils import *

MAPQUEST_KEY = "Fmjtd%7Cluur2hu829%2C75%3Do5-9wasd4"
GOOGLE_MAPS_KEY = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
MAX_LIMIT = 25
BASE_URL = 'http://www.mapquestapi.com/traffic/v2/'


class MapQuest():

    def __init__(self):
        pass

    def GetItemList(self, lat, lon, zoom):
        mx, my = latlon_to_meters(lat, lon)
        px, py = meters_to_pixels(mx, my, zoom)
        mx_high, my_high = pixels_to_meters(px + 320, py + 200, zoom)
        mx_low, my_low = pixels_to_meters(px - 320, py - 200, zoom)
        lat_high, lon_high = meters_to_latlon(mx_high, my_high)
        lat_low, lon_low = meters_to_latlon(mx_low, my_low)
        boundings = str(lat_high) + "," + str(lon_high) + "," + str(lat_low) + "," + str(lon_low)
        url = '%sincidents?key=%s&inFormat=kvp&boundingBox=%s' % (BASE_URL, MAPQUEST_KEY, boundings)
        results = Get_JSON_response(url)
        places_list = []
        pin_string = ""
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
                image = BASE_URL + url
                search_string = lat + "," + lon
                google_map = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, GOOGLE_MAPS_KEY)
                if place['type'] == 1:
                    incident_type = "Construction"
                elif place['type'] == 2:
                    incident_type = "Event"
                elif place['type'] == 3:
                    incident_type = "Congestion / Flow"
                elif place['type'] == 4:
                    incident_type = "Incident / Accident"
                prop_list = {'name': place['shortDesc'],
                             'label': place['shortDesc'],
                             'label2': place['startTime'],
                             'description': place['fullDesc'],
                             'distance': str(place['distance']),
                             'delaytypical': str(place['delayFromTypical']),
                             'delayfreeflow': str(place['delayFromFreeFlow']),
                             "GoogleMap": google_map,
                             "venue_image": image,
                             "thumb": image,
                             "icon": place['iconURL'],
                             'date': place['startTime'],
                             'severity': str(place['severity']),
                             'type': incident_type,
                             "sortletter": chr(letter),
                             "lat": lat,
                             "lon": lon,
                             "index": str(count)}
                pin_string = pin_string + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(prop_list)
                count += 1
                letter += 1
                if count > MAX_LIMIT:
                    break
            fill_area = "&path=color:0x00000000|weight:5|fillcolor:0xFFFF0033|%s,%s|%s,%s|%s,%s|%s,%s" % (lat_high, lon_high, lat_high, lon_low, lat_low, lon_low, lat_low, lon_high)
            pin_string = pin_string + fill_area.replace("|", "%7C")
            return places_list, pin_string
        else:
            Notify("Error", "Could not fetch results")
            return [], ""
