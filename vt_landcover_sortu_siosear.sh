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
echo "$(date +"%Y-%m-%d %H:%M:%S") - 1. Erabiliko dugun taula erauzi" >> "$log"
rm ./dat/SIOSEAR_20_1.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_20_GUIPUZCOA_GPKG/20_GUIPUZCOA.gpkg -nln SIOSEAR_20_1 sar_20_t_combinada 2>> "$log" >> "$log" # 9s

echo "$(date +"%Y-%m-%d %H:%M:%S") - 2. CSV baten arabera bersailkatu" >> "$log"
python3 vt_reclass_siosear.py ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/CONF/SIOSEAR_types.csv ./dat/SIOSEAR_20_2.gpkg $log # 1m43s

echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. Emaitza disolbatu" >> "$log"
python3 vt_disolbatu.py ./dat/SIOSEAR_20_2.gpkg ./dat/SIOSEAR_20_3.gpkg $log # 1h25m16s

# Ondoren...
# B5m marearteko eta igerilekuen datuak txertatu
# Eta agian zerbait gehiago...

# Behin behineko GPKGa eta estiloa kargatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 4. Behin behineko GPKGa eta estiloa kargatu" >> "$log"
rm ./dat/vt_landcover_SIOSEAR.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_SIOSEAR.gpkg ./dat/SIOSEAR_20_3.gpkg -nln vt_landcover_SIOSEAR 2>> "$log" >> "$log" # 4s

python3 vt_landcover_styles.py ./dat/vt_landcover_SIOSEAR.gpkg vt_landcover_SIOSEAR geom vt_landcover_SIOSEAR_style /home9/SHP/vt_landcover/SIOSEAR/CONF/vt_landcover_SIOSEAR.qml $log # 1s

# Estiloen txertaketa egiaztatzeko:
#/usr/local/bin/ogrinfo -so ./dat/vt_landcover_SIOSEAR.gpkg layer_styles
#/usr/bin/sqlite3 ./dat/vt_landcover_SIOSEAR.gpkg "SELECT styleQML FROM layer_styles;"
#/usr/bin/sqlite3 ./dat/vt_landcover_SIOSEAR.gpkg "SELECT id, styleName, length(styleQML) AS bytes, useAsDefault, typeof(styleQML) FROM layer_styles;"

# Bukaera
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
