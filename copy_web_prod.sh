#!/bin/bash

export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"

export HOME="/home/lidar"

cd "${HOME}/SCRIPTS/WEB_PROD"

./genera_datasets.sh &

./tiles_prod.sh &

./gpkg2.sh gpkg2_1.dsv 1 1 &

ssh solr@b5mdev "bash /var/solr/script/copy_solr.sh"

exit 0
