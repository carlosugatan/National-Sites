from secrets import google_places_key
from bs4 import BeautifulSoup
from alternate_advanced_caching import Cache
import requests
from datetime import datetime
from collections import OrderedDict
import plotly
import plotly.plotly as py
import sys

######################
#      SCRAPING      #
######################

def create_id(site, topic):
    return "{}_{}_{}.json".format(site, topic, str(datetime.now()).replace(' ', ''))

## ID for getting sites
def create_id_sites(urls):
    return "{}.json".format(urls, str(datetime.now()).replace(' ', ''))

def process(response):
    name_lst = []
    url_lst = []
    site_lst = []

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

        # Look at each URL and scrape that page
        for urls in url_lst:
            cache_file = "nps_address.json"
            cache_address = Cache(cache_file)

            UID = create_id_sites(urls)
            response2 = cache_address.get(UID)
            if response2 == None:
                response2 = requests.get(urls).text
                cache_address.set(UID, response2, 100)

            soup2 = BeautifulSoup(response2, "html.parser")
            try:
                ## Address Street
                address_street_fndr = soup2.find(attrs={"itemprop": "streetAddress"})
                process.address_street = address_street_fndr.text
                process.address_street = process.address_street.replace('\n', '')
                # print(process.address_street)

                ## Address City
                address_city_fndr = soup2.find(attrs={"itemprop": "addressLocality"})
                process.address_city = address_city_fndr.text
                # print(process.address_city)

                ## Address State
                address_state_fndr = soup2.find(attrs={"itemprop": "addressRegion"})
                process.address_state = address_state_fndr.text
                # print(process.address_state)

                ## Address ZIP
                address_zip_fndr = soup2.find(attrs={"itemprop": "postalCode"})
                process.address_zip = address_zip_fndr.text
                process.address_zip = process.address_zip.strip()
                # print(process.address_zip)
            except: # If address is not found
                # print("No address found for {}".format(urls))
                process.address_street = "Not found"
                process.address_city = "Not found"
                process.address_state = "Not found"
                process.address_zip = "Not found"

        national_sites = NationalSite(type, name) # Create a new NationalSite instance
        site_lst.append(national_sites) # Append each NationalSite instance to site_lst list
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
            # combines latitude and longitude
            google_coordinates.location = lat+","+lng
            # print(google_coordinates.location)
        # print("Data in cache")
        return lat,lng,google_coordinates.location
    else:
        resp = requests.get(baseurl, params=params_diction)
        obj = json.loads(resp.text)
        c2.set(unique_rep, obj, 100)
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
                print(nearbyplaces[key_dict]["values"]["results"][i]["name"])
            # print(nearby_places_lst)
        return nearby_places_lst
    else:
        resp = requests.get(baseurl, params=params_diction)
        obj = json.loads(resp.text)
        c.set(unique_rep, obj, 100)
        return obj

######################
#   NATIONAL SITES   #
######################

class NationalSite():
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self.description = process.desc
        self.url = process.url

        self.address_street = process.address_street
        self.address_city = process.address_city
        self.address_state = process.address_state
        self.address_zip = process.address_zip

    def __str__(self):
        # return "{} ({}): {} {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state,self.address_zip)
        return "{} {}".format(self.name, self.type)

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

