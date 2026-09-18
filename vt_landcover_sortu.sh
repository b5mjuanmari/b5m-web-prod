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
/usr/local/bin/ogr2ogr -f GPKG ./dat/gipuzkoarec1.gpkg /home5/SHP/Cuadriculas/gipurec.shp -sql "SELECT * FROM gipurec WHERE TAG IN ('KT', 'LT', 'MT', 'NT', 'PT', 'QU')" 2>> "$log" >> "$log"
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
python3 vt_disolbatu.py ./dat/fondos_veg_2025_arb.gpkg ./dat/vt_landuse_tree.gpkg $log # 15,4h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_for.gpkg ./dat/vt_landuse_forest.gpkg $log # 0,4h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_mat.gpkg ./dat/vt_landuse_scrub.gpkg $log # 0,3h
python3 vt_disolbatu.py ./dat/fondos_veg_2025_pra.gpkg ./dat/vt_landuse_meadow.gpkg $log # 2,1h

# Fusionatu 2

# Besteak sortu
echo "$(date +"%Y-%m-%d %H:%M:%S") - 3. Besteak sortu" >> "$log"
python3 vt_other.py /home5/SHP/LimMun/GIPUTZ.shp ./dat/vt_landuse_other.gpkg $log
python3 vt_beach.py /home5/SHP/Edificios/playas.shp ./dat/vt_landuse_beach.gpkg $log
python3 vt_water.py /home5/SHP/Agua/ITSASOind.shp ./dat/vt_landuse_water.gpkg $log

python3 vt_trokelatu.py ./dat/vt_landuse_water.gpkg ./dat/vt_landuse_beach.gpkg ./dat/vt_landuse_water_trok.gpkg $log # 4s

python3 vt_fusionatu_bi.py ./dat/vt_landuse_beach.gpkg ./dat/vt_landuse_water_trok.gpkg ./dat/vt_landuse_12.gpkg $log # 3s

python3 vt_fusionatu_bi.py ./dat/vt_landuse_forest.gpkg ./dat/vt_landuse_meadow.gpkg ./dat/vt_landuse_forest_meadow.gpkg $log # 2m17s
python3 vt_fusionatu_bi.py ./dat/vt_landuse_scrub.gpkg ./dat/vt_landuse_tree.gpkg ./dat/vt_landuse_scrub_tree.gpkg $log # 1m55s
python3 vt_fusionatu_bi.py ./dat/vt_landuse_forest_meadow.gpkg ./dat/vt_landuse_scrub_tree.gpkg ./dat/vt_landuse_vegetation.gpkg $log # 4m9s
rm ./dat/vt_landuse_scrub_tree.gpkg 2> /dev/null
rm ./dat/vt_landuse_forest_meadow.gpkg 2> /dev/null

python3 vt_trokelatu.py ./dat/vt_landuse_vegetation.gpkg ./dat/vt_landuse_12.gpkg ./dat/vt_landuse_vegetation_trok1.gpkg $log # 25m43s
python3 vt_trokelatu.py ./dat/vt_landuse_other.gpkg ./dat/vt_landuse_12.gpkg ./dat/vt_landuse_other_trok1.gpkg $log # 1m
python3 vt_moztu.py ./dat/vt_landuse_vegetation_trok1.gpkg ./dat/gipuzkoa.gpkg ./dat/vt_landuse_vegetation_trok2.gpkg $log # 5h44m - Gaizki, berriro egin behar
python3 vt_trokelatu.py ./dat/vt_landuse_other_trok1.gpkg ./dat/vt_landuse_vegetation_trok2.gpkg ./dat/vt_landuse_other_trok2.gpkg $log # 45m - Gaizki, berriro egin behar

python3 vt_barru_ukitu.py ./dat/gipuzkoa.gpkg ./dat/vt_landuse_12.gpkg ./dat/vt_landuse_12_gipu.gpkg $log # 57s

python3 vt_fusionatu_bi.py ./dat/vt_landuse_12_gipu.gpkg ./dat/vt_landuse_vegetation_trok2.gpkg ./dat/vt_landuse_1.gpkg $log # Falta da (4m16s)
python3 vt_fusionatu_bi.py ./dat/vt_landuse_1.gpkg ./dat/vt_landuse_other_trok2.gpkg ./dat/vt_landuse_2.gpkg $log # Falta da (4m20s)
python3 vt_trokelatu.py ./dat/gipuzkoarec.gpkg ./dat/vt_landuse_2.gpkg ./dat/vt_landuse_other_plus1.gpkg $log # Falta da (19m53s)
python3 vt_multi2poly.py  ./dat/vt_landuse_other_plus1.gpkg ./dat/vt_landuse_other_plus2.gpkg $log # Falta da (2s)
python3 vt_moztu.py ./dat/vt_landuse_other_plus2.gpkg ./dat/gipuzkoa.gpkg ./dat/vt_landuse_other_plus3.gpkg $log # Falta da (1m31s)
python3 vt_fusionatu_bi.py ./dat/vt_landuse_2.gpkg ./dat/vt_landuse_other_plus2.gpkg ./dat/vt_landuse.gpkg $log # Falta da ()

# Bukaera
echo >> "$log"
echo "${has} - Hasiera" >> "$log"
echo "$(date +"%Y-%m-%d %H:%M:%S") - Bukaera" >> "$log"

exit 0
