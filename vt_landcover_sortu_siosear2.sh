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
# 1. SIOSEAR trokelatu eta fusionatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 1. SIOSEAR trokelatu eta fusionatu" >> "$log"
python3 vt_disolbatu2.py /home5/SHP/LimMun/GIPUTZ.shp /home9/SHP/vt_landcover/gipuzkoa.gpkg $log # 1s
rm ./dat/ehrec.gpkg 2> /dev/null
echo '{"type":"Polygon","coordinates":[[[450000,4635000],[690000,4635000],[690000,4815000],[450000,4815000],[450000,4635000]]]}' | /usr/local/bin/ogr2ogr -f GPKG ./dat/ehrec.gpkg /vsistdin/ -a_srs EPSG:25830 -nln ehrec 2>> "$log" >> "$log" # 1s
python3 vt_trokelatu2.py ./dat/ehrec.gpkg ./dat/gipuzkoa.gpkg ./dat/ehshad.gpkg $log # 1s
rm ./dat/ehrec.gpkg 2> /dev/null
rm ./dat/SIOSEAR_01_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_01_01.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_01_ALAVA_GPKG/01_ALAVA.gpkg -nln SIOSEAR_01_01 sar_01_t_poligonos 2>> "$log" >> "$log" # 17s
rm ./dat/SIOSEAR_20_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_20_01.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_20_GUIPUZCOA_GPKG/20_GUIPUZCOA.gpkg -nln SIOSEAR_20_01 sar_20_t_poligonos 2>> "$log" >> "$log" # 15s
rm ./dat/SIOSEAR_31_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_31_01.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_31_NAVARRA_GPKG/31_NAVARRA.gpkg -nln SIOSEAR_31_01 sar_31_t_poligonos 2>> "$log" >> "$log" # 7m27s
rm ./dat/SIOSEAR_48_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/SIOSEAR_48_01.gpkg /home9/SHP/vt_landcover/SIOSEAR/SAR2020_48_VIZCAYA_GPKG/48_VIZCAYA.gpkg -nln SIOSEAR_48_01 sar_48_t_poligonos 2>> "$log" >> "$log" # 24s
python3 vt_trokelatu2.py ./dat/SIOSEAR_01_01.gpkg ./dat/ehshad.gpkg ./dat/SIOSEAR_01_02.gpkg $log # 2m15s
python3 vt_trokelatu2.py ./dat/SIOSEAR_20_01.gpkg ./dat/ehshad.gpkg ./dat/SIOSEAR_20_02.gpkg $log # 7m03s
python3 vt_trokelatu2.py ./dat/SIOSEAR_31_01.gpkg ./dat/ehshad.gpkg ./dat/SIOSEAR_31_02.gpkg $log # 8m24s
python3 vt_trokelatu2.py ./dat/SIOSEAR_48_01.gpkg ./dat/ehshad.gpkg ./dat/SIOSEAR_48_02.gpkg $log # 2m46s
rm ./dat/ehshad.gpkg 2> /dev/null
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_01_02.gpkg ./dat/SIOSEAR_48_02.gpkg ./dat/SIOSEAR_20_03.gpkg $log # 1s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_03.gpkg ./dat/SIOSEAR_31_02.gpkg ./dat/SIOSEAR_20_04.gpkg $log # 1s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_04.gpkg ./dat/SIOSEAR_20_02.gpkg ./dat/SIOSEAR_20_05.gpkg $log # 5m35s
#rm ./dat/SIOSEAR_01_01.gpkg 2> /dev/null
rm ./dat/SIOSEAR_01_02.gpkg 2> /dev/null
#rm ./dat/SIOSEAR_31_01.gpkg 2> /dev/null
rm ./dat/SIOSEAR_31_02.gpkg 2> /dev/null
#rm ./dat/SIOSEAR_48_01.gpkg 2> /dev/null
rm ./dat/SIOSEAR_48_02.gpkg 2> /dev/null
#rm ./dat/SIOSEAR_20_01.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_02.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_03.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_04.gpkg 2> /dev/null

