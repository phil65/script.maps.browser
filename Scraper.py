import xbmc, os, sys, time, re, xbmcgui,xbmcaddon, xbmcvfs,urllib
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__language__     = __addon__.getLocalizedString
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % __addonid__ ).decode("utf-8") )    
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
googlemaps_key_streetview = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'
foursquare_id = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
foursquare_secret = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
lastfm_apikey = '6c14e451cd2d480d503374ff8c8f4e2b'
max_limit = 25

            
def GetNearEvents(self,tag = False,festivalsonly = False):
    self.PinString = ""
    letter = ord('A')
    count = 0
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
    if tag:
        url = url + '&tag=%s' % (urllib.quote_plus(tag))  
    if self.lat:
        url = url + '&lat=%s&long=%s' % (self.lat,self.lon)  # &distance=60
    results = GetLastFMData(self,url)
    events_list = list()
    if "events" in results and results['events'].get("event"):
        for event in results['events']['event']:
            artists = event['artists']['artist']
            if isinstance(artists, list):
                my_arts = ' / '.join(artists)
            else:
                my_arts = artists
            lat = ""
            lon = ""               
            if event['venue']['location']['geo:point']['geo:long']:
                lon = event['venue']['location']['geo:point']['geo:long']
                lat = event['venue']['location']['geo:point']['geo:lat']
                search_string = lat + "," + lon
            elif event['venue']['location']['street']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['location']['street']
            elif event['venue']['location']['city']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['name']               
            else:
                search_string = event['venue']['name']
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_normal)
            item = xbmcgui.ListItem(event['venue']['name'])
            item.setProperty("date", event['startDate'])
            item.setProperty("name", event['venue']['name'])
            item.setProperty("id", event['startDate'])
            item.setProperty("street", event['venue']['location']['street'])
            item.setProperty("eventname", event['title'])
            item.setProperty("website", event['website'])
            item.setProperty("description", self.cleanText(event['description']))
            item.setProperty("city", event['venue']['location']['city'])
            item.setProperty("country", event['venue']['location']['country'])
            item.setProperty("lon", event['venue']['location']['geo:point']['geo:long'])
            item.setProperty("lat", event['venue']['location']['geo:point']['geo:lat'])
            item.setProperty("artists", my_arts)
            item.setProperty("sortletter", chr(letter))
            item.setProperty("googlemap", googlemap)
            item.setProperty("artist_image", event['image'][-1]['#text'])
            item.setProperty("venue_image", event['venue']['image'][-1]['#text'])
            item.setProperty("headliner", event['artists']['headliner'])
            item.setArt({'thumb': event['venue']['image'][-1]['#text']})
            item.setLabel(event['venue']['name'])
            item.setLabel2(event['startDate'])
            events_list.append(item)
            self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + str(event['venue']['location']['geo:point']['geo:lat']) + "," + str(event['venue']['location']['geo:point']['geo:long'])
            count += 1
            letter += 1
            if count > max_limit:
                break
    else:
        self.log("Error when handling LastFM results")
    return events_list
          
def GetLastFMData(self, url = "", cache_days = 14):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return self.read_from_file(path)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&%s' % (lastfm_apikey, url)
        response = self.GetStringFromUrl(url)
        results = simplejson.loads(response)
        self.save_to_file(results,filename,Addon_Data_Path)
        return results
        
def GetGoogleMapURLs(self):
    try:
        if not self.type:
            self.type="roadmap"
        if self.aspect == "square":
            size = "640x640"
        else:
            size = "640x400"
        if self.lat and self.lon:
            self.search_string = str(self.lat) + "," + str(self.lon)
        else:
            self.search_string = urllib.quote_plus(self.search_string.replace('"',''))
        base_url='http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&'
        self.GoogleMapURL = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (self.type, self.search_string, self.zoom_level, self.search_string, size, googlemaps_key_normal) + self.PinString
        zoom = 120 - int(self.zoom_level_streetview) * 6
        base_url='http://maps.googleapis.com/maps/api/streetview?&sensor=false&'
        self.GoogleStreetViewURL = base_url + 'location=%s&size=%s&fov=%s&key=%s&heading=%s' % (self.search_string, size, str(zoom), googlemaps_key_streetview, str(self.direction))        
        self.SetProperties()
    except Exception,e:
        self.log(e)
        
# def GetBingMap(self):
   # # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s?mapSize=800,600&key=%s' % (urllib.quote(self.search_string),bing_key)
    # url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/5?key=%s' % (self.lat,self.lon, bing_key)
   ##         'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%.6f,%.6f/%i?fmt=%s&key=%s' % (self.lat, self.lon, self.zoom_level, self._format, bing_key)
    # self.log(url)
    # return url
                          
def GetGeoCodes(self, search_string):
    try:
        search_string = urllib.quote_plus(search_string)
        url = 'https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&address=%s' % (search_string)
        self.log("Google Geocodes Search:" + url)
        response = self.GetStringFromUrl(url)
        results = simplejson.loads(response)
        self.prettyprint(results)
        self.log(len(results["results"]))
        for item in results["results"]:
            pass
        first_hit = results["results"][0]["geometry"]["location"]
        return (first_hit["lat"], first_hit["lng"])
    except Exception,e:
        self.log(e)
        return ("","")
        
