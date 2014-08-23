import xbmc, os, sys, time, re, xbmcgui
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
googlemaps_key_normal = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
googlemaps_key_streetview = 'AIzaSyCo31ElCssn5GfH2eHXHABR3zu0XiALCc4'
foursquare_id = "OPLZAEBJAWPE5F4LW0QGHHSJDF0K3T5GVJAAICXUDHR11GPS"
foursquare_secret = "0PIG5HGE0LWD3Z5TDSE1JVDXGCVK4AJYHL50VYTJ2CFPVPAC"
            
def GetNearEvents(self,tag = False,festivalsonly = False, lat = "", lon = ""):
    if festivalsonly:
        festivalsonly = "1"
    else:
        festivalsonly = "0"
    url = 'method=geo.getevents&festivalsonly=%s&limit=40' % (festivalsonly)
    if tag:
        url = url + '&tag=%s' % (urllib.quote_plus(tag))  
    if lat:
        url = url + '&lat=%s&long=%s' % (lat,lon)  # &distance=60
    results = GetLastFMData(url)
    events = []
    self.log("starting HandleLastFMEventResult based on following JSON answer:")
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
                search_string = ""
            elif event['venue']['location']['street']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['location']['street']
            elif event['venue']['location']['city']:
                search_string = event['venue']['location']['city'] + " " + event['venue']['name']               
            else:
                search_string = event['venue']['name']
            googlemap = 'http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&maptype=roadmap&center=%s&zoom=13&markers=%s&size=640x640&key=%s' % (search_string, search_string, googlemaps_key_old)
            event = {'date': event['startDate'],
                     'name': event['venue']['name'],
                     'id': event['venue']['id'],
                     'street': event['venue']['location']['street'],
                     'eventname': event['title'],
                     'website': event['website'],
                     'description': cleanText(event['description']),
                    # 'description': event['description'], ticket missing
                 #    'city': event['venue']['location']['postalcode'] + " " + event['venue']['location']['city'],
                     'city': event['venue']['location']['city'],
                     'country': event['venue']['location']['country'],
                     'geolong': event['venue']['location']['geo:point']['geo:long'],
                     'geolat': event['venue']['location']['geo:point']['geo:lat'],
                     'artists': my_arts,
                     'googlemap': googlemap,
                     'artist_image': event['image'][-1]['#text'],
                     'venue_image': event['venue']['image'][-1]['#text'],
                     'headliner': event['artists']['headliner']  }
            events.append(event)
    else:
        self.log("Error when handling LastFM results")
          
def GetLastFMData(self, url = "", cache_days = 14):
    from base64 import b64encode
    filename = b64encode(url).replace("/","XXXX")
    path = Addon_Data_Path + "/" + filename + ".txt"
    self.log("trying to load "  + path)
    if xbmcvfs.exists(path) and ((time.time() - os.path.getmtime(path)) < (cache_days * 86400)):
        return read_from_file(path)
    else:
        url = 'http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&%s' % (lastfm_apikey, url)
        response = GetStringFromUrl(url)
        results = json.loads(response)
        save_to_file(results,filename,Addon_Data_Path)
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
        self.GoogleMapURL = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (self.type, self.search_string, self.zoom_level, self.search_string, size, googlemaps_key_normal)
        zoom = 120 - int(self.zoom_level) * 6
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
        location = results["results"][0]["geometry"]["location"]
        return (location["lat"], location["lng"])
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
        
def GetPlaces(self):
    url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.6f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (self.lat, self.lon, "test", foursquare_id, foursquare_secret)
    self.log(url)
    response = self.GetStringFromUrl(url)
    results = simplejson.loads(response)
    self.prettyprint(results)
    places_list = list()
    try:
        if results and 'meta' in results:
            if results['meta']['code'] == 200:
                for v in results['response']['venues']:
                    p = {'id': v['id'], 'name': v['name'], 'lat': v['location']['lat'], 'lng': v['location']['lng'], 'distance': v['location']['distance'], 'comments': v['stats']['tipCount'], 'visited': v['stats']['usersCount']}
                    if 'formattedAddress' in v['location']:
                        p['address'] = ', '.join(filter(None, v['location']['formattedAddress']))
                    if 'phone' in v['contact']:
                        p['phone'] = v['contact']['phone']
                    if 'twitter' in v['contact']:
                        p['phone'] = v['contact']['twitter']
                             # create a list item
                    item = xbmcgui.ListItem(v['name'])
                    item.setProperty("id", str(v['id']))
                    item.setProperty("id", str(v['id']))
                    places_list.append(("item['file']", item, False))
            elif results['meta']['code'] == 400:
                self.log("LIMIT EXCEEDED")
            else:
                self.log("ERROR")
        else:
            self.log("ERROR")
    except Exception,e:
        self.log(e)
        info['status'] = 'ERROR'
    return places_list