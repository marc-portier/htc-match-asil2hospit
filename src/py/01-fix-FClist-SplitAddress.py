#! /usr/bin/env python

import argparse
import os
import geopy

from csv import DictReader, DictWriter
from geopy.geocoders import Nominatim

geopy.geocoders.options.default_user_agent = 'GeoLoc/0.0'
geopy.geocoders.options.default_timeout = 7

FLD_NM ="Naam"
FLD_ADR="Adres";
FLD_STR="Straat"
FLD_NR ="Nr"
FLD_ZIP="Zip"
FLD_GEM="Gemeente"
FLD_LAT="Latitude"
FLD_LON="Longitude"
FIELDS =[FLD_NM, FLD_ADR, FLD_STR, FLD_NR, FLD_ZIP, FLD_GEM, FLD_LAT, FLD_LON]

# define cli arguments
parser = argparse.ArgumentParser(description='SplitAddress field in the input csv.')
parser.add_argument('--file', help='the file to process', default='./opendata/20200330-fedasil-LijstFC.csv')
parser.add_argument('--force', help='switch to force updating fields', action='store_true')

# parse arguments and assign settings
args = parser.parse_args()
file = os.path.abspath(args.file)
forced = args.force

# initialize
country = 'Belgium'
delimiter = ';'
lines = []


def stripUnwantedKeys(obj, REFKEYS):
    for key in list(obj.keys()):  # clone the list for this iteration a
        if not (key in REFKEYS):
            del obj[key]

# start off
try:
    # read lines (using utf-8-sig to survive possible BOM character)
    with open(file, 'r', encoding='utf-8-sig') as flin:
        dict_reader = DictReader(flin, delimiter=delimiter)
        # Pass reader object to list() to get a list of lists
        lines = list(dict_reader)
except IOError:
    print("could not read", file)


# modify lines  --> run through lines finding parts using regexp and adding them
for line in lines:
    adres = line[FLD_ADR]
    straat = line[FLD_STR]
    nr = line[FLD_NR]
    zip = line[FLD_ZIP]
    gemeente = line[FLD_GEM]
    lat = line[FLD_LAT] if FLD_LAT in line else ''
    lon = line[FLD_LON] if FLD_LON in line else ''

    if (forced or straat == '' or gemeente == ''):
        adres = adres.splitlines()
        strnr = adres[0].rsplit(' ', 1)
        straat = strnr[0]
        nr = strnr[1] if len(strnr) > 1 else '' # some first lines have no space to split on
        (zip, gemeente) = adres[1].split(' ', 1)

    if (forced or lat == '' or lon == ''):
        # use geolocator to find latlon
        # https://pypi.org/project/geopy/
        loctr = Nominatim()
        qadr = "%s, %s, %s, %s" % (nr, straat, gemeente, country)
        loc = loctr.geocode(qadr)
        if loc:
            lat = loc.latitude
            lon = loc.longitude
        else:
            print("***", "WARN", "***", "No location for '%s'" % qadr)

    line[FLD_STR] = straat
    line[FLD_NR] = nr
    line[FLD_ZIP] = zip
    line[FLD_GEM] = gemeente
    line[FLD_LAT] = lat
    line[FLD_LON] = lon


# write (modified) lines to csv
# https://www.tutorialspoint.com/How-to-save-a-Python-Dictionary-to-CSV-file
try:
    with open(file, 'w', encoding="utf-8", newline='') as flout:
        writer = DictWriter(flout, fieldnames=FIELDS, delimiter=delimiter)
        writer.writeheader()
        for line in lines:
            stripUnwantedKeys(line, FIELDS)
            writer.writerow(line)

except IOError:
    print("could not write", file)


