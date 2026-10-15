#!/usr/bin/env bash
set -euo pipefail

# Erabilera: ./filtroa.sh sarrera.gpkg irteera.gpkg
IN="${1:?Erabilera: $0 sarrera.gpkg irteera.gpkg}"
OUT="${2:?Erabilera: $0 sarrera.gpkg irteera.gpkg}"
WHERE="type = 'artificial'"

rm -f "$OUT"

layers=$(ogrinfo -ro "$IN" | grep -E '^[0-9]+: ' | cut -d: -f2- | sed -E 's/ \(.*\)$//')

for layer in $layers; do
    # layer_styles: kopiatu osorik, filtrorik gabe, eta jarraitu
    if [[ "$layer" == "layer_styles" ]]; then
        echo ">> $layer: estilo-taula, oso-osorik kopiatzen..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -nln "$layer"
        continue
    fi

    if ogrinfo -so -ro "$IN" "$layer" | grep -qi '^type:'; then
        echo ">> $layer: filtroa aplikatzen..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -where "$WHERE" -nln "$layer"
    else
        echo ">> $layer: 'type' eremurik ez, oso-osorik kopiatzen..."
        ogr2ogr -f GPKG -update -append "$OUT" "$IN" "$layer" -nln "$layer"
    fi
done

echo "Eginda: $OUT"
