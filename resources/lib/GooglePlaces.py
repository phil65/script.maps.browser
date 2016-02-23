import Utils
import xbmc
import xbmcgui
import xbmcaddon
import urllib

GOOGLE_PLACES_KEY = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
ADDON = xbmcaddon.Addon()
BASE_URL = 'https://maps.googleapis.com/maps/api/place/'


class GooglePlaces():

    def __init__(self):
        pass

    def select_category(self):
        Categories = {"accounting": ADDON.getLocalizedString(32000),
                      "airport": ADDON.getLocalizedString(32035),
                      "amusement_park": ADDON.getLocalizedString(32036),
                      "aquarium": ADDON.getLocalizedString(32037),
                      "art_gallery": ADDON.getLocalizedString(32038),
                      "atm": ADDON.getLocalizedString(32039),
                      "bakery": ADDON.getLocalizedString(32040),
                      "bank": ADDON.getLocalizedString(32041),
                      "bar": ADDON.getLocalizedString(32042),
                      "beauty_salon": ADDON.getLocalizedString(32016),
                      "bicycle_store": ADDON.getLocalizedString(32017),
                      "book_store": ADDON.getLocalizedString(32018),
                      "bowling_alley": ADDON.getLocalizedString(32023),
                      "bus_station": ADDON.getLocalizedString(32033),
                      "cafe": ADDON.getLocalizedString(32043),
                      "campground": ADDON.getLocalizedString(32044),
                      "car_dealer": ADDON.getLocalizedString(32045),
                      "car_rental": ADDON.getLocalizedString(32046),
                      "car_repair": ADDON.getLocalizedString(32047),
                      "car_wash": ADDON.getLocalizedString(32048),
                      "casino": ADDON.getLocalizedString(32049),
                      "cemetery": ADDON.getLocalizedString(32050),
                      "church": ADDON.getLocalizedString(32051),
                      "city_hall": ADDON.getLocalizedString(32052),
                      "clothing_store": ADDON.getLocalizedString(32053),
                      "convenience_store": ADDON.getLocalizedString(32054),
                      "courthouse": ADDON.getLocalizedString(32055),
                      "dentist": ADDON.getLocalizedString(32056),
                      "department_store": ADDON.getLocalizedString(32057),
                      "doctor": ADDON.getLocalizedString(32058),
                      "electrician": ADDON.getLocalizedString(32059),
                      "electronics_store": ADDON.getLocalizedString(32060),
                      "embassy": ADDON.getLocalizedString(32061),
                      "establishment": ADDON.getLocalizedString(32062),
                      "finance": xbmc.getLocalizedString(29957),
                      "fire_station": ADDON.getLocalizedString(32063),
                      "florist": ADDON.getLocalizedString(32064),
                      "food": ADDON.getLocalizedString(32006),
                      "funeral_home": ADDON.getLocalizedString(32065),
                      "furniture_store": ADDON.getLocalizedString(32066),
                      "gas_station": ADDON.getLocalizedString(32067),
                      "general_contractor": ADDON.getLocalizedString(32068),
                      "grocery_or_supermarket": ADDON.getLocalizedString(32069),
                      "gym": ADDON.getLocalizedString(32070),
                      "hair_care": ADDON.getLocalizedString(32071),
                      "hardware_store": ADDON.getLocalizedString(32072),
                      "health": ADDON.getLocalizedString(32073),
                      "hindu_temple": ADDON.getLocalizedString(32074),
                      "home_goods_store": ADDON.getLocalizedString(32075),
                      "hospital": ADDON.getLocalizedString(32076),
                      "insurance_agency": ADDON.getLocalizedString(32077),
                      "jewelry_store": ADDON.getLocalizedString(32078),
                      "laundry": ADDON.getLocalizedString(32079),
                      "lawyer": ADDON.getLocalizedString(32080),
                      "library": xbmc.getLocalizedString(14022),
                      "liquor_store": ADDON.getLocalizedString(32081),
                      "local_government_office": ADDON.getLocalizedString(32082),
                      "locksmith": ADDON.getLocalizedString(32083),
                      "lodging": ADDON.getLocalizedString(32084),
                      "meal_delivery": ADDON.getLocalizedString(32085),
                      "meal_takeaway": ADDON.getLocalizedString(32086),
                      "mosque": ADDON.getLocalizedString(32087),
                      "movie_rental": ADDON.getLocalizedString(32088),
                      "movie_theater": ADDON.getLocalizedString(32089),
                      "moving_company": ADDON.getLocalizedString(32090),
                      "museum": ADDON.getLocalizedString(32091),
                      "night_club": ADDON.getLocalizedString(32092),
                      "painter": ADDON.getLocalizedString(32093),
                      "park": ADDON.getLocalizedString(32094),
                      "parking": ADDON.getLocalizedString(32095),
                      "pet_store": ADDON.getLocalizedString(32096),
                      "pharmacy": ADDON.getLocalizedString(32097),
                      "physiotherapist": ADDON.getLocalizedString(32098),
                      "place_of_worship": ADDON.getLocalizedString(32099),
                      "plumber": ADDON.getLocalizedString(32100),
                      "police": ADDON.getLocalizedString(32101),
                      "post_office": ADDON.getLocalizedString(32102),
                      "real_estate_agency": ADDON.getLocalizedString(32103),
                      "restaurant": ADDON.getLocalizedString(32104),
                      "roofing_contractor": ADDON.getLocalizedString(32105),
                      "rv_park": ADDON.getLocalizedString(32106),
                      "school": ADDON.getLocalizedString(32107),
                      "shoe_store": ADDON.getLocalizedString(32108),
                      "spa": ADDON.getLocalizedString(32109),
                      "stadium": ADDON.getLocalizedString(32110),
                      "storage": xbmc.getLocalizedString(154),
                      "store": ADDON.getLocalizedString(32111),
                      "subway_station": ADDON.getLocalizedString(32112),
                      "synagogue": ADDON.getLocalizedString(32113),
                      "taxi_stand": ADDON.getLocalizedString(32114),
                      "train_station": ADDON.getLocalizedString(32115),
                      "travel_agency": ADDON.getLocalizedString(32116),
                      "university": ADDON.getLocalizedString(32117),
                      "veterinary_care": ADDON.getLocalizedString(32118),
                      "zoo": ADDON.getLocalizedString(32119)
                      }
        modeselect = [ADDON.getLocalizedString(32120)]
        modeselect += [value for value in Categories.iterkeys()]
        index = xbmcgui.Dialog().select(ADDON.getLocalizedString(32121), modeselect)
        if index > 0:
            return Categories.keys()[index - 1]
        elif index > -1:
            return ""
        else:
            return None

    def get_locations(self, lat, lon, radius, locationtype):
        params = {"key": GOOGLE_PLACES_KEY,
                  "radius": min(30000, radius),
                  "location": "%s,%s" % (lat, lon),
                  "types": locationtype}
        base_url = BASE_URL + 'nearbysearch/json?'
        results = Utils.get_JSON_response(base_url + urllib.urlencode(params))
        places = []
        pins = ""
        letter = ord('A')
        if "meta" in results and results['meta']['code'] == 400:
            Utils.log("LIMIT EXCEEDED")
            return "", []
        if "results" not in results:
            return "", []
        for count, place in enumerate(results['results']):
            try:
                params = {"maxwidth": 400,
                          "photoreference": place['photos'][0]['photo_reference'],
                          "key": GOOGLE_PLACES_KEY}
                photo = BASE_URL + 'photo?' + urllib.urlencode(params)
            except:
                photo = ""
            description = place['vicinity'] if "vicinity" in place else place.get('formatted_address', "")
            lat = str(place['geometry']['location']['lat'])
            lon = str(place['geometry']['location']['lng'])
            rating = str(place['rating'] * 2.0) if "rating" in place else ""
            props = {'name': place['name'],
                     'label': place['name'],
                     'label2': " / ".join(place['types']),
                     'description': description,
                     "letter": chr(letter),
                     "index": str(count),
                     "thumb": photo,
                     "icon": place['icon'],
                     "lat": lat,
                     "lon": lon,
                     "rating": rating,
                     "index": str(count)}
            pins += "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + lat + "," + lon
            places.append(props)
            letter += 1
        return pins, places
