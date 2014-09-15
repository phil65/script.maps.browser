from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

googlemaps_key_places = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
max_limit = 25
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'


class GooglePlaces():

    def __init__(self):
        pass

    def GetGooglePlacesList(self, locationtype):
        location = str(self.lat) + "," + str(self.lon)
        base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?radius=500&key=%s' % (googlemaps_key_places)
        url = '&location=%s&types=%s' % (location, locationtype)
        results = Get_JSON_response(base_url, url)
        places_list = list()
        PinString = ""
        letter = ord('A')
        count = 0
        if "results" in results:
            for v in results['results']:
                item = xbmcgui.ListItem(v['name'])
                try:
                    photo_ref = v['photos'][0]['photo_reference']
                    photo = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s' % (photo_ref, googlemaps_key_places)
                except:
                    photo = ""
                typestring = ""
                typestring = " / ".join(v['types'])
                item.setArt({'thumb': photo})
                item.setArt({'icon': v['icon']})
                item.setLabel(v['name'])
                item.setProperty('name', v['name'])
                item.setProperty('description', v['vicinity'])
                item.setLabel2(typestring)
                item.setProperty("sortletter", chr(letter))
                item.setProperty("index", str(count))
                lat = str(v['geometry']['location']['lat'])
                lon = str(v['geometry']['location']['lng'])
                item.setProperty("lat", lat)
                item.setProperty("lon", lon)
                item.setProperty("index", str(count))
                if "rating" in v:
                    rating = str(v['rating'] * 2.0)
                    item.setProperty("rating", rating)
                PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(item)
                count += 1
                letter += 1
                if count > max_limit:
                    break
          #  difference_lat = results['response']['suggestedBounds']['ne']['lat'] - results['response']['suggestedBounds']['sw']['lat']
           # difference_lon = results['response']['suggestedBounds']['ne']['lng'] - results['response']['suggestedBounds']['sw']['lng']
           # log(difference_lat)
        elif results['meta']['code'] == 400:
            log("LIMIT EXCEEDED")
        else:
            log("ERROR")
        return PinString, places_list