def GetLocationCoordinates(self):
    try:
        url = 'http://www.telize.com/geoip'
        response = self.GetStringFromUrl(url)
        results = simplejson.loads(response)
        self.lat = results["latitude"]
        self.lon = results["longitude"]
    except Exception,e:
        self.log(e)
        
def GetPlacesList(self):
    url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, foursquare_id, foursquare_secret)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
   # url = 'https://api.foursquare.com/v2/venues/explore?ll=%.8f,%.8f&section=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "topPicks", foursquare_id, foursquare_secret)
    self.log(url)
    response = self.GetStringFromUrl(url)
    results = simplejson.loads(response)
 #   self.prettyprint(results)
    places_list = list()
    self.PinString = ""
    letter = ord('A')
    count = 0
    if True:
        if results and 'meta' in results:
            if results['meta']['code'] == 200:
                for v in results['response']['venues']:
                    p = {'id': v['id'], 'name': v['name'], 'distance': v['location']['distance'], 'comments': v['stats']['tipCount'], 'visited': v['stats']['usersCount']}
                    if 'formattedAddress' in v['location']:
                        p['address'] = "aa"
                    if 'phone' in v['contact']:
                        p['phone'] = v['contact']['phone']
                    if 'twitter' in v['contact']:
                        p['phone'] = v['contact']['twitter']
                             # create a list item
                    item = xbmcgui.ListItem(v['name'])
                    item.setProperty("id", str(v['id']))
                    item.setProperty("lat", str(v['location']['lat']))
                    item.setProperty("lon", str(v['location']['lng']))
                    self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + str(v['location']['lat']) + "," + str(v['location']['lng'])
                    try: 
                        icon = v['categories'][0]['icon']['prefix'] + "88" +  v['categories'][0]['icon']['suffix']
#                        if count < 12:
                   #     self.PinString = self.PinString + "&markers=icon:" + v['categories'][0]['icon']['prefix'] + "64" +  v['categories'][0]['icon']['suffix'] + "|" + str(v['location']['lat']) + "," + str(v['location']['lng'])
                    #    self.PinString = self.PinString + "&markers="+ str(v['location']['lat']) + "," + str(v['location']['lng'])
                    #
                    except Exception, e:
                        icon = ""
                        self.log("Error: Exception in GetPlacesList with message:")
                        self.log(e)
                    item.setArt({'thumb': icon})
                    item.setLabel(v['name'])
                    item.setLabel2(v['name'])
                    item.setProperty("name", v['name'])
                    item.setProperty("sortletter", chr(letter))
                    item.setProperty("eventname", ', '.join(filter(None, v['location']['formattedAddress'])))
                    item.setProperty("Venue_Image", icon)
                    item.setProperty("GoogleMap", icon)
                    places_list.append(item)
                    count += 1
                    letter += 1
                    if count > max_limit:
                        break
            elif results['meta']['code'] == 400:
                self.log("LIMIT EXCEEDED")
            else:
                self.log("ERROR")
        else:
            self.log("ERROR")
    else:
        self.log("ERROR")
    return places_list
    
def GetPlacesListExplore(self,type):
   # url = 'https://api.foursquare.com/v2/venues/search?ll=%.8f,%.8f&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, foursquare_id, foursquare_secret)
  #  url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.8f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "Food", foursquare_id, foursquare_secret)
    url = 'https://api.foursquare.com/v2/venues/explore?ll=%.8f,%.8f&section=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, type, foursquare_id, foursquare_secret)
    self.log(url)
    response = self.GetStringFromUrl(url)
    results = simplejson.loads(response)
  #  self.prettyprint(results)
    places_list = list()
    self.PinString = ""
    letter = ord('A')
    count = 0
    if results and 'meta' in results:
        if results['meta']['code'] == 200:
            for v in results['response']['groups'][0]['items']:
                if True:
                    item = xbmcgui.ListItem(v['venue']['name'])
                    icon = v['venue']['categories'][0]['icon']['prefix'] + "88" +  v['venue']['categories'][0]['icon']['suffix']
                    item.setArt({'thumb': icon})
                    item.setLabel(v['venue']['name'])
                    item.setProperty('name',v['venue']['name'])
                    item.setLabel2(v['venue']['categories'][0]['name'])
                    item.setProperty("sortletter", chr(letter))
                    item.setProperty("Venue_Image", icon)
                    item.setProperty("lat", str(v['venue']['location']['lat']))
                    item.setProperty("lon", str(v['venue']['location']['lng']))
                    self.PinString = self.PinString + "&markers=color:blue%7Clabel:" + chr(letter) + "%7C" + str(v['venue']['location']['lat']) + "," + str(v['venue']['location']['lng'])
                    places_list.append(item)
                    count += 1
                    letter += 1
                    if count > max_limit:
                        break
            difference_lat = results['response']['suggestedBounds']['ne']['lat'] - results['response']['suggestedBounds']['sw']['lat']
            difference_lon = results['response']['suggestedBounds']['ne']['lng'] - results['response']['suggestedBounds']['sw']['lng']
            self.log(difference_lat)
        elif results['meta']['code'] == 400:
            self.log("LIMIT EXCEEDED")
        else:
            self.log("ERROR")
    else:
        self.log("ERROR")
    return places_list