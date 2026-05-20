#!/bin/bash

# Shapefile fitxategiak sortu VTerako (Vector Tiles)

rm /tmp/landuse_merged.shp 2> /dev/null

# Lehenik tileindex-etik shapefile guztiak batu
for shp in /home9/SHP/fondo2005/fondo2005_*.shp; do
  basename=$(basename "$shp")
  if [ "$basename" = "fondo2005_idx.shp" ]; then
    echo "Saltatzen: $shp"
    continue
  fi
  if [ ! -f /tmp/landuse_merged.shp ]; then
    ogr2ogr -f "ESRI Shapefile" \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      /tmp/landuse_merged.shp \
      "$shp"
  else
    ogr2ogr -f "ESRI Shapefile" \
      -update -append \
      -where "Categoria LIKE 'Suelo e%' OR Categoria = 'Carreteras' OR Categoria = 'Autovia' OR Categoria = 'Viaductos y puentes' OR Categoria = 'Edificios'" \
      /tmp/landuse_merged.shp \
      "$shp"
  fi
  echo "Eginda: $shp"
done

# Ondoren fon_col1 gehitu
ogr2ogr -f "ESRI Shapefile" \
  -update -append \
  -where "TAG = 'cascos'" \
  /tmp/landuse_merged.shp \
  /home5/SHP/Resto/fon_col1.shp
echo "Eginda: fon_col1.shp"

exit 0
