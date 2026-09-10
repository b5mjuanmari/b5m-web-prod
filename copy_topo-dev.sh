#!/bin/bash

#
# TOPO-DEV ingurunea kopiatzeko scripta
#

dir1="TOPO-DEV2"
dir2="topo"

# Kopia
rm -rf "./${dir2}" 2> /dev/null
cp -rp "../${dir1}" "./${dir2}"

exit 0
