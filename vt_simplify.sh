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
echo "SCRIPT: ${script}"
echo "LOG   : ${LOG_FILE}"
echo "=================================================="
echo

set -euo pipefail

##############################################################################
# ERABILERA
#
# ./vt_simplify.sh <gpkg_oinarrizko_izena> [rmarea] [snap] [tile] [buffer]
##############################################################################

INPUTB=$(basename "${1}" .gpkg)
AREA_THRESHOLD="${2:-10000}"
SNAP_THRESHOLD="${3:-0.1}"
TILE_SIZE="${4:-5000}"
BUFFER_SIZE="${5:-3000}"

# Izen berria: punturik gabe
SNAP_NODOT=$(echo "${SNAP_THRESHOLD}" | tr -d '.')

INPUT="./dat/${INPUTB}.gpkg"
OUTPUT_MERGED="./dat/${INPUTB}_merged_tmp.gpkg"
OUTPUT="./dat/${INPUTB}_${AREA_THRESHOLD}_${SNAP_NODOT}.gpkg"

if [ ! -f "${INPUT}" ]; then
    echo "ERROR: Ez da aurkitu ${INPUT}"
    exit 1
fi

GRASS_BIN="${GRASS_BIN:-grass74}"

OGR2OGR=/usr/local/bin/ogr2ogr
OGRINFO=/usr/local/bin/ogrinfo

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
# GRASS barruko tile-prozesamendua
##############################################################################

process_tile() {
    TILE_SHP="${1}"
    TILE_OUT_SHP="${2}"
    SNAP_THRESHOLD="${3}"
    AREA_THRESHOLD="${4}"

    v.in.ogr input="${TILE_SHP}" output=landcover \
        snap="${SNAP_THRESHOLD}" --overwrite

    v.clean input=landcover output=landcover_rmarea \
        tool=rmarea threshold="${AREA_THRESHOLD}" --overwrite

    v.build map=landcover_rmarea

    v.generalize input=landcover_rmarea output=landcover_gen \
        method=douglas threshold=50 --overwrite

    v.build map=landcover_gen

    v.out.ogr input=landcover_gen output="${TILE_OUT_SHP}" \
        format=ESRI_Shapefile --overwrite
}

export -f process_tile

##############################################################################
# EXTENT
##############################################################################

EXTENT=$(${OGRINFO} -so "${INPUT}" "${INPUTB}" |
grep "Extent:" |
sed -E 's/Extent: \(([^,]+), ([^)]+)\) - \(([^,]+), ([^)]+)\)/\1 \2 \3 \4/')

if [ -z "${EXTENT}" ]; then
    echo "ERROR: Ez da Extent irakurri ahal izan ${INPUT} fitxaitik"
    exit 1
fi

read XMIN YMIN XMAX YMAX <<< "${EXTENT}"

XMIN=${XMIN%.*}
YMIN=${YMIN%.*}
XMAX=${XMAX%.*}
YMAX=${YMAX%.*}

echo
echo "INPUT            : ${INPUT}"
echo "AREA_THRESHOLD   : ${AREA_THRESHOLD}"
echo "SNAP_THRESHOLD   : ${SNAP_THRESHOLD}"
echo "TILE_SIZE        : ${TILE_SIZE}"
echo "BUFFER_SIZE      : ${BUFFER_SIZE}"
echo "OUTPUT           : ${OUTPUT}"
echo

##############################################################################
# GARBITU AURREKO EMAITZAK
##############################################################################

rm -f "${OUTPUT_MERGED}"
rm -f "${OUTPUT}"

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

    ${OGR2OGR} -overwrite \
        "${TILE_GPKG}" "${INPUT}" "${INPUTB}" \
        -spat ${BXMIN} ${BYMIN} ${BXMAX} ${BYMAX}

    COUNT=$(${OGRINFO} -so "${TILE_GPKG}" "${INPUTB}" 2>/dev/null \
        | awk '/Feature Count/ {print $3}')

    [ -z "${COUNT}" ] && COUNT=0

    if [ "${COUNT}" = "0" ]; then
        echo "Tile hutsa"
        continue
    fi

    echo "Features: ${COUNT}"

    ${OGR2OGR} -overwrite -lco ENCODING=UTF-8 \
        "${TILE_SHP}" "${TILE_GPKG}"

    TILE_GRASS="${GISDBASE}/tile_${TILE_ID}"

    "${GRASS_BIN}" -c EPSG:25830 "${TILE_GRASS}" --exec \
        bash -c "process_tile '${TILE_SHP}' '${TILE_OUT_SHP}' '${SNAP_THRESHOLD}' '${AREA_THRESHOLD}'"

    ${OGR2OGR} -overwrite -f GPKG \
        "${TILE_OUT_GPKG}" "${TILE_OUT_SHP}" -nln landcover

    ${OGR2OGR} -overwrite \
        "${TILE_CORE_GPKG}" "${TILE_OUT_GPKG}" landcover \
        -clipsrc ${TXMIN} ${TYMIN} ${TXMAX} ${TYMAX}

    if [ ${FIRST_TILE} -eq 1 ]; then
        ${OGR2OGR} -overwrite -f GPKG \
            "${OUTPUT_MERGED}" "${TILE_CORE_GPKG}" -nln merged
        FIRST_TILE=0
    else
        ${OGR2OGR} -append \
            "${OUTPUT_MERGED}" "${TILE_CORE_GPKG}" -nln merged
    fi

done
done

##############################################################################
# DISSOLVE -> GPKG BAKARRA
##############################################################################

echo
echo "Final dissolve..."

${OGR2OGR} \
    -overwrite \
    -f GPKG \
    "${OUTPUT}" \
    "${OUTPUT_MERGED}" \
    -dialect SQLITE \
    -sql "
        SELECT
            type,
            ST_Union(geom) AS geom
        FROM merged
        GROUP BY type
    " \
    -nln "${INPUTB}"

##############################################################################
# SPATIAL INDEX
##############################################################################

${OGRINFO} "${OUTPUT}" \
    -sql "
        SELECT CreateSpatialIndex(
            '${INPUTB}',
            'geom'
        )
    " \
    >/dev/null 2>&1 || true

##############################################################################
# AMAIERA: garbitu eta END azken mezua
##############################################################################

rm -f "${OUTPUT_MERGED}"

cleanup
trap - EXIT          # trap-a desaktibatu: ez da berriz exekutatuko

echo
echo "RESULT"

${OGRINFO} -so "${OUTPUT}" "${INPUTB}"

echo
echo "DONE"
echo
echo "Output:"
echo "  ${OUTPUT}"

echo
echo "=================================================="
echo "END : $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

exit 0