# 2. CSV baten arabera bersailkatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 2. CSV baten arabera bersailkatu" >> "$log"
python3 vt_reclass_siosear2.py ./dat/SIOSEAR_20_05.gpkg /home9/SHP/vt_landcover/SIOSEAR/CONF/SIOSEAR_types.csv ./dat/SIOSEAR_20_06.gpkg $log # 2m43s
rm ./dat/SIOSEAR_20_05.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_07.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f "GPKG" ./dat/SIOSEAR_20_07.gpkg ./dat/SIOSEAR_20_06.gpkg -sql "select type, geom from SIOSEAR_20_06 where type in ('farming', 'forest', 'marsh', 'meadow', 'rock', 'scrub')" -nln SIOSEAR_20_07 2>> "$log" >> "$log" # 6s

# 3. Ur masak eta hondartza txertatu #########################################
echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. Ur masak eta hondartza txertatu" >> "$log"
python3 vt_beach.py /home5/SHP/Edificios/playas.shp ./dat/vt_landcover_beach.gpkg $log # 1s
python3 vt_water.py /home5/SHP/Agua/ITSASOind.shp ./dat/vt_landcover_water.gpkg $log # 1s
python3 vt_barru_ukitu.py /home9/SHP/vt_landcover/gipuzkoa.gpkg ./dat/vt_landcover_beach.gpkg ./dat/vt_landcover_beach_gip.gpkg $log # 1s
python3 vt_barru_ukitu.py /home9/SHP/vt_landcover/gipuzkoa.gpkg ./dat/vt_landcover_water.gpkg ./dat/vt_landcover_water_gip.gpkg $log # 61s
python3 vt_trokelatu2.py ./dat/vt_landcover_water_gip.gpkg ./dat/vt_landcover_beach_gip.gpkg ./dat/vt_landcover_water_gip_trk.gpkg $log # 4s
python3 vt_fusionatu_bi.py ./dat/vt_landcover_beach_gip.gpkg ./dat/vt_landcover_water_gip_trk.gpkg ./dat/vt_landcover_beach_water_gip.gpkg $log # 3s
python3 vt_trokelatu2.py ./dat/SIOSEAR_20_07.gpkg ./dat/vt_landcover_beach_water_gip.gpkg ./dat/SIOSEAR_20_08.gpkg $log # 2m14s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_08.gpkg ./dat/vt_landcover_beach_water_gip.gpkg ./dat/SIOSEAR_20_09.gpkg $log # 1m29s
rm ./dat/vt_landcover_beach.gpkg 2> /dev/null
rm ./dat/vt_landcover_beach_gip.gpkg 2> /dev/null
rm ./dat/vt_landcover_water.gpkg 2> /dev/null
rm ./dat/vt_landcover_water_gip.gpkg 2> /dev/null
rm ./dat/vt_landcover_water_gip_trk.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_07.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_08.gpkg 2> /dev/null

# 4. Padurak (marsh) txertatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 4. Padurak (marsh) txertatu" >> "$log"
rm ./dat/SIOSEAR_20_07_marsh.gpkg
/usr/local/bin/ogr2ogr -f "GPKG" ./dat/SIOSEAR_20_07_marsh.gpkg ./dat/SIOSEAR_20_07.gpkg -sql "select type, geom from SIOSEAR_20_07 where type in ('marsh')" -nln SIOSEAR_20_07_marsh 2>> "$log" >> "$log" # 1s
python3 vt_trokelatu2.py ./dat/SIOSEAR_20_09.gpkg ./dat/SIOSEAR_20_07_marsh.gpkg ./dat/SIOSEAR_20_10.gpkg $log # 2m10s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_10.gpkg ./dat/SIOSEAR_20_07_marsh.gpkg ./dat/SIOSEAR_20_11.gpkg $log # 1m25s
rm ./dat/SIOSEAR_20_07_marsh.gpkg
rm ./dat/SIOSEAR_20_08.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_09.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_10.gpkg 2> /dev/null

