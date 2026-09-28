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

# Oinarriak disolbatu
python3 vt_disolbatu2.py /home5/SHP/LimMun/GIPUTZ.shp ./dat/gipuzkoa.gpkg $log # 1s
rm ./dat/gipuzkoarec1.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/gipuzkoarec1.gpkg /home5/SHP/Cuadriculas/gipurec.shp -sql "SELECT * FROM gipurec WHERE TAG IN ('KT', 'LT', 'MT', 'NT', 'PT', 'QU')" -nln "gipuzkoarec1" 2>> "$log" >> "$log"
python3 vt_disolbatu2.py ./dat/gipuzkoarec1.gpkg ./dat/gipuzkoarec.gpkg $log # 1s
rm ./dat/gipuzkoarec1.gpkg 2> /dev/null

# Fusionatu #1 50"
echo "$(date +"%Y-%m-%d %H:%M:%S") - 1. Landaretza Shapefileak fusionatu" >> "$log"
python3 vt_fusionatu.py /home9/SHP/Fondos2025 ./dat/fondos_veg_2025_arb.gpkg arb $log
python3 vt_fusionatu.py /home9/SHP/Fondos2025 ./dat/fondos_veg_2025_for.gpkg for $log
python3 vt_fusionatu.py /home9/SHP/Fondos2025 ./dat/fondos_veg_2025_mat.gpkg mat $log
python3 vt_fusionatu.py /home9/SHP/Fondos2025 ./dat/fondos_veg_2025_pra.gpkg pra $log

# Disolbatu 36'
echo "$(date +"%Y-%m-%d %H:%M:%S") - 2. Landaretza disolbatu" >> "$log"
python3 vt_disolbatu.py ./dat/fondos_veg_2025_arb.gpkg ./dat/vt_landcover_tree.gpkg $log # 15,4h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_for.gpkg ./dat/vt_landcover_forest.gpkg $log # 0,4h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_mat.gpkg ./dat/vt_landcover_scrub.gpkg $log # 0,3h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_pra.gpkg ./dat/vt_landcover_meadow.gpkg $log # 2,1h

# Fusionatu 2

# Besteak sortu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. Besteak sortu" >> "$log"
python3 vt_other.py /home5/SHP/LimMun/GIPUTZ.shp ./dat/vt_landcover_other.gpkg $log
python3 vt_beach.py /home5/SHP/Edificios/playas.shp ./dat/vt_landcover_beach.gpkg $log
python3 vt_water.py /home5/SHP/Agua/ITSASOind.shp ./dat/vt_landcover_water.gpkg $log

python3 vt_trokelatu.py ./dat/vt_landcover_water.gpkg ./dat/vt_landcover_beach.gpkg ./dat/vt_landcover_water_trok.gpkg $log # 4s
rm ./dat/vt_landcover_water.gpkg 2> /dev/null

python3 vt_fusionatu_bi.py ./dat/vt_landcover_beach.gpkg ./dat/vt_landcover_water_trok.gpkg ./dat/vt_landcover_12.gpkg $log # 3s
rm ./dat/vt_landcover_beach.gpkg 2> /dev/null
rm ./dat/vt_landcover_water_trok.gpkg 2> /dev/null

python3 vt_fusionatu_bi.py ./dat/vt_landcover_forest.gpkg ./dat/vt_landcover_meadow.gpkg ./dat/vt_landcover_forest_meadow.gpkg $log # 2m17s
python3 vt_fusionatu_bi.py ./dat/vt_landcover_scrub.gpkg ./dat/vt_landcover_tree.gpkg ./dat/vt_landcover_scrub_tree.gpkg $log # 1m55s
python3 vt_fusionatu_bi.py ./dat/vt_landcover_forest_meadow.gpkg ./dat/vt_landcover_scrub_tree.gpkg ./dat/vt_landcover_vegetation.gpkg $log # 4m9s
rm ./dat/vt_landcover_scrub_tree.gpkg 2> /dev/null
rm ./dat/vt_landcover_forest_meadow.gpkg 2> /dev/null

