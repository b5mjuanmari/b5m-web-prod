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
# 1. Erabiliko dugun taula erauzi
echo "$(date +"%Y-%m-%d %H:%M:%S") - 1. Erabiliko dugun taula erauzi" >> "$log"
#rm ./dat/SIOSEAR_20_1.gpkg 2> /dev/null
#/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_20_GUIPUZCOA_GPKG/20_GUIPUZCOA.gpkg -nln SIOSEAR_20_1 sar_20_t_combinada 2>> "$log" >> "$log" # 9s
rm ./dat/SIOSEAR_20_1_POL.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_20_1_POL.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_20_GUIPUZCOA_GPKG/20_GUIPUZCOA.gpkg -nln SIOSEAR_20_1_POL sar_20_t_poligonos 2>> "$log" >> "$log" # 9s

# 2. CSV baten arabera bersailkatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 2. CSV baten arabera bersailkatu" >> "$log"
#python3 vt_reclass_siosear.py ./dat/SIOSEAR_20_1.gpkg /home9/SHP/vt_landcover/SIOSEAR/CONF/SIOSEAR_types.csv ./dat/SIOSEAR_20_2.gpkg $log # 1m43s
python3 vt_reclass_siosear2.py ./dat/SIOSEAR_20_1_POL.gpkg /home9/SHP/vt_landcover/SIOSEAR/CONF/SIOSEAR_types.csv ./dat/SIOSEAR_20_2_POL.gpkg $log # 2m51s

# 3. b5m itsasoa txertatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. b5m itsasoa txertatu (itsasoa)" >> "$log"
rm ./dat/SIOSEAR_ITSASO_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f "GPKG" ./dat/SIOSEAR_ITSASO_01.gpkg /home5/SHP/Agua/ITSASOind.shp -sql "select SUBTIPO_E as type from ITSASOind" -nln SIOSEAR_ITSASO_01 2>> "$log" >> "$log" # 1s
rm ./dat/SIOSEAR_BEACH_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f "GPKG" ./dat/SIOSEAR_BEACH_01.gpkg ./dat/SIOSEAR_20_2.gpkg -sql "select type, geom from SIOSEAR_20_2 where type = 'beach'" -nln SIOSEAR_BEACH_01 # 1s
python3 vt_trokelatu2.py ./dat/SIOSEAR_ITSASO_01.gpkg ./dat/SIOSEAR_BEACH_01.gpkg ./dat/SIOSEAR_ITSASO_02.gpkg # 5s
/usr/local/bin/ogrinfo ./dat/SIOSEAR_ITSASO_02.gpkg -dialect SQLITE -sql "UPDATE SIOSEAR_ITSASO_02 SET type = CASE WHEN type = 'mareartekoa' THEN 'intertidal' WHEN type = 'baltsa' THEN 'pond' WHEN type = 'igerilekuko ura' THEN 'swimming pool' WHEN type = 'urmaela' THEN 'pool' WHEN type = 'urtegia' THEN 'reservoir' WHEN type = 'baltsa' THEN 'pond' WHEN type = 'baltsa' THEN 'pond' WHEN type = 'baltsa' THEN 'pond' ELSE 'water' END" 2>> "$log" >> "$log" # 1s
python3 vt_trokelatu2.py ./dat/SIOSEAR_20_2_POL.gpkg ./dat/SIOSEAR_ITSASO_02.gpkg ./dat/SIOSEAR_20_2_trok.gpkg $log # 3m48s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_2_trok.gpkg ./dat/SIOSEAR_ITSASO_02.gpkg ./dat/SIOSEAR_20_3.gpkg $log # 1m33s

## 4. Hiriguneko arrokak (rock) artifizial (artificial) jarri
#echo "$(date +"%Y-%m-%d %H:%M:%S") - 4. Hiriguneko arrokak (rock) artifizial (artificial) jarri" >> "$log"
## 4.1. GPKG berria sortu kopia gisa
#rm ./dat/SIOSEAR_20_4.gpkg 2> /dev/null
#/usr/local/bin/ogr2ogr -f "GPKG" ./dat/SIOSEAR_20_4.gpkg ./dat/SIOSEAR_20_3.gpkg -nln SIOSEAR_20_4 2>> "$log" >> "$log" # 4s
#
## 4.2. cascos.shp inportatu geruza laguntzaile gisa
#/usr/local/bin/ogr2ogr -f "GPKG" -update -nln _tmp_cascos ./dat/SIOSEAR_20_4.gpkg /home5/SHP/Edificios/cascos.shp 2>> "$log" >> "$log" # 1s
#
## 4.3. Eguneratu
#/usr/local/bin/ogrinfo ./dat/SIOSEAR_20_4.gpkg -dialect SQLITE -sql "UPDATE SIOSEAR_20_4 SET type = 'artificial' WHERE type = 'rock' AND EXISTS (SELECT 1 FROM _tmp_cascos s WHERE ST_Intersects(SIOSEAR_20_4.geom, s.geom))" 2>> "$log" >> "$log" # 45s
#
## 4.4. Geruza laguntzailea kendu
#/usr/local/bin/ogrinfo ./dat/SIOSEAR_20_4.gpkg -sql "DROP TABLE _tmp_cascos" 2>> "$log" >> "$log"
#/usr/local/bin/ogrinfo ./dat/SIOSEAR_20_4.gpkg -dialect SQLITE -sql "DELETE FROM gpkg_contents WHERE table_name = '_tmp_cascos'; DELETE FROM gpkg_geometry_columns WHERE table_name = '_tmp_cascos'" 2>> "$log" >> "$log"

# 5. Emaitza disolbatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 5. Emaitza disolbatu" >> "$log"
python3 vt_disolbatu3.py ./dat/SIOSEAR_20_3.gpkg ./dat/SIOSEAR_20_4.gpkg $log # 19m9s

# 6. Azalera handiak moztu (oraingoz type = 'artificial')
python3 vt_split.py ./dat/SIOSEAR_20_4.gpkg ./dat/SIOSEAR_20_5.gpkg "type = 'artificial'" $log # 2m15s

# 6. Behin behineko GPKGa eta estiloa kargatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 6. Behin behineko GPKGa eta estiloa kargatu" >> "$log"
rm ./dat/vt_landcover_SIOSEAR.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_SIOSEAR.gpkg ./dat/SIOSEAR_20_5.gpkg -nln vt_landcover_SIOSEAR 2>> "$log" >> "$log" # 4s

python3 vt_landcover_styles.py ./dat/vt_landcover_SIOSEAR.gpkg vt_landcover_SIOSEAR geom vt_landcover_SIOSEAR_style /home9/SHP/vt_landcover/SIOSEAR/CONF/vt_landcover_SIOSEAR3.qml $log # 1s

# Estiloen txertaketa egiaztatzeko:
#/usr/local/bin/ogrinfo -so ./dat/vt_landcover_SIOSEAR.gpkg layer_styles
#/usr/bin/sqlite3 ./dat/vt_landcover_SIOSEAR.gpkg "SELECT styleQML FROM layer_styles;"
#/usr/bin/sqlite3 ./dat/vt_landcover_SIOSEAR.gpkg "SELECT id, styleName, length(styleQML) AS bytes, useAsDefault, typeof(styleQML) FROM layer_styles;"

# Bukaera
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
