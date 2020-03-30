#! /usr/bin/env python

import argparse
import os
import re
from csv import DictReader

parser = argparse.ArgumentParser(description='SplitAddress field in the input csv.')
parser.add_argument('--file', help='the file to process', default='./opendata/20200330-fedasil-LijstFC.csv')

args = parser.parse_args()
file = os.path.abspath(args.file)
lines = []

print(file)

try:
    # read lines (using utf-8-sig to survive possible BOM character)
    with open(file, 'r', encoding='utf-8-sig') as fp:
        dict_reader = DictReader(fp, delimiter=';')
        # Pass reader object to list() to get a list of lists
        lines = list(dict_reader)

    # modify lines  --> run through lines finding parts using regexp and adding them
    for line in lines:
        adres = str(line['Adres']).splitlines()
        strnr = adres[0].rsplit(' ', 1)
        straat = strnr[0]
        nr = strnr[1] if len(strnr) > 1 else '' # some first lines have no space to split on
        (zip, gemeente) = adres[1].split(' ', 1)

        line['Straat'] = straat
        line['Nr'] = nr
        line['Zip'] = zip
        line['Gemeente'] = gemeente

    # use geolocator to find latlon
    # https://pypi.org/project/geopy/

    # write (modified) lines to csv
    # https://www.tutorialspoint.com/How-to-save-a-Python-Dictionary-to-CSV-file
    print(lines)

except IOError:
    print("could not read", file)

