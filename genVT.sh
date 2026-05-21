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
landuse_uar="vt_landuse_urban_areas_roads"

# 1. landuse
landuse_uar_f="${dir}/${landuse_uar}"
landuse_uar_tmp="/tmp/${landuse_uar}_tmp"
landuse_uar_diss="/tmp/${landuse_uar}_diss"
rm ${landuse_uar_tmp}.* 2> /dev/null
rm ${landuse_uar_diss}.* 2> /dev/null

# Erroreen kudeaketa: tmp fitxategiak garbitu huts eginez gero
trap 'rm -f ${landuse_uar_tmp}.* ${landuse_uar_diss}.*' EXIT

# Lehenik tileindex-etik shapefile guztiak batu
for shp in /home9/SHP/fondo2005/fondo2005_*.shp; do
  basename=$(basename "$shp")
  if [ "$basename" = "fondo2005_idx.shp" ]; then
    echo "Saltatzen: $shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
    continue
  fi
  echo "$shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
  if [ ! -f ${landuse_uar_tmp}.shp ]; then
    ogr2ogr -f "ESRI Shapefile" \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      ${landuse_uar_tmp}.shp \
      "$shp" || { echo "ERROREA: $shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"; exit 1; }
  else
    ogr2ogr -f "ESRI Shapefile" \
      -update -append \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      ${landuse_uar_tmp}.shp \
      "$shp" || { echo "ERROREA: $shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"; exit 1; }
  fi
done

# fon_col1 gehitu
echo "fon_col1.shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
ogr2ogr -f "ESRI Shapefile" \
  -update -append \
  -sql "SELECT 'Cascos' AS Categoria FROM fon_col1 WHERE TAG = 'cascos'" \
  ${landuse_uar_tmp}.shp \
  /home5/SHP/Resto/fon_col1.shp || { echo "ERROREA: fon_col1.shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"; exit 1; }

# cascos gehitu
echo "cascos.shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
ogr2ogr -f "ESRI Shapefile" \
  -update -append \
  -sql "SELECT 'Cascos' as Categoria FROM cascos" \
  ${landuse_uar_tmp}.shp \
  /home9/SHP/FondosRevisados/cascos.shp || { echo "ERROREA: cascos.shp - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"; exit 1; }

# Disolbatu Categoria eremuaren arabera
echo "Disolbatzen Categoria-ren arabera - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
ogr2ogr -f "ESRI Shapefile" \
  -sql "SELECT ST_Union(geometry), Categoria FROM ${landuse_uar}_tmp GROUP BY Categoria" \
  -dialect SQLite \
  ${landuse_uar_diss}.shp \
  ${landuse_uar_tmp}.shp || { echo "ERROREA: disolbatzean - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"; exit 1; }

# Emaitza helburura kopiatu
echo "Kopiatu: ${landuse_uar} - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
rm ${landuse_uar_f}.* 2> /dev/null
for ext in shp shx dbf prj; do
  [ -f "${landuse_uar_diss}.${ext}" ] && \
    cp "${landuse_uar_diss}.${ext}" "${landuse_uar_f}.${ext}" || \
    echo "ABISUA: .${ext} fitxategia ez da aurkitu - $(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
done

# Bukaera
buk="$(date '+%Y-%m-%d %H:%M:%S')"
echo >> "$log"
echo "Hasiera: $has" >> "$log"
echo "Bukaera: $buk" >> "$log"

exit 0
