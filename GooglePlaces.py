from Utils import *
import xbmcgui
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

googlemaps_key_places = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString


class GooglePlaces():

    def __init__(self):
        pass

    def SelectCategory(self):
        Categories = {"accounting": __language__(34005),
                      "airport": __language__(34006),
                      "amusement_park": __language__(34007),
                      "aquarium": __language__(34008),
                      "art_gallery": __language__(34009),
                      "atm": __language__(34010),
                      "bakery": __language__(34011),
                      "bank": __language__(34012),
                      "bar": __language__(34013),
                      "beauty_salon": __language__(34014),
                      "bicycle_store": __language__(34015),
                      "book_store": __language__(34015),
                      "bowling_alley": __language__(34015),
                      "bus_station": __language__(34015),
                      "cafe": __language__(34015),
                      "campground": __language__(34015),
                      "car_dealer": __language__(34015),
                      "car_rental": __language__(34015),
                      "car_repair": __language__(34015),
                      "car_wash": __language__(34015),
                      "casino": __language__(34015),
                      "cemetery": __language__(34015),
                      "church": __language__(34015),
                      "city_hall": __language__(34015),
                      "clothing_store": __language__(34015),
                      "convenience_store": __language__(34015),
                      "courthouse": __language__(34015),
                      "dentist": __language__(34015),
                      "department_store": __language__(34015),
                      "doctor": __language__(34015),
                      "electrician": __language__(34015),
                      "electronics_store": __language__(34015),
                      "embassy": __language__(34015),
                      "establishment": __language__(34015),
                      "finance": __language__(34015),
                      "fire_station": __language__(34015),
                      "florist": __language__(34015),
                      "food": __language__(34015),
                      "funeral_home": __language__(34015),
                      "furniture_store": __language__(34015),
                      "gas_station": __language__(34015),
                      "general_contractor": __language__(34015),
                      "grocery_or_supermarket": __language__(34015),
                      "gym": __language__(34015),
                      "hair_care": __language__(34015),
                      "hardware_store": __language__(34015),
                      "health": __language__(34015),
                      "hindu_temple": __language__(34015),
                      "home_goods_store": __language__(34015),
                      "hospital": __language__(34015),
                      "insurance_agency": __language__(34015),
                      "jewelry_store": __language__(34015),
                      "laundry": __language__(34015),
                      "lawyer": __language__(34015),
                      "library": __language__(34015),
                      "liquor_store": __language__(34015),
                      "local_government_office": __language__(34015),
                      "locksmith": __language__(34015),
                      "lodging": __language__(34015),
                      "meal_delivery": __language__(34015),
                      "meal_takeaway": __language__(34015),
                      "mosque": __language__(34015),
                      "movie_rental": __language__(34015),
                      "movie_theater": __language__(34015),
                      "moving_company": __language__(34015),
                      "museum": __language__(34015),
                      "night_club": __language__(34015),
                      "painter": __language__(34015),
                      "park": __language__(34015),
                      "parking": __language__(34015),
                      "pet_store": __language__(34015),
                      "pharmacy": __language__(34015),
                      "physiotherapist": __language__(34015),
                      "place_of_worship": __language__(34015),
                      "plumber": __language__(34015),
                      "police": __language__(34015),
                      "post_office": __language__(34015),
                      "real_estate_agency": __language__(34015),
                      "restaurant": __language__(34015),
                      "roofing_contractor": __language__(34015),
                      "rv_park": __language__(34015),
                      "school": __language__(34015),
                      "shoe_store": __language__(34015),
                      "spa": __language__(34015),
                      "stadium": __language__(34015),
                      "storage": __language__(34015),
                      "store": __language__(34015),
                      "subway_station": __language__(34015),
                      "synagogue": __language__(34015),
                      "taxi_stand": __language__(34015),
                      "train_station": __language__(34015),
                      "travel_agency": __language__(34015),
                      "university": __language__(34015),
                      "veterinary_care": __language__(34015),
                      "zoo": __language__(34015)
                      }
        modeselect = []
        modeselect.append("All Sections")
        for value in Categories.iterkeys():
            modeselect.append(value)
        categorydialog = xbmcgui.Dialog()
        provider_index = categorydialog.select("Choose Section", modeselect)
        if provider_index > 0:
            return Categories.keys()[provider_index - 1]
        elif provider_index > -1:
            return ""
        else:
            return None

    def GetGooglePlacesList(self, lat, lon, radius, locationtype):
        location = str(lat) + "," + str(lon)
        base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s' % (googlemaps_key_places)
        url = '&radius=%i&location=%s&types=%s' % (radius, location, locationtype)
        results = Get_JSON_response(base_url, url)
        log(url)
        places_list = list()
        PinString = ""
        letter = ord('A')
        count = 0
        if "results" in results:
            for place in results['results']:
                try:
                    photo_ref = place['photos'][0]['photo_reference']
                    photo = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s' % (photo_ref, googlemaps_key_places)
                except:
                    photo = ""
       #         prettyprint(place)
                if "vicinity" in place:
                    description = place['vicinity']
                else:
                    description = place.get('formatted_address', "")
                typestring = ""
                typestring = " / ".join(place['types'])
                lat = str(place['geometry']['location']['lat'])
                lon = str(place['geometry']['location']['lng'])
                rating = ""
                if "rating" in place:
                    rating = str(place['rating'] * 2.0)
                prop_list = {'name': place['name'],
                             'label': place['name'],
                             'label2': typestring,
                             'description': description,
                             "sortletter": chr(letter),
                             "index": str(count),
                             "thumb": photo,
                             "icon": place['icon'],
                             "lat": lat,
                             "lon": lon,
                             "rating": rating,
                             "index": str(count)}
                item = CreateListItem(prop_list)
                PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(item)
                count += 1
                letter += 1
          #  difference_lat = results['response']['suggestedBounds']['ne']['lat'] - results['response']['suggestedBounds']['sw']['lat']
           # difference_lon = results['response']['suggestedBounds']['ne']['lng'] - results['response']['suggestedBounds']['sw']['lng']
           # log(difference_lat)
        elif results['meta']['code'] == 400:
            log("LIMIT EXCEEDED")
        else:
            log("ERROR")
        return PinString, places_list