# 5. Pier
echo "$(date +"%Y-%m-%d %H:%M:%S") - 5. Pier" >> "$log" # 1m46s
rm ./dat/gipuzkoarec1.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/gipuzkoarec1.gpkg /home5/SHP/Cuadriculas/gipurec.shp -sql "SELECT * FROM gipurec WHERE TAG IN ('KT', 'LT', 'MT', 'NT', 'PT', 'QU')" -nln "gipuzkoarec1" 2>> "$log" >> "$log" # 1s
python3 vt_disolbatu2.py ./dat/gipuzkoarec1.gpkg ./dat/gipuzkoarec.gpkg $log # 3s
rm ./dat/gipuzkoarec1.gpkg 2> /dev/null
python3 vt_trokelatu2.py ./dat/gipuzkoarec.gpkg ./dat/vt_landcover_beach_water_gip.gpkg ./dat/vt_pier_01.gpkg $log # 5s
python3 vt_trokelatu2.py ./dat/vt_pier_01.gpkg /home9/SHP/vt_landcover/gipuzkoa.gpkg ./dat/vt_pier_02.gpkg $log # 2s
rm ./dat/vt_pier_01.gpkg 2> /dev/null
rm ./dat/vt_landcover_intertidal_gip.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_intertidal_gip.gpkg ./dat/vt_landcover_beach_water_gip.gpkg -sql "SELECT * FROM vt_landcover_beach_water_gip WHERE type = 'intertidal'" -nln "vt_landcover_intertidal_gip" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_landcover_beach_water_gip.gpkg 2> /dev/null
python3 vt_trokelatu2.py ./dat/vt_pier_02.gpkg ./dat/vt_landcover_intertidal_gip.gpkg ./dat/vt_pier_03.gpkg $log # 1s
rm ./dat/vt_pier_02.gpkg 2> /dev/null
rm ./dat/vt_landcover_intertidal_gip.gpkg 2> /dev/null
python3 vt_multi2poly.py ./dat/vt_pier_03.gpkg ./dat/vt_pier_04.gpkg $log # 2s
rm ./dat/vt_pier_03.gpkg 2> /dev/null
rm ./dat/vt_pier_05.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier_05.gpkg ./dat/vt_pier_04.gpkg -sql "SELECT fid, 'pier' AS type, geom FROM vt_pier_04" -nln "vt_pier_05" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_pier_04.gpkg 2> /dev/null
rm ./dat/vt_pier_06.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier_06.gpkg ./dat/vt_pier_05.gpkg -sql "SELECT * FROM vt_pier_05 WHERE fid NOT IN (SELECT fid FROM vt_pier_05 ORDER BY ST_Area(geom) DESC LIMIT 3)" -nln "vt_pier_06" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_pier_05.gpkg 2> /dev/null
rm ./dat/gipuzkoa_b500.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/gipuzkoa_b500.gpkg /home9/SHP/vt_landcover/gipuzkoa.gpkg -dialect SQLITE -sql "SELECT type, ST_Buffer(geom, 500) AS geom FROM gipuzkoa" -nln "gipuzkoa_b500" 2>> "$log" >> "$log" # 3s
/usr/local/bin/ogr2ogr -update -append ./dat/vt_pier_06.gpkg ./dat/gipuzkoa_b500.gpkg -nln "gipuzkoa_b500" 2>> "$log" >> "$log" # 1s
rm ./dat/gipuzkoa_b500.gpkg 2> /dev/null
rm ./dat/vt_pier_07.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier_07.gpkg ./dat/vt_pier_06.gpkg -dialect SQLITE -sql "SELECT a.* FROM vt_pier_06 a WHERE EXISTS ( SELECT 1 FROM gipuzkoa_b500 b WHERE ST_Within(a.geom, b.geom))" -nln "vt_pier_07" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_pier_06.gpkg 2> /dev/null

