#!/bin/bash

# Shapefile fitxategiak sortu VTerako (Vector Tiles)

dir="/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles"

# Log
o="$(pwd)"
prc="$(echo "$0" | gawk 'BEGIN{FS="/"}{split($NF,a,".");print a[1]}')"
gaur="$(date +'%Y%m%d')"
log="${o}/log/${prc}_${gaur}.log"
rm "$log" 2> /dev/null

# Hasiera
has="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Hasiera: $has" >> "$log"

# Shapefielak
landuse="${dir}/vt_landuse"

# 1. landuse
landuse_tmp="/tmp/vt_landuse_tmp"
rm ${landuse_tmp}.* 2> /dev/null

# Lehenik tileindex-etik shapefile guztiak batu
for shp in /home9/SHP/fondo2005/fondo2005_*.shp; do
  basename=$(basename "$shp")
  if [ "$basename" = "fondo2005_idx.shp" ]; then
    echo "Saltatzen: $shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
    continue
  fi
  echo "$shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
  if [ ! -f ${landuse_tmp}.shp ]; then
    ogr2ogr -f "ESRI Shapefile" \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      ${landuse_tmp}.shp \
      "$shp"
  else
    ogr2ogr -f "ESRI Shapefile" \
      -update -append \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      ${landuse_tmp}.shp \
      "$shp"
  fi
done

# Ondoren fon_col1 gehitu
echo "fon_col1.shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
ogr2ogr -f "ESRI Shapefile" \
  -update -append \
  -sql "SELECT 'Cascos' AS Categoria FROM fon_col1 WHERE TAG = 'cascos'" \
  ${landuse_tmp}.shp \
  /home5/SHP/Resto/fon_col1.shp

# Emaitza helburura kopiatu
echo "Kopiatu: ${landuse} - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
rm ${landuse}.* 2> /dev/null
cp "${landuse_tmp}.shp" "${landuse}.shp"
cp "${landuse_tmp}.shx" "${landuse}.shx"
cp "${landuse_tmp}.dbf" "${landuse}.dbf"
cp "${landuse_tmp}.prj" "${landuse}.prj"
rm ${landuse_tmp}.* 2> /dev/null

# Bukaera
buk="$(date '+%Y-%m-%d %H:%M:%S')"
echo >> "$log"
echo "Hasiera: $has" >> "$log"
echo "Bukaera: $buk" >> "$log"

exit 0
