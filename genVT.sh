#!/bin/bash

# Shapefile fitxategiak sortu VTerako (Vector Tiles)

dir="/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles"

# Shapes
landuse="${dir}/vt_landuse"

# 1. landuse
landuse_tmp="/tmp/vt_landuse_tmp"
rm ${landuse_tmp}.* 2> /dev/null

# Lehenik tileindex-etik shapefile guztiak batu
for shp in /home9/SHP/fondo2005/fondo2005_*.shp; do
  basename=$(basename "$shp")
  if [ "$basename" = "fondo2005_idx.shp" ]; then
    echo "Saltatzen: $shp"
    continue
  fi
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
  echo "Eginda: $shp"
done

# Ondoren fon_col1 gehitu
ogr2ogr -f "ESRI Shapefile" \
  -update -append \
  -sql "SELECT 'Cascos' AS Categoria FROM fon_col1 WHERE TAG = 'cascos'" \
  ${landuse_tmp}.shp \
  /home5/SHP/Resto/fon_col1.shp
echo "Eginda: fon_col1.shp"

# Emaitza helburura kopiatu
rm ${landuse}.* 2> /dev/null
cp "${landuse_tmp}.shp" "${landuse}.shp"
cp "${landuse_tmp}.shx" "${landuse}.shx"
cp "${landuse_tmp}.dbf" "${landuse}.dbf"
cp "${landuse_tmp}.prj" "${landuse}.prj"
rm ${landuse_tmp}.* 2> /dev/null
echo "Kopiatuta: ${landuse}"

exit 0
