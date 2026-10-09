#!/bin/bash

HOME="${HOME:-/home/juanmari}"
work="${HOME}/SCRIPTS/WEB_PROD"
gaur="$(date +"%Y%m%d")"
script=$(basename "$0" | sed 's/\..*$//')

##############################################################################
# ERABILERA
#
# ./vt_simplify.sh <gpkg_izena> [rmarea] [snap] [tile] [buffer] [douglas] [zutabea]
#
# PARAMETROAK
#
# $1 gpkg oinarrizko izena (= layer izena), ./dat/ barruan
# $2 rmarea threshold (m2)             [10000]
# $3 snap threshold (m)                [0.1]
# $4 tile tamaina (m)                  [5000]
# $5 buffer tamaina (m)                [3000]
# $6 Douglas-Peucker threshold (m)     [50]
# $7 disolbatzeko atributu-zutabea     [type]
#
# IRTEERA: ./dat/<gpkg>_<rmarea>_<snap>.gpkg
#          taularen izena = GPKG fitxategiaren izena, ".gpkg" gabe
##############################################################################

# Argumentuen egiaztapena LOGera birbideratu aurretik: errorea terminalean ikusteko
if [ $# -lt 1 ]; then
    echo "ERROREA: gpkg izena falta da" >&2
    echo "Erabilera: $0 <gpkg_izena> [rmarea] [snap] [tile] [buffer] [douglas] [zutabea]" >&2
    exit 1
fi

source ~/.bashrc
mkdir -p "${work}/log"
cd "${work}"

INPUTB=$(basename "${1}" .gpkg)
AREA_THRESHOLD="${2:-10000}"
SNAP_THRESHOLD="${3:-0.1}"
TILE_SIZE="${4:-5000}"
BUFFER_SIZE="${5:-3000}"
SIMPLIFY_THRESHOLD="${6:-50}"
GROUP_COL="${7:-type}"

SNAP_TAG="${SNAP_THRESHOLD//./}"

INPUT="./dat/${INPUTB}.gpkg"
OUTPUT_MERGED="./dat/${INPUTB}_merged_tmp.gpkg"
OUTPUT="./dat/${INPUTB}_${AREA_THRESHOLD}_${SNAP_TAG}_${SIMPLIFY_THRESHOLD}.gpkg"
OUTPUT_TABLE="$(basename "${OUTPUT}" .gpkg)"

if [ ! -f "${INPUT}" ]; then
    echo "ERROREA: ez da aurkitu ${INPUT}" >&2
    exit 1
fi

LOG_FILE="./log/${script}_${gaur}.log"
rm -f "${LOG_FILE}" 2> /dev/null

exec >> "${LOG_FILE}" 2>&1

echo "=================================================="
echo "START : $(date '+%Y-%m-%d %H:%M:%S')"
echo "SCRIPT: ${script}"
echo "LOG   : ${LOG_FILE}"
echo "=================================================="
echo

set -euo pipefail
trap 'echo "ERROREA: ${LINENO}. lerroan huts egin du (irteera-kodea $?)"' ERR

GRASS_BIN="${GRASS_BIN:-grass74}"
OGR2OGR=/usr/local/bin/ogr2ogr
OGRINFO=/usr/local/bin/ogrinfo

# GRASS: ehunekozko progresioa ez idatzi logean
export GRASS_MESSAGE_FORMAT=plain

# -makevalid GDAL 3.x-tik aurrera dago bakarrik
MAKEVALID_OPT=""
if "${OGR2OGR}" --help-general 2>&1 | grep -q -- "-makevalid" \
   || "${OGR2OGR}" --long-usage 2>&1 | grep -q -- "-makevalid"; then
    MAKEVALID_OPT="-makevalid"
fi

##############################################################################

WORKDIR=$(mktemp -d)
GISDBASE=$(mktemp -d)

cleanup() {
    echo "Cleaning up..."
    rm -rf "${WORKDIR}" "${GISDBASE}"
    rm -f "${OUTPUT_MERGED}"
}

trap cleanup EXIT

##############################################################################
# GRASS barruko tile-prozesamendua (script bereizia: ez dago export -f arazorik)
##############################################################################

TILE_SCRIPT="${WORKDIR}/process_tile.sh"

cat > "${TILE_SCRIPT}" <<'EOF'
#!/bin/bash
set -euo pipefail

IN_SHP="${1}"
OUT_SHP="${2}"
SNAP="${3}"
AREA="${4}"
SIMPL="${5}"

v.in.ogr input="${IN_SHP}" output=landcover \
    snap="${SNAP}" --overwrite --quiet

v.clean input=landcover output=landcover_rmarea \
    tool=rmarea threshold="${AREA}" --overwrite --quiet

v.generalize input=landcover_rmarea output=landcover_gen \
    method=douglas threshold="${SIMPL}" --overwrite --quiet

v.out.ogr input=landcover_gen type=area output="${OUT_SHP}" \
    format=ESRI_Shapefile --overwrite --quiet
EOF

chmod +x "${TILE_SCRIPT}"

##############################################################################
# EXTENT (tesela-sare globalari lerrokatua: TILE_SIZE-ren multiploak)
##############################################################################

EXTENT=$(${OGRINFO} -so "${INPUT}" "${INPUTB}" |
    grep "Extent:" |
    sed -E 's/.*Extent: \(([^,]+), ([^)]+)\) - \(([^,]+), ([^)]+)\).*/\1 \2 \3 \4/' || true)

if [ -z "${EXTENT}" ]; then
    echo "ERROREA: ezin izan da Extent irakurri (${INPUT}, layer: ${INPUTB})"
    exit 1
fi

read XMIN YMIN XMAX YMAX < <(
    echo "${EXTENT}" | awk -v t="${TILE_SIZE}" '
        function floor(x) { return (x == int(x)) ? x : (x < 0 ? int(x) - 1 : int(x)) }
        function ceil(x)  { return (x == int(x)) ? x : (x < 0 ? int(x) : int(x) + 1) }
        { printf "%.0f %.0f %.0f %.0f\n",
            floor($1 / t) * t, floor($2 / t) * t,
            ceil($3 / t) * t,  ceil($4 / t) * t }'
)

echo
echo "INPUT            : ${INPUT}"
echo "AREA_THRESHOLD   : ${AREA_THRESHOLD}"
echo "SNAP_THRESHOLD   : ${SNAP_THRESHOLD}"
echo "TILE_SIZE        : ${TILE_SIZE}"
echo "BUFFER_SIZE      : ${BUFFER_SIZE}"
echo "DOUGLAS          : ${SIMPLIFY_THRESHOLD}"
echo "GROUP_COL        : ${GROUP_COL}"
echo "EXTENT (lerrok.) : ${XMIN} ${YMIN} ${XMAX} ${YMAX}"
echo "OUTPUT           : ${OUTPUT}"
echo "OUTPUT TABLE     : ${OUTPUT_TABLE}"
echo "MAKEVALID        : ${MAKEVALID_OPT:-ez}"
echo

##############################################################################
# GARBITU AURREKO EMAITZAK
##############################################################################

rm -f "${OUTPUT_MERGED}" "${OUTPUT}"

FIRST_TILE=1

# Tesela kopuru osoa (extent-a TILE_SIZE-ra lerrokatuta dago) eta kontagailua
TOTAL_TILES=$(( ((XMAX - XMIN) / TILE_SIZE) * ((YMAX - YMIN) / TILE_SIZE) ))
TILE_N=0

echo "TESELA KOPURUA   : ${TOTAL_TILES}"

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
    TILE_N=$((TILE_N + 1))

    echo
    echo "=================================================="
    echo "Tile ${TILE_N}/${TOTAL_TILES}  (${TILE_ID})  $(date '+%H:%M:%S')"
    echo "=================================================="

    TILE_GPKG="${WORKDIR}/${TILE_ID}_buffer.gpkg"
    TILE_SHP="${WORKDIR}/${TILE_ID}.shp"
    TILE_OUT_SHP="${WORKDIR}/${TILE_ID}_out.shp"
    TILE_OUT_GPKG="${WORKDIR}/${TILE_ID}_out.gpkg"
    TILE_GRASS="${GISDBASE}/tile_${TILE_ID}"

    # Bufferreko elementuak atera
    ${OGR2OGR} -overwrite \
        "${TILE_GPKG}" "${INPUT}" "${INPUTB}" \
        -spat ${BXMIN} ${BYMIN} ${BXMAX} ${BYMAX}

    COUNT=$(${OGRINFO} -so "${TILE_GPKG}" "${INPUTB}" 2>/dev/null \
        | awk '/Feature Count/ {print $3}' || true)

    [ -z "${COUNT}" ] && COUNT=0

    if [ "${COUNT}" = "0" ]; then
        echo "Tile hutsa"
        rm -rf "${WORKDIR}/${TILE_ID}"*
        continue
    fi

    echo "Features: ${COUNT}"

    # GPKG -> SHP (grass74-ren GDAL-ek ezin du GPKG ireki)
    ${OGR2OGR} -overwrite -lco ENCODING=UTF-8 \
        "${TILE_SHP}" "${TILE_GPKG}"

    "${GRASS_BIN}" -c EPSG:25830 "${TILE_GRASS}" --exec \
        bash "${TILE_SCRIPT}" \
            "${TILE_SHP}" "${TILE_OUT_SHP}" \
            "${SNAP_THRESHOLD}" "${AREA_THRESHOLD}" "${SIMPLIFY_THRESHOLD}"

    # SHP -> GPKG
    ${OGR2OGR} -overwrite -f GPKG \
        "${TILE_OUT_GPKG}" "${TILE_OUT_SHP}" -nln landcover

    # Nukleoa bakarrik gorde eta zuzenean batutakora gehitu
    if [ ${FIRST_TILE} -eq 1 ]; then
        WRITE_MODE="-overwrite"
    else
        WRITE_MODE="-append"
    fi

    ${OGR2OGR} ${WRITE_MODE} -f GPKG \
        "${OUTPUT_MERGED}" "${TILE_OUT_GPKG}" landcover \
        -clipsrc ${TXMIN} ${TYMIN} ${TXMAX} ${TYMAX} \
        -nlt MULTIPOLYGON ${MAKEVALID_OPT} \
        -nln merged

    FIRST_TILE=0

    # Tesela honen tarteko fitxategiak eta GRASS location-a garbitu
    rm -rf "${TILE_GRASS}" "${WORKDIR}/${TILE_ID}"*

done
done

if [ ${FIRST_TILE} -eq 1 ]; then
    echo "ERROREA: ez da tesela baliodunik sortu"
    exit 1
fi

##############################################################################
# DISSOLVE -> GPKG BAKARRA (taula-izena = GPKG izena, .gpkg gabe)
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
            \"${GROUP_COL}\",
            ST_Multi(ST_UnaryUnion(ST_Collect(geom))) AS geom
        FROM merged
        GROUP BY \"${GROUP_COL}\"
    " \
    -nlt MULTIPOLYGON \
    -nln "${OUTPUT_TABLE}"

##############################################################################
# GARBIKETA (END mezuaren aurretik, azken lerroa END izan dadin)
##############################################################################

cleanup
trap - EXIT

##############################################################################
# ESTATISTIKAK
##############################################################################

echo
echo "RESULT"

${OGRINFO} -so "${OUTPUT}" "${OUTPUT_TABLE}"

echo
echo "DONE"
echo
echo "Output:"
echo "  ${OUTPUT}  (taula: ${OUTPUT_TABLE})"

echo
echo "=================================================="
echo "END : $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

exit 0