#  Arroka solteak pier geruzan
GPKG="./dat/vt_pier_07.gpkg"
LAYER="vt_pier_07"
coords=(
    "565518 4794389"
    "565484 4794412"
    "570360 4793762"
    "575327 4795789"
    "585733 4798596"
    "584645 4798777"
    "589896 4799960"
    "590321 4800239"
    "597959 4804980"
    "552214 4794759"
    "552101 4794821"
    "551053 4795370"
    "551055 4795384"
    "549602 4796271"
    "548049 4796891"
    "547902 4796939"
    "547860 4796943"
    "547955 4796971"
    "547698 4797005"
    "568614 4793577"
    "568642 4793579"
    "568633 4793631"
    "568555 4793650"
    "568616 4793681"
    "559300 4794458"
    "559844 4794589"
    "552227 4794772"
    "570588 4792871"
    "570581 4792871"
    "570568 4792872"
    "570522 4792877"
    "568644 4793634"
    "571275 4793926"
    "573330 4795088"
    "580871 4796815"
    "580518 4797316"
    "585215 4798322"
    "585019 4798624"
    "584897 4798655"
    "584917 4798665"
    "586415 4798727"
    "587518 4798772"
    "587914 4798878"
    "587926 4798895"
    "588022 4798936"
    "588050 4798977"
    "588069 4798982"
    "588076 4798982"
    "588111 4798997"
    "588090 4799000"
    "588174 4799004"
    "588159 4799009"
    "588274 4799055"
    "588296 4799062"
    "588998 4799396"
    "589017 4799456"
    "589663 4799824"
    "589762 4799857"
    "589950 4799995"
    "590038 4800065"
    "590107 4800116"
    "590151 4800141"
    "590232 4800190"
    "590509 4800372"
    "591468 4802343"
    "593704 4803416"
    "593676 4803473"
    "593882 4803648"
    "594657 4804170"
    "595048 4804271"
    "595848 4804407"
    "596411 4804660"
    "596843 4804717"
    "596815 4804735"
    "596953 4804743"
    "596995 4804785"
    "597998 4805173"
    "597517 4805208"
    "597950 4805242"
    "597713 4805409"
    "597946 4805449"
    "597771 4805473"
    "597940 4805496"
    "597790 4805510"
)
for coord in "${coords[@]}"; do
    read -r X Y <<< "$coord"
    echo "Aldatzen: $X,$Y" >> "$log"
    /usr/local/bin/ogrinfo "$GPKG" \
        -dialect SQLITE \
        -sql "
            UPDATE $LAYER
            SET type = 'rock'
            WHERE ST_Contains(
                geom,
                MakePoint($X, $Y)
            )
        " \
        2>> "$log" >> "$log"
done
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_11.gpkg ./dat/vt_pier_07.gpkg ./dat/SIOSEAR_20_12.gpkg $log # 1m26s
rm ./dat/vt_pier_07.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_11.gpkg 2> /dev/null

# 6. Ur hutsuneak bete (ken Bidasoko pantalana)
echo "$(date +"%Y-%m-%d %H:%M:%S") - 6. Ur hutsuneak bete" >> "$log"
rm ./dat/vt_water_holes_01.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_water_holes_01.gpkg ./dat/SIOSEAR_20_06.gpkg -sql "SELECT type, geom FROM SIOSEAR_20_06 WHERE type = 'water'" -nln "vt_water_holes_01" 2>> "$log" >> "$log" # 1s
/usr/local/bin/ogrinfo ./dat/vt_water_holes_01.gpkg -dialect SQLITE -sql "UPDATE vt_water_holes_01 SET type = 'water other'" 2>> "$log" >> "$log"
rm ./dat/SIOSEAR_20_06.gpkg 2> /dev/null
python3 vt_trokelatu2.py ./dat/vt_water_holes_01.gpkg ./dat/SIOSEAR_20_12.gpkg ./dat/vt_water_holes_02.gpkg $log # 55s
rm ./dat/vt_water_holes_01.gpkg 2> /dev/null
rm ./dat/vt_tmp_bida_01.gpkg
echo '{"type":"Polygon","coordinates":[[[598420,4800000],[598480,4800000],[598480,4800050],[598420,4800050],[598420,4800000]]]}' | /usr/local/bin/ogr2ogr -f GPKG ./dat/vt_tmp_bida_01.gpkg /vsistdin/ -a_srs EPSG:25830 -nln vt_tmp_bida_01 2>> "$log" >> "$log" # 1s
python3 vt_trokelatu2.py ./dat/vt_water_holes_02.gpkg ./dat/vt_tmp_bida_01.gpkg ./dat/vt_water_holes_03.gpkg $log # 5s
rm ./dat/vt_water_holes_02.gpkg 2> /dev/null
rm ./dat/vt_tmp_bida_01.gpkg
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_12.gpkg ./dat/vt_water_holes_03.gpkg ./dat/SIOSEAR_20_13.gpkg $log # 1m30s
rm ./dat/vt_water_holes_03.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_12.gpkg 2> /dev/null