python3 vt_barru_ukitu.py ./dat/gipuzkoa.gpkg ./dat/vt_landcover_12.gpkg ./dat/vt_landcover_12_gipu.gpkg $log # 58s
rm ./dat/vt_landcover_12.gpkg 2> /dev/null
python3 vt_rename_subtype.py ./dat/vt_landcover_12_gipu.gpkg ./dat/vt_landcover_12_gipu2.gpkg $log # 2s
rm ./dat/vt_landcover_12_gipu.gpkg 2> /dev/null

python3 vt_moztu.py ./dat/vt_landcover_vegetation.gpkg ./dat/gipuzkoa.gpkg ./dat/vt_landcover_vegetation_gipu.gpkg $log # 5h46m

# Overlay
python3 vt_overlay.py ./dat/vt_landcover_12_gipu2.gpkg ./dat/vt_landcover_vegetation_gipu.gpkg ./dat/vt_landcover_12_vegetation_gipu.gpkg $log # 28m5s
rm ./dat/vt_landcover_12_gipu2.gpkg 2> /dev/null
rm ./dat/vt_landcover_vegetation_gipu.gpkg 2> /dev/null
python3 vt_reclass.py ./dat/vt_landcover_12_vegetation_gipu.gpkg ./dat/vt_landcover_12_vegetation_gipu2.gpkg $log # 4m18s (intertidal + meadow = marsh)
rm ./dat/vt_landcover_12_vegetation_gipu.gpkg 2> /dev/null

./vt_dis_disolbatu.sh ./dat/vt_landcover_12_vegetation_gipu2.gpkg $log # 1m52s
python3 vt_fusionatu_bi.py ./dat/vt_landcover_other_trok3.gpkg ./dat/vt_landcover_12_vegetation_gipu2_dis.gpkg ./dat/vt_landcover_1.gpkg $log # 13m14s
#rm ./dat/vt_landcover_other_trok3.gpkg 2> /dev/null
rm ./dat/vt_landcover_12_vegetation_gipu2_dis.gpkg 2> /dev/null

