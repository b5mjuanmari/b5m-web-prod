#!/bin/bash

HOME="/home/juanmari"
work="SCRIPTS/WEB_PROD"
gaur="$(date +"%Y%m%d")"
script=$(basename "$0" | sed 's/\..*$//')
LOG_FILE="./log/${script}_${gaur}.log"

cd "$HOME"
source ~/.bashrc
cd "$work"

rm -f "${LOG_FILE}" 2> /dev/null

exec >> "${LOG_FILE}" 2>&1

echo "=================================================="
echo "START : $(date '+%Y-%m-%d %H:%M:%S')"
echo "SCRIPT: ${SCRIPT_NAME}"
echo "LOG   : ${LOG_FILE}"
echo "=================================================="
echo

set -euo pipefail

##############################################################################
# ERABILERA
#
# ./vt_simplify_grid.sh \
#     vt_landcover_SIOSEAR \
#     10000 \
#     0.1 \
#     5000 \
#     3000
#
# PARAMETROAK
#
# $1 layer/gpkg oinarrizko izena
# $2 rmarea threshold (m2)
# $3 snap threshold (m)
# $4 tile tamaina (m)
# $5 buffer tamaina (m)
##############################################################################

INPUTB="${1}"
AREA_THRESHOLD="${2:-10000}"
SNAP_THRESHOLD="${3:-0.1}"
TILE_SIZE="${4:-5000}"
BUFFER_SIZE="${5:-3000}"

INPUT="./dat/${INPUTB}.gpkg"
OUTPUT="./dat/${INPUTB}_lowzoom.gpkg"
OUTPUT_DISS="./dat/${INPUTB}_lowzoom_dissolved.gpkg"

##############################################################################

WORKDIR=$(mktemp -d)
GISDBASE=$(mktemp -d)

cleanup() {
    echo "Cleaning up..."
    rm -rf "${WORKDIR}"
    rm -rf "${GISDBASE}"
}

trap cleanup EXIT

##############################################################################
# EXTENT
##############################################################################

EXTENT=$(/usr/local/bin/ogrinfo -so "${INPUT}" "${INPUTB}" |
grep "Extent:" |
sed -E 's/Extent: \(([^,]+), ([^)]+)\) - \(([^,]+), ([^)]+)\)/\1 \2 \3 \4/')

read XMIN YMIN XMAX YMAX <<< "${EXTENT}"

XMIN=$(printf "%.0f" "${XMIN}")
YMIN=$(printf "%.0f" "${YMIN}")
XMAX=$(printf "%.0f" "${XMAX}")
YMAX=$(printf "%.0f" "${YMAX}")

echo
echo "INPUT            : ${INPUT}"
echo "AREA_THRESHOLD   : ${AREA_THRESHOLD}"
echo "SNAP_THRESHOLD   : ${SNAP_THRESHOLD}"
echo "TILE_SIZE        : ${TILE_SIZE}"
echo "BUFFER_SIZE      : ${BUFFER_SIZE}"
echo

##############################################################################
# GARBITU AURREKO EMAITZAK
##############################################################################

rm -f "${OUTPUT}"
rm -f "${OUTPUT_DISS}"

FIRST_TILE=1

##############################################################################
# TILE LOOP
##############################################################################

