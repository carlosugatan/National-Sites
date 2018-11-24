## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import json
import requests
from datetime import datetime
from collections import OrderedDict
import plotly

######################
#      SCRAPING      #
######################

def create_id(site, topic):
    return "{}_{}_{}.json".format(site, topic, str(datetime.now()).replace(' ', ''))

def create_id_sites(urls):
    return "{}.json".format(urls, str(datetime.now()).replace(' ', ''))

def process(response):
    name_lst = []
    url_lst = []
    site_lst = []

    ## use the `response` to create a BeautifulSoup object
    soup = BeautifulSoup(response, 'html.parser')

    national_site_container = soup.find_all('div', class_ = 'col-md-9 col-sm-9 col-xs-12 table-cell list_left')

    for container in national_site_container:

        # Name
        name = container.h3.text
        name_lst.append(name)
        # print(name)

        # Type
        type = container.h2.text
        # print(type)

        # Description
        process.desc = container.p.text
        # print(desc)

        # URL
        process.url = "https://www.nps.gov"+container.h3.a.get('href')+"index.htm"
        url_lst.append(process.url)
        # print(url)

        for urls in url_lst:
            cache_file = "nps_address.json"
            cache_address = Cache(cache_file)

            UID = create_id_sites(urls)
            response2 = cache_address.get(UID)
            if response2 == None:
                response2 = requests.get(urls).text
                cache_address.set(UID, response2, 1)
            # get_address(response2)

            soup2 = BeautifulSoup(response2, "html.parser")
            try:
                # ## Address Street
                address_street_fndr = soup2.find(attrs={"itemprop": "streetAddress"})
                process.address_street = address_street_fndr.text
                # print(process.address_street)

                ## Address City
                address_city_fndr = soup2.find(attrs={"itemprop": "addressLocality"})
                process.address_city = address_city_fndr.text
                # print(process.address_city)

                # ## Address State
                address_state_fndr = soup2.find(attrs={"itemprop": "addressRegion"})
                process.address_state = address_state_fndr.text
                # print(process.address_state)

                # ## Address ZIP
                address_zip_fndr = soup2.find(attrs={"itemprop": "postalCode"})
                process.address_zip = address_zip_fndr.text
                # print(process.address_zip)
            except:
                # print("No address found for {}".format(urls))
                process.address_street = "None"
                process.address_city = "None"
                process.address_state = "None"
                process.address_zip = "None"

        national_sites = NationalSite(type, name)
        site_lst.append(national_sites)
        # print(national_sites)
    return site_lst


######################
#  GOOGLE PLACES API #
######################

CACHE_FILE1 = "google_places.json"
CACHE_FILE2 = "google_coordinates.json"
c = Cache(CACHE_FILE1)
c2 = Cache(CACHE_FILE2)

def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    # HTTPS://MAPS.GOOGLEAPIS.COM/MAPS/API/PLACE/NEARBYSEARCH/JSON?LOCATION=44.778410, -117.827940&RADIUS=10000
    alphabetized_keys = OrderedDict(params_d)
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}={}".format(k, params_d[k]))
    return baseurl + "&".join(res)

def google_coordinates(input, inputtype="textquery", fields="formatted_address,geometry"):
    # gets coordinates
    baseurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
    params_diction = OrderedDict({})
    params_diction["input"] = input
    params_diction["inputtype"] = inputtype
    params_diction["fields"] = fields
    params_diction["key"] = google_places_key
    unique_rep = params_unique_combination(baseurl, params_diction,private_keys=["key"])
    # print(unique_rep)
    data = c2.get(unique_rep)
    if data:
        with open ("google_coordinates.json", 'r') as f:
            key_dict = unique_rep.upper()
            coordinates = json.load(f)
            lng = str(coordinates[key_dict]["values"]["candidates"][0]["geometry"]["location"]["lng"])
            lat = str(coordinates[key_dict]["values"]["candidates"][0]["geometry"]["location"]["lat"])
            google_coordinates.location = lat+","+lng
            print(google_coordinates.location)
        # print("Data in cache")
        return google_coordinates.location
    else:
        resp = requests.get(baseurl, params=params_diction)
        obj = json.loads(resp.text)
        c2.set(unique_rep, obj, 10)
        return obj

