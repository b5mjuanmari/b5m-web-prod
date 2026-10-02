#!/bin/bash

set -e

INPUTB="vt_landcover_SIOSEAR_QT59"
OUTPUTB="vt_landcover_SIOSEAR_QT59_lowzoom"

AREA_THRESHOLD="${1:-10000}"
SNAP_THRESHOLD="${2:-0.1}"

INPUT="$(readlink -f ./dat/${INPUTB}.gpkg)"
OUTPUT="$(readlink -f ./dat/${OUTPUTB}.gpkg)"

GISDBASE=$(mktemp -d)
TMPDIR=$(mktemp -d)

SRC_SHP="${TMPDIR}/src.shp"
OUT_SHP="${TMPDIR}/out.shp"

cleanup() {
    echo "Cleaning up temporary files..."
    rm -rf "${GISDBASE}"
    rm -rf "${TMPDIR}"
}

trap cleanup EXIT

echo "AREA_THRESHOLD=${AREA_THRESHOLD}"
echo "SNAP_THRESHOLD=${SNAP_THRESHOLD}"

echo "STEP 1/5: GPKG -> Shapefile"

ogr2ogr \
    -overwrite \
    "${SRC_SHP}" \
    "${INPUT}" \
    "${INPUTB}"

echo "STEP 2/5: Shapefile -> GRASS"

grass -c EPSG:25830 "${GISDBASE}/work" --exec bash -c "

    echo 'Importing...'

    v.in.ogr \
        input='${SRC_SHP}' \
        output=landcover \
        snap=${SNAP_THRESHOLD} \
        --overwrite

    echo 'Removing polygons smaller than ${AREA_THRESHOLD} m2...'

    v.clean \
        input=landcover \
        output=landcover_rmarea \
        tool=rmarea \
        threshold=${AREA_THRESHOLD} \
        --overwrite

    echo 'Rebuilding topology...'

    v.build \
        map=landcover_rmarea

    echo 'Simplifying geometries...'

    v.generalize \
        input=landcover_rmarea \
        output=landcover_gen \
        method=douglas \
        threshold=50 \
        --overwrite

    echo 'Building final topology...'

    v.build \
        map=landcover_gen

    echo 'Exporting result...'

    v.out.ogr \
        input=landcover_gen \
        output='${OUT_SHP}' \
        format=ESRI_Shapefile \
        --overwrite
"

echo "STEP 3/5: Shapefile -> GeoPackage"

ogr2ogr \
    -overwrite \
    -f GPKG \
    "${OUTPUT}" \
    "${OUT_SHP}" \
    -nln "${OUTPUTB}"

echo "STEP 4/5: Spatial index"

ogrinfo "${OUTPUT}" \
    -sql "SELECT CreateSpatialIndex('${OUTPUTB}','geom')" \
    > /dev/null 2>&1 || true

echo "STEP 5/5: Statistics"

ogrinfo -so \
    "${OUTPUT}" \
    "${OUTPUTB}"

echo
echo "DONE"
echo "Output: ${OUTPUT}"
