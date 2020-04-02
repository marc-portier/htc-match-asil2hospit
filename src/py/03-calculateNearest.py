#! /usr/bin/env python

import argparse
import os
import json

from geopy import distance
from csv import DictReader, DictWriter

FLD_ID ="business_product_id"
FLD_PRODTYPE = "product_type"
FILTER_PRODTYPE = "BASE"
FLD_NM="name"
FLD_TYPE="discriminator"
FLD_STR="street"
FLD_NR ="house_number"
FLD_ZIP="postal_code"
FLD_GEM="main_city_name"
FLD_LAT="lat"
FLD_LON="long"
FLD_UNITS="number_of_units"
FLD_CAPACITY="maximum_capacity"
FLD_EMAIL="email"
FLD_TEL="phone1"
FLD_NEAR="nearestFC"
FLD_DIST="distanceFC"

REF_NM = 'Naam'
REF_LAT="Latitude"
REF_LON="Longitude"

FIELDS = [ FLD_ID, FLD_NM, FLD_TYPE, FLD_STR, FLD_NR, FLD_ZIP, FLD_GEM,
           FLD_UNITS, FLD_CAPACITY, FLD_EMAIL, FLD_TEL,
           FLD_LAT, FLD_LON, FLD_NEAR, FLD_DIST]

# define cli arguments
parser = argparse.ArgumentParser(description='SplitAddress field in the input csv.')
parser.add_argument('--file', help='the file to process', default='./opendata/toerisme-vlaanderen-basisregister.json')
parser.add_argument('--out', help='the file to generate', default='./opendata/fl-lodging-nearest.csv')
parser.add_argument('--ref', help='the file to generate', default='./opendata/20200330-fedasil-LijstFC.csv')
parser.add_argument('--force', help='switch to force updating fields', action='store_true')

# parse arguments and assign settings
args = parser.parse_args()
injson = os.path.abspath(args.file)
outcsv = os.path.abspath(args.out)
refcsv = os.path.abspath(args.ref)
forced = args.force

# initialize
delimiter = ';'
inlocs = []
reflocs = []

count_missing_latlon = 0


def stripUnwantedKeys(obj, REFKEYS):
    for key in list(obj.keys()):  # clone the list for this iteration a
        if not (key in REFKEYS):
            del obj[key]

# read the lines from the injson
try:
    with open(injson, 'r') as flinlocs:
        inlocs = json.load(flinlocs)
        for inloc in inlocs:
            if not(FLD_PRODTYPE in inloc) or inloc[FLD_PRODTYPE] != FILTER_PRODTYPE:
                continue    # just skip these lines, as they represent duplicate entries for the same actual lodging

            if not(FLD_LON in inloc and FLD_LAT in inloc):
                count_missing_latlon += 1
                continue    # use some geolocator before this process!
except IOError:
    print("could not read", injson)

# read the ref locations
try:
    # read lines (using utf-8-sig to survive possible BOM character)
    with open(refcsv, 'r', encoding='utf-8-sig') as flreflocs:
        dict_reader = DictReader(flreflocs, delimiter=delimiter)
        # Pass reader object to list() to get a list of lists
        reflocs = list(dict_reader)
except IOError:
    print("could not read", refcsv)

# calculate nearest
for inloc in inlocs:
    nearestFC = None
    distanceFC = 0
    for refloc in reflocs:
        thisFC = refloc[REF_NM]
        pos = (inloc[FLD_LAT], inloc[FLD_LON])
        refpos = (refloc[REF_LAT], refloc[REF_LON])
        dist = distance.distance(pos, refpos).kilometers
        if (nearestFC is None) or (dist < distanceFC):
            nearestFC = thisFC
            distanceFC = dist
    inloc[FLD_NEAR] = nearestFC
    inloc[FLD_DIST] = distanceFC

# generate output
try:
    with open(outcsv, 'w', encoding="utf-8", newline='') as flout:
        writer = DictWriter(flout, fieldnames=FIELDS, delimiter=delimiter)
        writer.writeheader()
        for inloc in inlocs:
            # strip fields not in the FIELDS list
            stripUnwantedKeys(inloc, FIELDS)
            writer.writerow(inloc)

except IOError:
    print("could not write", outcsv)

if (count_missing_latlon > 0):
    print ("*** WARNING *** there were %d entries skipped because they had missing lat-lon" % count_missing_latlon)
