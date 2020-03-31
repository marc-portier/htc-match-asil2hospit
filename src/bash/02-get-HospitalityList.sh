#! /usr/bin/bash

file=${1:-./opendata/toerisme-vlaanderen-basisregister.json}
dllink="https://opendata.visitflanders.org/sector/accommodation/base_registry.json?limit=-1"

curl --url "${dllink}" -o ${file}
