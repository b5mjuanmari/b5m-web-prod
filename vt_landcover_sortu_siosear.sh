#!/bin/bash

HOME="/home/juanmari"
work="SCRIPTS/WEB_PROD"
gaur="$(date +"%Y%m%d")"
script=$(basename "$0" | sed 's/\..*$//')
log="./log/${script}_${gaur}.log"

cd "$HOME"
source ~/.bashrc
cd "$work"
rm "$log" 2> /dev/null
has="$(date +"%Y-%m-%d %H:%M:%S")"
echo "${has} - Hasiera" >> "$log"

# SIOSEAR
echo "$(date +"%Y-%m-%d %H:%M:%S") - 1. Erabiliko dugu taula erauzi" >> "$log"
rm ./dat/SIOSEAR_20_1.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_20_GUIPUZCOA_GPKG/20_GUIPUZCOA.gpkg -nln SIOSEAR_20_1 sar_20_t_combinada 2>> "$log" >> "$log" # 9s

echo "$(date +"%Y-%m-%d %H:%M:%S") - 2. CSV baten arabera bersailkatu" >> "$log"
python3 vt_reclass_siosear.py ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/CSV/SIOSEAR_types.csv ./dat/SIOSEAR_20_2.gpkg $log # 1m43s

echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. Emaitza disolbatu" >> "$log"
python3 vt_disolbatu.py ./dat/SIOSEAR_20_2.gpkg ./dat/SIOSEAR_20_3.gpkg $log

# Bukaera
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
