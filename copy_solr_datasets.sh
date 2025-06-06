#!/bin/bash

export HOME="/home/lidar"

cd "${HOME}/SCRIPTS/WEB_PROD"

# Solr Datasets
ssh solr@b5mdev "bash /var/solr/script/copy_solr.sh datasets"

exit 0
