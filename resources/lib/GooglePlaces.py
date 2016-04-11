# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import urllib

import xbmcgui

import Utils

from kodi65 import utils
from kodi65 import addon

GOOGLE_PLACES_KEY = 'AIzaSyCgfpm7hE_ufKMoiSUhoH75bRmQqV8b7P4'
BASE_URL = 'https://maps.googleapis.com/maps/api/place/'


class GooglePlaces():

    def __init__(self):
        pass

    def select_category(self):
        Categories = {"accounting": addon.LANG(32000),
                      "airport": addon.LANG(32035),
                      "amusement_park": addon.LANG(32036),
                      "aquarium": addon.LANG(32037),
                      "art_gallery": addon.LANG(32038),
                      "atm": addon.LANG(32039),
                      "bakery": addon.LANG(32040),
                      "bank": addon.LANG(32041),
                      "bar": addon.LANG(32042),
                      "beauty_salon": addon.LANG(32016),
                      "bicycle_store": addon.LANG(32017),
                      "book_store": addon.LANG(32018),
                      "bowling_alley": addon.LANG(32023),
                      "bus_station": addon.LANG(32033),
                      "cafe": addon.LANG(32043),
                      "campground": addon.LANG(32044),
                      "car_dealer": addon.LANG(32045),
                      "car_rental": addon.LANG(32046),
                      "car_repair": addon.LANG(32047),
                      "car_wash": addon.LANG(32048),
                      "casino": addon.LANG(32049),
                      "cemetery": addon.LANG(32050),
                      "church": addon.LANG(32051),
                      "city_hall": addon.LANG(32052),
                      "clothing_store": addon.LANG(32053),
                      "convenience_store": addon.LANG(32054),
                      "courthouse": addon.LANG(32055),
                      "dentist": addon.LANG(32056),
                      "department_store": addon.LANG(32057),
                      "doctor": addon.LANG(32058),
                      "electrician": addon.LANG(32059),
                      "electronics_store": addon.LANG(32060),
                      "embassy": addon.LANG(32061),
                      "establishment": addon.LANG(32062),
                      "finance": addon.LANG(29957),
                      "fire_station": addon.LANG(32063),
                      "florist": addon.LANG(32064),
                      "food": addon.LANG(32006),
                      "funeral_home": addon.LANG(32065),
                      "furniture_store": addon.LANG(32066),
                      "gas_station": addon.LANG(32067),
                      "general_contractor": addon.LANG(32068),
                      "grocery_or_supermarket": addon.LANG(32069),
                      "gym": addon.LANG(32070),
                      "hair_care": addon.LANG(32071),
                      "hardware_store": addon.LANG(32072),
                      "health": addon.LANG(32073),
                      "hindu_temple": addon.LANG(32074),
                      "home_goods_store": addon.LANG(32075),
                      "hospital": addon.LANG(32076),
                      "insurance_agency": addon.LANG(32077),
                      "jewelry_store": addon.LANG(32078),
                      "laundry": addon.LANG(32079),
                      "lawyer": addon.LANG(32080),
                      "library": addon.LANG(14022),
                      "liquor_store": addon.LANG(32081),
                      "local_government_office": addon.LANG(32082),
                      "locksmith": addon.LANG(32083),
                      "lodging": addon.LANG(32084),
                      "meal_delivery": addon.LANG(32085),
                      "meal_takeaway": addon.LANG(32086),
                      "mosque": addon.LANG(32087),
                      "movie_rental": addon.LANG(32088),
                      "movie_theater": addon.LANG(32089),
                      "moving_company": addon.LANG(32090),
                      "museum": addon.LANG(32091),
                      "night_club": addon.LANG(32092),
                      "painter": addon.LANG(32093),
                      "park": addon.LANG(32094),
                      "parking": addon.LANG(32095),
                      "pet_store": addon.LANG(32096),
                      "pharmacy": addon.LANG(32097),
                      "physiotherapist": addon.LANG(32098),
                      "place_of_worship": addon.LANG(32099),
                      "plumber": addon.LANG(32100),
                      "police": addon.LANG(32101),
                      "post_office": addon.LANG(32102),
                      "real_estate_agency": addon.LANG(32103),
                      "restaurant": addon.LANG(32104),
                      "roofing_contractor": addon.LANG(32105),
                      "rv_park": addon.LANG(32106),
                      "school": addon.LANG(32107),
                      "shoe_store": addon.LANG(32108),
                      "spa": addon.LANG(32109),
                      "stadium": addon.LANG(32110),
                      "storage": addon.LANG(154),
                      "store": addon.LANG(32111),
                      "subway_station": addon.LANG(32112),
                      "synagogue": addon.LANG(32113),
                      "taxi_stand": addon.LANG(32114),
                      "train_station": addon.LANG(32115),
                      "travel_agency": addon.LANG(32116),
                      "university": addon.LANG(32117),
                      "veterinary_care": addon.LANG(32118),
                      "zoo": addon.LANG(32119)
                      }
        modeselect = [addon.LANG(32120)]
        modeselect += [value for value in Categories.itervalues()]
        index = xbmcgui.Dialog().select(addon.LANG(32121), modeselect)
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
        letter = ord('A')
        if "meta" in results and results['meta']['code'] == 400:
            utils.log("LIMIT EXCEEDED")
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
            props = {'name': place['name'],
                     'label': place['name'],
                     'label2': " / ".join(place['types']),
                     'description': description,
                     "letter": chr(letter + count),
                     "thumb": photo,
                     "icon": place['icon'],
                     "lat": lat,
                     "lon": lon,
                     "rating": str(place['rating'] * 2.0) if "rating" in place else ""}
            places.append(props)
        return places


GP = GooglePlaces()
