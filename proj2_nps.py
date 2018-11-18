## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import requests
from datetime import datetime

##############
# SETTING UP #
##############

def create_id(site, topic):
    return "{}_{}_{}.json".format(site, topic, str(datetime.now()).replace(' ', ''))

def process(response):
    name_lst = []
    url_lst = []

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
            site="nps.gov"
            topic="National Sites Address"
            cache_address = Cache(cache_file)

            UID = create_id(site, topic)
            response2 = cache_address.get(UID)
            if response2 == None:
                response2 = requests.get(urls).text
                cache_address.set(UID, response2, 1)
            # get_address(response2)

            soup2 = BeautifulSoup(response2, "html.parser")

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

            national_sites = NationalSite(type, name)
        print(national_sites)
                # name_lst.append(name)
    # return name_lst


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


## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name):
        self.name = name

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov
def get_sites_for_state(state_abbr):
    return process(response)
    # print(name_lst)
    # return process(response)
    # return []


## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    return []

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    pass

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


# xy = get_sites_for_state(state_abbr)
# print(xy)