# 7. Trokelatu zubiak, pasabideak, errepideak eta eraikinak...
echo "$(date +"%Y-%m-%d %H:%M:%S") - 7. Trokelatu zubiak, pasabideak, errepideak eta eraikinak..." >> "$log"
# Zubiak
rm ./dat/vt_tmp_zubiak.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_tmp_zubiak.gpkg /home5/SHP/Viales/puente.shp -sql "SELECT 'zubia' as type FROM puente" -nln "vt_tmp_zubiak" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_tmp_pasabideak.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_tmp_pasabideak.gpkg /home5/SHP/Viales/pasarela.shp -sql "SELECT 'pasabidea' as type FROM pasarela" -nln "vt_tmp_pasabideak" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_tmp_errepideak.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_tmp_errepideak.gpkg /home5/SHP/Viales/corre_pol.shp -sql "SELECT 'errepidea' as type FROM corre_pol" -a_srs "EPSG:25830" -nln "vt_tmp_errepideak" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_tmp_eraikinak.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_tmp_eraikinak.gpkg /home5/SHP/Edificios/a_edifind.shp -sql "SELECT 'eraikina' as type FROM a_edifind" -nln "vt_tmp_eraikinak" 2>> "$log" >> "$log" # 6s
# Honeraino 51m03s
python3 vt_fusionatu_bi.py ./dat/vt_tmp_zubiak.gpkg ./dat/vt_tmp_pasabideak.gpkg ./dat/vt_tmp_artificial_01.gpkg $log # 1s
python3 vt_fusionatu_bi.py ./dat/vt_tmp_artificial_01.gpkg ./dat/vt_tmp_errepideak.gpkg ./dat/vt_tmp_artificial_02.gpkg $log # 2s
rm ./dat/vt_tmp_artificial_01.gpkg 2> /dev/null
python3 vt_fusionatu_bi.py ./dat/vt_tmp_artificial_02.gpkg ./dat/vt_tmp_eraikinak.gpkg ./dat/vt_tmp_artificial_03.gpkg $log # 26s
rm ./dat/vt_tmp_artificial_02.gpkg 2> /dev/null
rm ./dat/vt_tmp_zubiak.gpkg 2> /dev/null
rm ./dat/vt_tmp_pasabideak.gpkg 2> /dev/null
rm ./dat/vt_tmp_errepideak.gpkg 2> /dev/null
rm ./dat/vt_tmp_eraikinak.gpkg 2> /dev/null
python3 vt_disolbatu3.py ./dat/vt_tmp_artificial_03.gpkg ./dat/vt_tmp_artificial_04.gpkg $log # 2m49s
rm ./dat/vt_tmp_artificial_03.gpkg 2> /dev/null
python3 vt_disolbatu4.py ./dat/SIOSEAR_20_13.gpkg ./dat/SIOSEAR_20_14.gpkg type $log # 4m06s
rm ./dat/SIOSEAR_20_13.gpkg 2> /dev/null
python3 vt_trokelatu3.py ./dat/SIOSEAR_20_14.gpkg ./dat/vt_tmp_artificial_04.gpkg ./dat/SIOSEAR_20_15.gpkg $log # 2m23s
rm ./dat/vt_tmp_artificial_04.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_14.gpkg 2> /dev/null

# 8. Ura disolbatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 8. Ura disolbatu" >> "$log"
/usr/local/bin/ogrinfo ./dat/SIOSEAR_20_15.gpkg -dialect SQLITE -sql "UPDATE SIOSEAR_20_15 SET type = CASE WHEN type IN ('inner water','pond','pool','reservoir','sea','swimming pool') THEN 'water' ELSE type END" # 2s
python3 vt_disolbatu4.py ./dat/SIOSEAR_20_15.gpkg ./dat/SIOSEAR_20_16.gpkg type $log # 3m29s
rm ./dat/SIOSEAR_20_15.gpkg 2> /dev/null

