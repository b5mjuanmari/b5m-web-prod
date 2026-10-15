#!/usr/bin/env bash
#
# filtroa.sh
#
# Deskribapena:
#   Sarrerako GeoPackage (GPKG) batetik irteerako GPKG berri bat sortzen du.
#   'type' eremua duten geruzetan hautaketa-filtro bat aplikatzen da
#   (lehenespenez: type = 'artificial'); eremurik ez duten geruzak
#   oso-osorik kopiatzen dira. 'layer_styles' taula beti kopiatzen da
#   osorik, filtrorik gabe (beti existitzen bada).
#
# Erabilera:
#   ./filtroa.sh sarrera.gpkg irteera.gpkg
#
# Menpekotasunak:
#   - GDAL/OGR: ogrinfo, ogr2ogr
#
set -euo pipefail

# ---------------------------------------------------------------------
# Parametroak
# ---------------------------------------------------------------------
IN="${1:?Erabilera: $0 sarrera.gpkg irteera.gpkg}"     # Sarrerako GPKG
OUT="${2:?Erabilera: $0 sarrera.gpkg irteera.gpkg}"   # Irteerako GPKG

# Aplikatu beharreko hautaketa-filtroa
WHERE="type = 'artificial'"

# ---------------------------------------------------------------------
# Prestaketa: irteerako fitxategi zaharra kendu, badago
# ---------------------------------------------------------------------
rm -f "$OUT"

# ---------------------------------------------------------------------
# Geruza-zerrenda lortu
#   ogrinfo-ren irteera honelakoa da:
#     1: geruza_izena (Polygon)
#   Beraz: 'N: ' aurrizkia kendu (cut) eta amaierako '( ... )'
#   geometria-mota ere bai (sed).
# ---------------------------------------------------------------------
layers=$(ogrinfo -ro "$IN" | grep -E '^[0-9]+: ' | cut -d: -f2- | sed -E 's/ \(.*\)$//')

# ---------------------------------------------------------------------
# Geruza bakoitza prozesatu
# ---------------------------------------------------------------------
for layer in $layers; do

    # --- layer_styles: estilo-taula, beti kopiatu osorik -------------
    if [[ "$layer" == "layer_styles" ]]; then
        echo "[$(date +%T)] >> $layer: estilo-taula, oso-osorik kopiatzen..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -nln "$layer"
        continue
    fi

    # --- 'type' eremua duen ala ez begiratu --------------------------
    if ogrinfo -so -ro "$IN" "$layer" | grep -qi '^type:'; then
        # Eremua badago: hautaketa-filtroa aplikatu
        echo "[$(date +%T)] >> $layer: filtroa aplikatzen ($WHERE)..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -where "$WHERE" -nln "$layer"
    else
        # Eremurik ez: geruza osoa kopiatu
        echo "[$(date +%T)] >> $layer: 'type' eremurik ez, oso-osorik kopiatzen..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -nln "$layer"
    fi
done

# ---------------------------------------------------------------------
# Bukaera
# ---------------------------------------------------------------------
echo "[$(date +%T)] Eginda: $OUT"

exit 0
