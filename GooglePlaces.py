from Utils import *
import xbmcgui

GOOGLE_PLACES_KEY = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
ADDON = xbmcaddon.Addon()


class GooglePlaces():

    def __init__(self):
        pass

    def SelectCategory(self):
        Categories = {"accounting": ADDON.getLocalizedString(32005),
                      "airport": ADDON.getLocalizedString(32006),
                      "amusement_park": ADDON.getLocalizedString(32007),
                      "aquarium": ADDON.getLocalizedString(32008),
                      "art_gallery": ADDON.getLocalizedString(32009),
                      "atm": ADDON.getLocalizedString(32010),
                      "bakery": ADDON.getLocalizedString(32011),
                      "bank": ADDON.getLocalizedString(32012),
                      "bar": ADDON.getLocalizedString(32013),
                      "beauty_salon": ADDON.getLocalizedString(32014),
                      "bicycle_store": ADDON.getLocalizedString(32015),
                      "book_store": ADDON.getLocalizedString(32015),
                      "bowling_alley": ADDON.getLocalizedString(32015),
                      "bus_station": ADDON.getLocalizedString(32015),
                      "cafe": ADDON.getLocalizedString(32015),
                      "campground": ADDON.getLocalizedString(32015),
                      "car_dealer": ADDON.getLocalizedString(32015),
                      "car_rental": ADDON.getLocalizedString(32015),
                      "car_repair": ADDON.getLocalizedString(32015),
                      "car_wash": ADDON.getLocalizedString(32015),
                      "casino": ADDON.getLocalizedString(32015),
                      "cemetery": ADDON.getLocalizedString(32015),
                      "church": ADDON.getLocalizedString(32015),
                      "city_hall": ADDON.getLocalizedString(32015),
                      "clothing_store": ADDON.getLocalizedString(32015),
                      "convenience_store": ADDON.getLocalizedString(32015),
                      "courthouse": ADDON.getLocalizedString(32015),
                      "dentist": ADDON.getLocalizedString(32015),
                      "department_store": ADDON.getLocalizedString(32015),
                      "doctor": ADDON.getLocalizedString(32015),
                      "electrician": ADDON.getLocalizedString(32015),
                      "electronics_store": ADDON.getLocalizedString(32015),
                      "embassy": ADDON.getLocalizedString(32015),
                      "establishment": ADDON.getLocalizedString(32015),
                      "finance": ADDON.getLocalizedString(32015),
                      "fire_station": ADDON.getLocalizedString(32015),
                      "florist": ADDON.getLocalizedString(32015),
                      "food": ADDON.getLocalizedString(32015),
                      "funeral_home": ADDON.getLocalizedString(32015),
                      "furniture_store": ADDON.getLocalizedString(32015),
                      "gas_station": ADDON.getLocalizedString(32015),
                      "general_contractor": ADDON.getLocalizedString(32015),
                      "grocery_or_supermarket": ADDON.getLocalizedString(32015),
                      "gym": ADDON.getLocalizedString(32015),
                      "hair_care": ADDON.getLocalizedString(32015),
                      "hardware_store": ADDON.getLocalizedString(32015),
                      "health": ADDON.getLocalizedString(32015),
                      "hindu_temple": ADDON.getLocalizedString(32015),
                      "home_goods_store": ADDON.getLocalizedString(32015),
                      "hospital": ADDON.getLocalizedString(32015),
                      "insurance_agency": ADDON.getLocalizedString(32015),
                      "jewelry_store": ADDON.getLocalizedString(32015),
                      "laundry": ADDON.getLocalizedString(32015),
                      "lawyer": ADDON.getLocalizedString(32015),
                      "library": ADDON.getLocalizedString(32015),
                      "liquor_store": ADDON.getLocalizedString(32015),
                      "local_government_office": ADDON.getLocalizedString(32015),
                      "locksmith": ADDON.getLocalizedString(32015),
                      "lodging": ADDON.getLocalizedString(32015),
                      "meal_delivery": ADDON.getLocalizedString(32015),
                      "meal_takeaway": ADDON.getLocalizedString(32015),
                      "mosque": ADDON.getLocalizedString(32015),
                      "movie_rental": ADDON.getLocalizedString(32015),
                      "movie_theater": ADDON.getLocalizedString(32015),
                      "moving_company": ADDON.getLocalizedString(32015),
                      "museum": ADDON.getLocalizedString(32015),
                      "night_club": ADDON.getLocalizedString(32015),
                      "painter": ADDON.getLocalizedString(32015),
                      "park": ADDON.getLocalizedString(32015),
                      "parking": ADDON.getLocalizedString(32015),
                      "pet_store": ADDON.getLocalizedString(32015),
                      "pharmacy": ADDON.getLocalizedString(32015),
                      "physiotherapist": ADDON.getLocalizedString(32015),
                      "place_of_worship": ADDON.getLocalizedString(32015),
                      "plumber": ADDON.getLocalizedString(32015),
                      "police": ADDON.getLocalizedString(32015),
                      "post_office": ADDON.getLocalizedString(32015),
                      "real_estate_agency": ADDON.getLocalizedString(32015),
                      "restaurant": ADDON.getLocalizedString(32015),
                      "roofing_contractor": ADDON.getLocalizedString(32015),
                      "rv_park": ADDON.getLocalizedString(32015),
                      "school": ADDON.getLocalizedString(32015),
                      "shoe_store": ADDON.getLocalizedString(32015),
                      "spa": ADDON.getLocalizedString(32015),
                      "stadium": ADDON.getLocalizedString(32015),
                      "storage": ADDON.getLocalizedString(32015),
                      "store": ADDON.getLocalizedString(32015),
                      "subway_station": ADDON.getLocalizedString(32015),
                      "synagogue": ADDON.getLocalizedString(32015),
                      "taxi_stand": ADDON.getLocalizedString(32015),
                      "train_station": ADDON.getLocalizedString(32015),
                      "travel_agency": ADDON.getLocalizedString(32015),
                      "university": ADDON.getLocalizedString(32015),
                      "veterinary_care": ADDON.getLocalizedString(32015),
                      "zoo": ADDON.getLocalizedString(32015)
                      }
        modeselect = ["All Sections"]
        for value in Categories.iterkeys():
            modeselect.append(value)
        dialog = xbmcgui.Dialog()
        index = dialog.select("Choose Section", modeselect)
        if index > 0:
            return Categories.keys()[index - 1]
        elif index > -1:
            return ""
        else:
            return None

    def GetGooglePlacesList(self, lat, lon, radius, locationtype):
        location = str(lat) + "," + str(lon)
        base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=%s' % (GOOGLE_PLACES_KEY)
        url = '&radius=%i&location=%s&types=%s' % (radius, location, locationtype)
        results = Get_JSON_response(base_url + url)
        log(url)
        places_list = []
        PinString = ""
        letter = ord('A')
        count = 0
        if "results" in results:
            for place in results['results']:
                try:
                    photo_ref = place['photos'][0]['photo_reference']
                    photo = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=%s' % (photo_ref, GOOGLE_PLACES_KEY)
                except:
                    photo = ""
                if "vicinity" in place:
                    description = place['vicinity']
                else:
                    description = place.get('formatted_address', "")
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
                PinString = PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
                places_list.append(prop_list)
                count += 1
                letter += 1
        elif results['meta']['code'] == 400:
            log("LIMIT EXCEEDED")
        else:
            log("ERROR")
        return PinString, places_list