# 9. Artificial
echo "$(date +"%Y-%m-%d %H:%M:%S") - 9. Artificial" >> "$log"
python3 vt_trokelatu3.py /home9/SHP/vt_landcover/gipuzkoa.gpkg ./dat/SIOSEAR_20_16.gpkg ./dat/vt_tmp_artificial_05.gpkg $log # 3m33s
python3 vt_multi2poly.py ./dat/vt_tmp_artificial_05.gpkg ./dat/vt_tmp_artificial_06.gpkg $log # 17s
rm ./dat/vt_tmp_artificial_05.gpkg 2> /dev/null
/usr/local/bin/ogrinfo ./dat/vt_tmp_artificial_06.gpkg -dialect SQLITE -sql "UPDATE vt_tmp_artificial_06 SET type = 'artificial'" 2>> "$log" >> "$log" # 1s
python3 vt_fusionatu_bi.py ./dat/SIOSEAR_20_16.gpkg ./dat/vt_tmp_artificial_06.gpkg ./dat/SIOSEAR_20_17.gpkg $log # 43s
rm ./dat/vt_tmp_artificial_06.gpkg 2> /dev/null
rm ./dat/SIOSEAR_20_16.gpkg 2> /dev/null

# 10. 'water other' (SIOSEAR) birsailkatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 10. 'water other' (SIOSEAR) birsailkatu" >> "$log"
python3 vt_multi2poly.py ./dat/SIOSEAR_20_17.gpkg ./dat/SIOSEAR_20_18.gpkg $log # 53s
rm ./dat/SIOSEAR_20_17.gpkg 2> /dev/null
python3 vt_reclass_water.py ./dat/SIOSEAR_20_18.gpkg ./dat/SIOSEAR_20_19.gpkg $log # 12m26s
rm ./dat/SIOSEAR_20_18.gpkg 2> /dev/null
python3 vt_multi2poly.py ./dat/SIOSEAR_20_19.gpkg ./dat/SIOSEAR_20_20.gpkg $log # 53s
rm ./dat/SIOSEAR_20_19.gpkg 2> /dev/null
python3 vt_disolbatu4.py ./dat/SIOSEAR_20_20.gpkg ./dat/SIOSEAR_20_21.gpkg type $log # 14m04s
rm ./dat/SIOSEAR_20_20.gpkg 2> /dev/null
python3 vt_multi2poly.py ./dat/SIOSEAR_20_21.gpkg ./dat/SIOSEAR_20_22.gpkg $log # 49s
rm ./dat/SIOSEAR_20_21.gpkg 2> /dev/null

# 10. Azalera handiak moztu (oraingoz type = 'artificial')
echo "$(date +"%Y-%m-%d %H:%M:%S") - 10. Azalera handiak moztu" >> "$log"
#python3 vt_split.py ./dat/SIOSEAR_20_22.gpkg ./dat/SIOSEAR_20_23.gpkg "type = 'artificial'" $log # ?
python3 vt_split.py ./dat/SIOSEAR_20_22.gpkg ./dat/SIOSEAR_20_23.gpkg $log # 2m35s
rm ./dat/SIOSEAR_20_22.gpkg 2> /dev/null

# 11. Behin behineko GPKGa eta estiloa kargatu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 11. Behin behineko GPKGa eta estiloa kargatu" >> "$log"
####rm /home9/SHP/vt_landcover/vt_landcover_gipu2.gpkg 2> /dev/null
####/usr/local/bin/ogr2ogr -f GPKG /home9/SHP/vt_landcover/vt_landcover_gipu2.gpkg /home9/SHP/vt_landcover/vt_landcover_gipu.gpkg -nln vt_landcover_gipu2 # 11s
rm ./dat/vt_landcover_gipu.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_gipu.gpkg ./dat/SIOSEAR_20_23.gpkg -nln vt_landcover_gipu 2>> "$log" >> "$log" # 2s
rm ./dat/SIOSEAR_20_23.gpkg 2> /dev/null
python3 vt_landcover_styles.py ./dat/vt_landcover_gipu.gpkg vt_landcover_gipu geom vt_landcover_gipu /home9/SHP/vt_landcover/styles/vt_landcover_gipu.qml $log # 1s
/usr/local/bin/ogrinfo ./dat/vt_landcover_gipu.gpkg -sql "VACUUM" 2>> "$log" >> "$log" # 3s

# Bukaera ??m??s
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