# Pier
echo "$(date +"%Y-%m-%d %H:%M:%S") - 4. Pier" >> "$log" # 15s
rm ./dat/vt_landcover_water_sea.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_water_sea.gpkg ./dat/vt_landcover_water.gpkg -sql "SELECT * FROM vt_landcover_water WHERE subtype = 'sea'" -nln "vt_landcover_water_sea" 2>> "$log" >> "$log" # 4s
python3 vt_trokelatu.py ./dat/gipuzkoarec.gpkg ./dat/vt_landcover_water_sea.gpkg ./dat/vt_pier1.gpkg $log # 9s
rm ./dat/vt_landcover_water_sea.gpkg 2> /dev/null
rm ./dat/gipuzkoarec2.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/gipuzkoarec2.gpkg /home5/SHP/Cuadriculas/gipurec.shp -sql "SELECT * FROM gipurec" -nln "gipuzkoarec2" 2>> "$log" >> "$log"
python3 vt_disolbatu2.py ./dat/gipuzkoarec2.gpkg ./dat/gipuzkoarec_oso.gpkg $log # 2s
rm ./dat/gipuzkoarec2.gpkg 2> /dev/null
python3 vt_trokelatu.py ./dat/gipuzkoarec_oso.gpkg ./dat/gipuzkoa.gpkg ./dat/gipuzkoashad.gpkg $log # 1s
python3 vt_trokelatu.py ./dat/vt_pier1.gpkg ./dat/gipuzkoashad.gpkg ./dat/vt_pier2.gpkg $log # 2s
python3 vt_trokelatu.py ./dat/vt_pier1.gpkg ./dat/gipuzkoa.gpkg ./dat/vt_pier2.gpkg $log # 2s
rm ./dat/vt_pier1.gpkg 2> /dev/null
rm ./dat/vt_landcover_water_intertidal.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr -f GPKG ./dat/vt_landcover_water_intertidal.gpkg ./dat/vt_landcover_water.gpkg -sql "SELECT * FROM vt_landcover_water WHERE subtype = 'intertidal'" -nln "vt_landcover_water_intertidal" 2>> "$log" >> "$log" # 6s
python3 vt_trokelatu.py ./dat/vt_pier2.gpkg ./dat/vt_landcover_water_intertidal.gpkg ./dat/vt_pier3.gpkg $log # 6s
rm ./dat/vt_pier2.gpkg 2> /dev/null
rm ./dat/vt_landcover_water_intertidal.gpkg 2> /dev/null
python3 vt_multi2poly.py ./dat/vt_pier3.gpkg ./dat/vt_pier4.gpkg $log # 2s
rm ./dat/vt_pier3.gpkg 2> /dev/null
rm ./dat/vt_pier5.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier5.gpkg ./dat/vt_pier4.gpkg -sql "SELECT fid, 'pier' AS type, geom FROM vt_pier4" -nln "vt_pier5" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_pier4.gpkg 2> /dev/null
rm ./dat/vt_pier6.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier6.gpkg ./dat/vt_pier5.gpkg -sql "SELECT * FROM vt_pier5 WHERE fid NOT IN (SELECT fid FROM vt_pier5 ORDER BY ST_Area(geom) DESC LIMIT 3)" -nln "vt_pier6" 2>> "$log" >> "$log" # 1s
rm ./dat/vt_pier5.gpkg 2> /dev/null
rm ./dat/gipuzkoa_b500.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/gipuzkoa_b500.gpkg ./dat/gipuzkoa.gpkg -dialect SQLITE -sql "SELECT type, ST_Buffer(geom, 500) AS geom FROM gipuzkoa" -nln "gipuzkoa_b500" 2>> "$log" >> "$log" # 7s
/usr/local/bin/ogr2ogr -update -append ./dat/vt_pier6.gpkg ./dat/gipuzkoa_b500.gpkg -nln "gipuzkoa_b500" 2>> "$log" >> "$log" # 4s
rm ./dat/vt_pier7.gpkg 2> /dev/null
/usr/local/bin/ogr2ogr ./dat/vt_pier7.gpkg ./dat/vt_pier6.gpkg -dialect SQLITE -sql "SELECT a.* FROM vt_pier6 a WHERE EXISTS ( SELECT 1 FROM gipuzkoa_b500 b WHERE ST_Within(a.geom, b.geom))" -nln "vt_pier7" 2>> "$log" >> "$log" # 4s
rm ./dat/vt_pier6.gpkg 2> /dev/null

# Arroka solteak pier geruzan
echo "$(date +"%Y-%m-%d %H:%M:%S") - 5. Arroka solteak pier geruzan" >> "$log"
GPKG="./dat/vt_pier7.gpkg"
LAYER="vt_pier7"
coords=(
    "597959 4804980"
    "570360 4793762"
    "565515 4794380"
    "565499 4794420"
    "565485 4794401"
    "575309 4795786"
    "585724 4798595"
    "584640 4798780"
    "589899 4799956"
    "590329 4800244"
    "590321 4800237"
    "598351 4800667"
    "598374 4800692"
    "598348 4800660"
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
echo "$(date +"%Y-%m-%d %H:%M:%S") - Amaituta (5. Arroka solteak pier geruzan)" >> "$log"

python3 vt_fusionatu_bi.py ./dat/vt_landcover_1.gpkg ./dat/vt_pier7.gpkg ./dat/vt_landcover.gpkg $log # 12m40s
rm ./dat/vt_pier7.gpkg 2> /dev/null
rm ./dat/vt_landcover_1.gpkg 2> /dev/null

# Bukaera
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
