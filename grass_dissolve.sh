#!/bin/bash
#
# Erabilera: ./grass_dissolve.sh <gpkg_sarrera> <gpkg_irteera>
#
# GPKG-a shapefile-ra bihurtu, GRASS-era inportatu, 'type' eremuaren
# arabera disolbatu, SHP-ra esportatu eta GPKG-ra bihurtu.

set -e

GPKG_SARRERA="$1"
GPKG_IRTEERA="$2"

if [ -z "$GPKG_SARRERA" ] || [ -z "$GPKG_IRTEERA" ]; then
    echo "Erabilera: $0 <gpkg_sarrera> <gpkg_irteera>"
    exit 1
fi

if [ ! -f "$GPKG_SARRERA" ]; then
    echo "Errorea: sarrera-fitxategia ez da existitzen: $GPKG_SARRERA"
    exit 1
fi

SARRERA_IZENA=$(basename "$GPKG_SARRERA" .gpkg)
IRTEERA_IZENA=$(basename "$GPKG_IRTEERA" .gpkg)
SARRERA_ABSOLUTUA=$(realpath "$GPKG_SARRERA")
IRTEERA_ABSOLUTUA=$(realpath -m "$GPKG_IRTEERA")

# Sarrera GPKG-aren EPSG kodea detektatu (azken ID["EPSG",XXXXX] proiektatutako CRS-a da)
SRS_KODEA=$(ogrinfo -so -al "$SARRERA_ABSOLUTUA" | grep -oP 'ID\["EPSG",\K[0-9]+' | tail -1)

if [ -z "$SRS_KODEA" ]; then
    echo "Abisua: ezin izan da EPSG kodea detektatu. EPSG:25830 erabiliko da lehenespenez."
    SRS_KODEA=25830
fi

echo "Sarrera SRS: EPSG:$SRS_KODEA"

# Behin-behineko direktorioak
TMPDIR=$(mktemp -d /tmp/grass_dissolve_XXXXXX)
SHP_DIR="$TMPDIR/shp_in"
SHP_OUT_DIR="$TMPDIR/shp_out"
GRASSDATA="$TMPDIR/grassdata"
LOCATION="temp_loc"

mkdir -p "$SHP_DIR" "$SHP_OUT_DIR"

trap "rm -rf $TMPDIR" EXIT

echo "=== GRASS dissolve prozesua (GPKG -> SHP -> GRASS -> SHP -> GPKG) ==="
echo "Sarrera: $SARRERA_ABSOLUTUA"
echo "Irteera: $IRTEERA_ABSOLUTUA"
echo ""

# Denbora kontagailuak
T_OSO_HASIERA=$(date +%s.%N)

# ------------------------------------------------------------
# 0. FASEA: GPKG-a shapefile-ra bihurtu (ogr2ogr-ekin)
# ------------------------------------------------------------
echo "[0/5] GPKG-a shapefile-ra bihurtzen..."
T_INI=$(date +%s.%N)
ogr2ogr -f "ESRI Shapefile" "$SHP_DIR" "$SARRERA_ABSOLUTUA" "$SARRERA_IZENA"
T_IRAUPENA=$(echo "$(date +%s.%N) - $T_INI" | bc)
echo "      -> ${T_IRAUPENA} s"
echo ""

# ------------------------------------------------------------
# GRASS script-a prestatu
# ------------------------------------------------------------
TMPSCRIPT=$(mktemp /tmp/grass_inner_XXXXXX.sh)

cat > "$TMPSCRIPT" << EOF
#!/bin/bash
set -e

SHP_BIDEA="$SHP_DIR/$SARRERA_IZENA.shp"

T0=\$(date +%s.%N)

echo "[1/5] Shapefile-a GRASS-era inportatzen..."
T_INI=\$(date +%s.%N)
v.in.ogr input="\$SHP_BIDEA" output="temp_import" snap=1e-08 --overwrite
T_IRAUPENA=\$(echo "\$(date +%s.%N) - \$T_INI" | bc)
echo "      -> \${T_IRAUPENA} s"

echo "[2/5] 'type' eremuaren arabera disolbatzen..."
T_INI=\$(date +%s.%N)
v.dissolve input="temp_import" column="type" output="temp_dissolved" --overwrite
T_IRAUPENA=\$(echo "\$(date +%s.%N) - \$T_INI" | bc)
echo "      -> \${T_IRAUPENA} s"

echo "[3/5] Shapefile-ra esportatzen (behin-behinekoa)..."
T_INI=\$(date +%s.%N)
v.out.ogr input="temp_dissolved" type="area" output="$SHP_OUT_DIR/temp_dissolved.shp" format="ESRI_Shapefile" --overwrite
T_IRAUPENA=\$(echo "\$(date +%s.%N) - \$T_INI" | bc)
echo "      -> \${T_IRAUPENA} s"

T_TOTALA=\$(echo "\$(date +%s.%N) - \$T0" | bc)
echo ""
echo "GRASS barneko denbora totala: \${T_TOTALA} s"
EOF

chmod +x "$TMPSCRIPT"

export GRASS_VECTOR_LOWMEM=1
export OGR_SQLITE_CACHE=1024

# ------------------------------------------------------------
# 1-3. FASEAK: GRASS barnean
# ------------------------------------------------------------
grass -c EPSG:$SRS_KODEA -e "$GRASSDATA/$LOCATION" --exec bash "$TMPSCRIPT"

# ------------------------------------------------------------
# 4. FASEA: SHP-a GPKG-ra bihurtu eta layer izena jarri
# ------------------------------------------------------------
echo ""
echo "[4/5] SHP-a GPKG-ra bihurtzen..."
T_INI=$(date +%s.%N)

# Irteera zaharra ezabatu
rm -f "$IRTEERA_ABSOLUTUA"

ogr2ogr -f "GPKG" \
    -nln "$IRTEERA_IZENA" \
    -nlt MULTIPOLYGON \
    -lco GEOMETRY_NAME=geom \
    -lco SPATIAL_INDEX=YES \
    "$IRTEERA_ABSOLUTUA" \
    "$SHP_OUT_DIR/temp_dissolved.shp"

T_IRAUPENA=$(echo "$(date +%s.%N) - $T_INI" | bc)
echo "      -> ${T_IRAUPENA} s"

T_OSO_AMAiera=$(date +%s.%N)
T_OSO_TOTALA=$(echo "$T_OSO_AMAiera - $T_OSO_HASIERA" | bc)

echo ""
echo "GPKG sortuta: $IRTEERA_ABSOLUTUA"
echo "Prozesu osoko denbora: ${T_OSO_TOTALA} s"
