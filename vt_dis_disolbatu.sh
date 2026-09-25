#!/usr/bin/env bash
#
# vt_dis_disolbatu.sh
#
# GPKG fitxategi bateko poligonoak 'type' eremuaren arabera disolbatzen ditu,
# baina SOILIK TYPE jakin batzuetarako. Gainerako type-ak jatorrian bezala
# uzten dira (denbora aurrezteko).
#
# Erabilera:
#   ./vt_dis_disolbatu.sh <sarrera.gpkg> [log_fitxategia]
#
#   sarrera.gpkg    (derrigorrezkoa) Disolbatu beharreko GPKG fitxategia.
#                   Fitxategia existitzen dela egiaztatzen da.
#   log_fitxategia  (aukerakoa) Log fitxategiaren bidea. Ematen bada, mezu
#                   guztiak fitxategi horri gehituko zaizkio (ez da
#                   ezabatzen) eta terminalean EZ da ezer idatziko.
#                   Ez bada ematen, mezuak terminalera soilik.

set -euo pipefail

# ---------------------------------------------------------------------------
# Argumentuak
# ---------------------------------------------------------------------------

if [[ $# -lt 1 ]]; then
    echo "Erabilera: $(basename "$0") <sarrera.gpkg> [log_fitxategia]" >&2
    exit 1
fi

SARRERA="$1"
LOG_FITXATEGIA="${2:-}"

# ---------------------------------------------------------------------------
# Log sistema
# ---------------------------------------------------------------------------
# Log fitxategia ematen bada: mezuak fitxategira soilik (gehituz).
# Ez bada ematen: mezuak terminalera soilik.

log() {
    local mezua="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    if [[ -n "$LOG_FITXATEGIA" ]]; then
        echo "$mezua" >> "$LOG_FITXATEGIA"
    else
        echo "$mezua"
    fi
}

errorea() {
    local mezua="[$(date '+%Y-%m-%d %H:%M:%S')] ERROREA: $*"
    if [[ -n "$LOG_FITXATEGIA" ]]; then
        echo "$mezua" >> "$LOG_FITXATEGIA"
    else
        echo "$mezua" >&2
    fi
}

# Komandoak exekutatu, irteera log fitxategira edo terminalera birbideratuz.
exekutatu() {
    if [[ -n "$LOG_FITXATEGIA" ]]; then
        "$@" >> "$LOG_FITXATEGIA" 2>&1
    else
        "$@"
    fi
}

# ---------------------------------------------------------------------------
# Ezarpenak
# ---------------------------------------------------------------------------

SCRIPT_DISOLBATU="vt_disolbatu.py"
FIELD="type"

# Disolbatu nahi diren 'type' balioak.
DISOLBATU=(
    "beach"
    "intertidal"
    "intertidal beach"
    "marsh"
    "pond"
    "pool"
    "reservoir"
    "sea"
    "swimming pool"
    "water other"
)

# Bitarteko fitxategiak: sarrerako fitxategiaren karpeta berean, izen bereziak.
DAT_DIR="$(dirname "$SARRERA")"
TMP_DIS="${DAT_DIR}/vt_tmp_dis.gpkg"
TMP_DIS_OUT="${DAT_DIR}/vt_tmp_dis_out.gpkg"
TMP_REST="${DAT_DIR}/vt_tmp_rest.gpkg"
TMP_BATU="${DAT_DIR}/vt_tmp_batu.gpkg"

# ---------------------------------------------------------------------------
# Laguntza-funtzioak
# ---------------------------------------------------------------------------

garbitu() {
    rm -f "$TMP_DIS" "$TMP_DIS_OUT" "$TMP_REST" "$TMP_BATU"
}

# ---------------------------------------------------------------------------
# Hasierako egiazkoak
# ---------------------------------------------------------------------------

log "=== HASI: $(basename "$0") ==="
log "Argumentuak: $*"
log "Sarrera: $SARRERA"

if [[ ! -f "$SARRERA" ]]; then
    errorea "Sarrerako fitxategia ez da existitzen: $SARRERA"
    exit 1
fi

if [[ ! -f "$SCRIPT_DISOLBATU" ]]; then
    errorea "Ez da aurkitu: $SCRIPT_DISOLBATU"
    exit 1
fi

mkdir -p "$DAT_DIR"
garbitu

# ---------------------------------------------------------------------------
# 1. Disolbatu beharreko type-ak atera
# ---------------------------------------------------------------------------

where_dis=""
for balioa in "${DISOLBATU[@]}"; do
    balioa_esc="${balioa//\'/\'\'}"
    if [[ -z "$where_dis" ]]; then
        where_dis="\"${FIELD}\" = '${balioa_esc}'"
    else
        where_dis="${where_dis} OR \"${FIELD}\" = '${balioa_esc}'"
    fi
done

log "Disolbatu beharreko type-ak: ${DISOLBATU[*]}"
log "1/5 Disolbatu beharreko type-ak ateratzen..."

rm -f "$TMP_DIS"
exekutatu ogr2ogr -f GPKG "$TMP_DIS" "$SARRERA" \
    -sql "SELECT * FROM $(basename "${SARRERA%.gpkg}") WHERE ${where_dis}" \
    -nln "vt_tmp_dis"

# ---------------------------------------------------------------------------
# 2. Disolbatu
# ---------------------------------------------------------------------------

log "2/5 Disolbatzen (${SCRIPT_DISOLBATU})..."
rm -f "$TMP_DIS_OUT"
exekutatu python3 "$SCRIPT_DISOLBATU" "$TMP_DIS" "$TMP_DIS_OUT" "${LOG_FITXATEGIA:-}"

# ---------------------------------------------------------------------------
# 3. Gainerako type-ak atera (disolbatu gabe)
# ---------------------------------------------------------------------------

log "3/5 Gainerako type-ak ateratzen (disolbatu gabe)..."

where_rest="NOT (${where_dis})"

rm -f "$TMP_REST"
exekutatu ogr2ogr -f GPKG "$TMP_REST" "$SARRERA" \
    -dialect SQLITE \
    -sql "SELECT \"${FIELD}\", geom FROM $(basename "${SARRERA%.gpkg}") WHERE ${where_rest}" \
    -nln "vt_tmp_rest"

# ---------------------------------------------------------------------------
# 4. Dena batu
# ---------------------------------------------------------------------------

log "4/5 Disolbatuak eta gainerakoak batzen..."

rm -f "$TMP_BATU"
exekutatu ogr2ogr -f GPKG "$TMP_BATU" "$TMP_REST" -nln "vt_tmp_batu"
exekutatu ogr2ogr -update -append "$TMP_BATU" "$TMP_DIS_OUT" \
    -nln "vt_tmp_batu" \
    -sql "SELECT \"${FIELD}\", geom FROM vt_tmp_dis_out"

# ---------------------------------------------------------------------------
# 5. Azken fitxategia sortu
# ---------------------------------------------------------------------------

# Azken fitxategia: sarrerakoaren izen bera, baina '_dis' atzizkiarekin.
# Horrela, ez da jatorrizkoa gainidazten eta ez da babes-kopiarik behar.
IZEN_HUTSA="$(basename "${SARRERA%.gpkg}")"
IRTEERA="${DAT_DIR}/${IZEN_HUTSA}_dis.gpkg"

log "5/5 Azken fitxategia sortzen: $IRTEERA"
rm -f "$IRTEERA"
exekutatu ogr2ogr -f GPKG "$IRTEERA" "$TMP_BATU" -nln "$IZEN_HUTSA"

# ---------------------------------------------------------------------------
# Garbiketa
# ---------------------------------------------------------------------------

garbitu

log "Eginda: $IRTEERA"
log "=== AMAIERA ==="