for ((TXMIN=XMIN; TXMIN<XMAX; TXMIN+=TILE_SIZE))
do
for ((TYMIN=YMIN; TYMIN<YMAX; TYMIN+=TILE_SIZE))
do

    TXMAX=$((TXMIN + TILE_SIZE))
    TYMAX=$((TYMIN + TILE_SIZE))

    BXMIN=$((TXMIN - BUFFER_SIZE))
    BYMIN=$((TYMIN - BUFFER_SIZE))
    BXMAX=$((TXMAX + BUFFER_SIZE))
    BYMAX=$((TYMAX + BUFFER_SIZE))

    TILE_ID="${TXMIN}_${TYMIN}"

    echo
    echo "=================================================="
    echo "Tile ${TILE_ID}"
    echo "=================================================="

    TILE_GPKG="${WORKDIR}/${TILE_ID}_buffer.gpkg"
    TILE_SHP="${WORKDIR}/${TILE_ID}.shp"
    TILE_OUT_SHP="${WORKDIR}/${TILE_ID}_out.shp"
    TILE_OUT_GPKG="${WORKDIR}/${TILE_ID}_out.gpkg"
    TILE_CORE_GPKG="${WORKDIR}/${TILE_ID}_core.gpkg"

    ##########################################################################
    # BUFFERREKO ELEMENTUAK ATERA
    ##########################################################################

    /usr/local/bin/ogr2ogr \
        -overwrite \
        "${TILE_GPKG}" \
        "${INPUT}" \
        "${INPUTB}" \
        -spat \
        ${BXMIN} \
        ${BYMIN} \
        ${BXMAX} \
        ${BYMAX}

    COUNT=$(/usr/local/bin/ogrinfo -so "${TILE_GPKG}" "${INPUTB}" 2>/dev/null \
        | awk '/Feature Count/ {print $3}')

    [ -z "${COUNT}" ] && COUNT=0

    if [ "${COUNT}" = "0" ]
    then
        echo "Tile hutsa"
        continue
    fi

    echo "Features: ${COUNT}"

    ##########################################################################
    # GPKG -> SHP
    ##########################################################################

    /usr/local/bin/ogr2ogr \
        -overwrite \
        "${TILE_SHP}" \
        "${TILE_GPKG}"

    ##########################################################################
    # GRASS
    ##########################################################################

    TILE_GRASS="${GISDBASE}/tile_${TILE_ID}"

    grass -c EPSG:25830 "${TILE_GRASS}" --exec bash -c "

        v.in.ogr \
            input='${TILE_SHP}' \
            output=landcover \
            snap=${SNAP_THRESHOLD} \
            --overwrite

        v.clean \
            input=landcover \
            output=landcover_rmarea \
            tool=rmarea \
            threshold=${AREA_THRESHOLD} \
            --overwrite

        v.build \
            map=landcover_rmarea

        v.generalize \
            input=landcover_rmarea \
            output=landcover_gen \
            method=douglas \
            threshold=50 \
            --overwrite

        v.build \
            map=landcover_gen

        v.out.ogr \
            input=landcover_gen \
            output='${TILE_OUT_SHP}' \
            format=ESRI_Shapefile \
            --overwrite
    "

    ##########################################################################
    # SHP -> GPKG
    ##########################################################################

    /usr/local/bin/ogr2ogr \
        -overwrite \
        -f GPKG \
        "${TILE_OUT_GPKG}" \
        "${TILE_OUT_SHP}" \
        -nln landcover

    ##########################################################################
    # ERDIKO TILEA BAKARRIK GORDE
    ##########################################################################

    /usr/local/bin/ogr2ogr \
        -overwrite \
        "${TILE_CORE_GPKG}" \
        "${TILE_OUT_GPKG}" \
        landcover \
        -clipsrc \
        ${TXMIN} \
        ${TYMIN} \
        ${TXMAX} \
        ${TYMAX}

    ##########################################################################
    # APPEND
    ##########################################################################

    if [ ${FIRST_TILE} -eq 1 ]
    then

        /usr/local/bin/ogr2ogr \
            -overwrite \
            -f GPKG \
            "${OUTPUT}" \
            "${TILE_CORE_GPKG}" \
            -nln merged

        FIRST_TILE=0

    else

        /usr/local/bin/ogr2ogr \
            -append \
            "${OUTPUT}" \
            "${TILE_CORE_GPKG}" \
            -nln merged

    fi

done
done

##############################################################################
# DISSOLVE
##############################################################################

echo
echo "Final dissolve..."

/usr/local/bin/ogr2ogr \
    -overwrite \
    -f GPKG \
    "${OUTPUT_DISS}" \
    "${OUTPUT}" \
    -dialect SQLITE \
    -sql "
        SELECT
            type,
            ST_Union(geom) AS geom
        FROM merged
        GROUP BY type
    " \
    -nln "${INPUTB}_lowzoom"

##############################################################################
# SPATIAL INDEX
##############################################################################

/usr/local/bin/ogrinfo "${OUTPUT_DISS}" \
    -sql "
        SELECT CreateSpatialIndex(
            '${INPUTB}_lowzoom',
            'geom'
        )
    " \
    >/dev/null 2>&1 || true

##############################################################################
# ESTATISTIKAK
##############################################################################

echo
echo "RESULT"

/usr/local/bin/ogrinfo -so \
    "${OUTPUT_DISS}" \
    "${INPUTB}_lowzoom"

echo
echo "DONE"
echo
echo "Output:"
echo "  ${OUTPUT_DISS}"

echo
echo "=================================================="
echo "END : $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

exit 0