def google_nearby_places(location, radius=10000):
    nearby_places_lst = []
    # gets nearby location with default radius of 10km
    baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params_diction = OrderedDict({})
    params_diction["location"] = location
    params_diction["radius"] = radius
    params_diction["key"] = google_places_key
    unique_rep = params_unique_combination(baseurl, params_diction,private_keys=["key"])
    # print(unique_rep)
    data = c.get(unique_rep)
    if data:
        # print("Data in cache")
        with open ("google_places.json", 'r') as f:
            key_dict = unique_rep.upper()
            nearbyplaces = json.load(f)
            for i in range(len(nearbyplaces[key_dict]["values"]["results"])):
                nearby_places_lst.append(nearbyplaces[key_dict]["values"]["results"][i]["name"])
            print(nearby_places_lst)
        return data
    else:
        resp = requests.get(baseurl, params=params_diction)
        obj = json.loads(resp.text)
        c.set(unique_rep, obj, 10)
        return obj

# restaurant = google_coordinates("Sleeping Bear Dunes National Lakeshore")
# restaurant = google_nearby_places(google_coordinates.location)
# restaurant = google_nearby_places("-33.8599358,151.2090295")


######################
#   NATIONAL SITES   #
######################

class NationalSite():
    def __init__(self, type, name):
    # def __init__(self, name):
        self.type = type
        self.name = name
        self.description = process.desc
        self.url = process.url

        self.address_street = process.address_street
        self.address_city = process.address_city
        self.address_state = process.address_state
        self.address_zip = process.address_zip

    def __str__(self):
        return "{} ({}): {} {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state,self.address_zip)
        # return "{} ({}) {}".format(self.name, self.type, self.address_city)
        # return "{} ({})".format(self.name, self.type)

    def __repr__(self):
        return "{} {}".format(self.name, self.type)

class NearbyPlace():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "{}".format(self.name)

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    return process(response) # returns NationalSites instances of that state
    # print(name_lst)
    # return process(response)
    # return []


## Must return the list of NearbyPlaces for the specific NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places(national_site):
    google_coordinates(national_site)
    # google_nearby_places(google_coordinates.location)
    # return []

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    national_sites_list = process(response)
    for site in national_sites_list:
        try:
            full_site_name = site.name + " " + site.type
            site_coord = google_coordinates(full_site_name)
            print(site_coord)
        except:
            national_sites_list.remove(site)
            print("Coordinates not found")


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    pass


###################
#     CONFIG      #
###################
state_abbr = input("Please enter state abbr: ").lower()
cache_file = "nps.json"
site="nps.gov"
topic="National Sites"
cache = Cache(cache_file)
# base = "https://www.nps.gov/state/mi/index.htm"
base_org = "https://www.nps.gov/state/%%/index.htm"
base = base_org.replace('%%', state_abbr)

######################
#    RUN PROGRAM     #
######################
UID = create_id(site, topic)
response = cache.get(UID)
if response == None:
    response = requests.get(base).text
    cache.set(UID, response, 1)
process(response)


## TESTING GET SITES FOR STATE
# xy = get_sites_for_state(state_abbr)
# print(xy)


## TESTING NATIONAL SITES CLASS
# national_sites = NationalSite("National Lakeshore", "Sleeping Bear Dunes")
# print(national_sites.type)


## TESTING GET NEARBY PLACES
# z = get_nearby_places(NationalSite("National Monument", "Fort Stanwix"))
# print(z)

plot_sites_for_state(state_abbr)


## THIS IS JUNK BUT I'LL KEEP IT HERE
# with open ("nps.json", 'r') as f2:
#     nps_json = json.load(f2)
#     soup = BeautifulSoup(response, 'html.parser')
#     national_site_container = soup.find_all('div', class_ = 'col-md-9 col-sm-9 col-xs-12 table-cell list_left')
#
#     for container in national_site_container:
#
#         # Name
#         name = container.h3.text
#         print(name)

# with open ("nps_address.json", 'r') as f3:
#     nps_address_json = json.load(f3)
#
#     soup2 = BeautifulSoup(response2, "html.parser")
#     ## Address Street
#     address_street_fndr = soup2.find(attrs={"itemprop": "streetAddress"})
#     address_street = address_street_fndr.text
#     print(address_street)

    # print(nps_json)
    # lng = str(coordinates[key_dict]["values"]["candidates"][0]["geometry"]["location"]["lng"])
    # lat = str(coordinates[key_dict]["values"]["candidates"][0]["geometry"]["location"]["lat"])
    # google_coordinates.location = lng+","+lat