## Must return the list of NearbyPlaces for the specific NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places(national_site):
    google_coordinates(national_site)
    google_nearby_places(google_coordinates.location)

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
# Code from Plotly guide provided for Project 2
def plot_sites_for_state(state_abbr):
    lat_vals = []
    lon_vals = []
    text_vals = []
    national_sites_list = process(response)
    for site in national_sites_list:
        try:
            full_site_name = site.name + " " + site.type
            site_coord = google_coordinates(full_site_name)
            lat_vals.append(site_coord[0])
            lon_vals.append(site_coord[1])
            text_vals.append(full_site_name)
            # print(site_coord)
        except:
            national_sites_list.remove(site)
            # print("Coordinates not found")

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat -1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 12,
                symbol = 'star',
                color = "red"
            ))]

    layout = dict(
            title = 'US National Sites<br>(Hover for National Site names)',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                lataxis = dict(range = lat_axis),
                lonaxis = dict(range = lon_axis),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(0, 76, 14)",
                center = {'lat': center_lat, 'lon': center_lon },
                countrycolor = "rgb(217, 100, 217)",
                countrywidth = 3,
                subunitwidth = 2
            ),
        )

    fig = dict( data=data, layout=layout )
    py.plot( fig, validate=False, filename='testing-national-sites' )


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
# def plot_nearby_for_site(site_object):
# Code from Plotly guide provided for Project 2
def plot_nearby_for_site(national_site):
    big_lat_vals = []
    big_lon_vals = []
    big_text_vals= []
    small_lat_vals = []
    small_lon_vals = []
    small_text_vals = []
    init_site = google_coordinates(national_site)
    big_lat_vals.append(init_site[0])
    big_lon_vals.append(init_site[1])
    big_text_vals.append(national_site)
    nearby_places = google_nearby_places(google_coordinates.location)
    for places in nearby_places:
        try:
            nearby_coord = google_coordinates(places)
            small_lat_vals.append(nearby_coord[0])
            small_lon_vals.append(nearby_coord[1])
            small_text_vals.append(places)
            print(places)
            # print(small_lat_vals)
        # if coordinates are not found, remove it from the list
        except:
            nearby_places.remove(places)
            # print("Coordinates not found")

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in big_lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in big_lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat -1, max_lat + 1]
    lon_axis = [min_lon - 1, max_lon + 1]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    trace1 = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = big_lon_vals,
            lat = big_lat_vals,
            text = big_text_vals,
            mode = 'markers',
            marker = dict(
                size = 18,
                symbol = 'star',
                color = "red"
            ))

    trace2 = dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = small_lon_vals,
            lat = small_lat_vals,
            text = small_text_vals,
            mode = 'markers',
            marker = dict(
                size = 5,
                symbol = 'circle',
                color = "blue"
            ))

    data = [trace1, trace2]

    layout = dict(
            title = 'US National Sites<br>(Hover for National Site names)',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                lataxis = dict(range = lat_axis),
                lonaxis = dict(range = lon_axis),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(0, 76, 14)",
                center = {'lat': center_lat, 'lon': center_lon },
                countrycolor = "rgb(217, 100, 217)",
                countrywidth = 3,
                subunitwidth = 3
            ),
        )

    fig = dict( data=data, layout=layout )
    py.plot( fig, validate=False, filename='national-sites-nearby-places' )

###################
#     CONFIG      #
###################
print("Hello! Interested in National Sites in the United States?")
print("Please input state abbreviation to search up it's national sites")
state_abbr = input("Please enter state abbr: ").lower()
while state_abbr != "exit":
    info = "Getting information about national site of %%..."
    print(info.replace('%%', state_abbr.upper()))
    print("***************************************************************")
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
        cache.set(UID, response, 100)
    process(response)


    ######################
    #      CONSOLE       #
    ######################
    # Welcome message
    national_sites_list_console = get_sites_for_state(state_abbr)
    national_site_message = "Here are the National Sites of %%:"
    print(national_site_message.replace('%%', state_abbr.upper()))
    print("_______________________________________________________________")
    for each_national_site in national_sites_list_console:
        print(each_national_site)
    print("***************************************************************")

    # Menu 1: Show sites on map or show nearby places
    print("1: Look at these sites on a map")
    print("2: Show nearby places of a national site")
    print("Type 'exit' to quit the program")
    choice1 = input("1 or 2?: ")
    # Choice 1 from Menu 1
    if choice1 == "1":
        print("Browser will open up to show you the sites on a map...")
        plot_sites_for_state(state_abbr)
    elif choice1 == "2":
        print()
        # Menu 2: Nearby places of a particular site
        choice2 = input("Please type a national site from the list above to show it's nearby places...: ")
        string_choice2 = "Here are the nearby places near %%%:"
        print(string_choice2.replace('%%%', choice2))
        print("_______________________________________________________________")
        get_nearby_places(choice2)
        print("***************************************************************")
        # Menu 3: Map nearby places of a National Site
        string_choice3 = "Would you like to see a map of all nearby places near %%? (y/n) "
        choice3 = input(string_choice3.replace('%%', choice2))
        if choice3 == "y":
            print("Browser will open up to show you the sites on a map...")
            plot_nearby_for_site(choice2)
        elif choice3 == "n":
            # Restart to state abbr menu
            print("Please input state abbreviation to search up it's national sites")
            print("Type 'exit' to quit the program")
            state_abbr = input("Please enter state abbr: ").lower()
            process(response)
        else:
            # print("Not a valid input")
            sys.exit()
    else:
        # print("Not a valid input")
        sys.exit()
