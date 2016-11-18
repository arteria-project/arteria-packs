#!/bin/bash

set -e 

RUNFOLDER=$1
SWAP_FROM=$2
SWAP_TO=$3

sed -i -e "s:Read number=\"${SWAP_FROM}\":Read number=\"${SWAP_TO}\":g" ${RUNFOLDER}/Unaligned/Stats/ConversionStats.xml
