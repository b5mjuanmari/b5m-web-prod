#!/usr/bin/env python3
"""
Shapefile bat irakurri, geometria guztiak batu (disoluzioa) eta GPKG bat sortu.

Erabilera:
    vt_other.py <sarrera.shp> <irteera.gpkg> [log_fitxategia]

- Sarrerako Shapefile-a existitzen dela egiaztatzen du.
- Irteerako GPKG-a existitzen bada, ezabatu egiten du.
- Geometria guztiak bateratu egiten ditu (union), baliogabeak konponduz.
- Irteerako geruzak bi eremu ditu: 'fid' (automatikoa) eta 'type'.
- 'type' eremua beti 'other' da.
- Exekuzio denbora neurtzen du.
"""

import os
import sys
import time
from osgeo import ogr

from log_utils import Log


def main():
    script_name = os.path.basename(sys.argv[0])

    # --- Argumentuak egiaztatu ---
    if len(sys.argv) not in (3, 4):
        print(
            f"Erabilera: {script_name} <sarrera.shp> <irteera.gpkg> "
            f"[log_fitxategia]",
            file=sys.stderr,
        )
        sys.exit(1)

    src_path = sys.argv[1]
    dst_path = sys.argv[2]
    log_path = sys.argv[3] if len(sys.argv) == 4 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, script_name, sys.argv[1:])

    try:
        # Irteerako geruzaren izena: fitxategiaren basename-a, .gpkg gabe
        layer_name = os.path.splitext(os.path.basename(dst_path))[0]

        # Sarrerako fitxategia egiaztatu
        if not os.path.isfile(src_path):
            log.errorea(
                f"Sarrerako fitxategia ez da existitzen: {src_path}"
            )
            sys.exit(1)

        # Irteerako fitxategia existitzen bada, ezabatu
        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
                log.info(
                    f"Existitzen zen irteerako fitxategia ezabatu da: "
                    f"{dst_path}"
                )
            except OSError as e:
                log.errorea(
                    f"Ezin izan da irteerako fitxategia ezabatu: {e}"
                )
                sys.exit(1)

        start_time = time.time()

        # Sarrera ireki
        src_ds = ogr.Open(src_path, 0)
        if src_ds is None:
            log.errorea(f"Ezin izan da Shapefile-a ireki: {src_path}")
            sys.exit(1)

        src_layer = src_ds.GetLayer(0)
        src_srs = src_layer.GetSpatialRef()
        geom_type = src_layer.GetGeomType()

        # Geometria guztiak batu (disoluzioa)
        log.info("Geometriak batzen...")
        union_geom = None
        count = 0
        for feat in src_layer:
            g = feat.GetGeometryRef()
            if g is None:
                continue
            g = g.Clone()
            if not g.IsValid():
                g = g.MakeValid()
            if union_geom is None:
                union_geom = g
            else:
                union_geom = union_geom.Union(g)
            count += 1
            if count % 1000 == 0:
                log.info(f"  {count} elementu prozesatuta...")

        log.info(f"  {count} elementu batu dira guztira.")

        if union_geom is None:
            log.errorea("Ez da geometriarik aurkitu.")
            sys.exit(1)

        # Irteerako GPKG-a sortu
        dst_driver = ogr.GetDriverByName("GPKG")
        dst_ds = dst_driver.CreateDataSource(dst_path)
        if dst_ds is None:
            log.errorea(f"Ezin izan da irteerako GPKG-a sortu: {dst_path}")
            sys.exit(1)

        # Geruza: izena fitxategiarena (.gpkg gabe)
        final_layer = dst_ds.CreateLayer(
            layer_name,
            srs=src_srs,
            geom_type=union_geom.GetGeometryType(),
            options=["SPATIAL_INDEX=YES"],
        )
        if final_layer is None:
            log.errorea(f"Ezin izan da '{layer_name}' geruza sortu.")
            sys.exit(1)

        # 'type' eremua
        final_layer.CreateField(ogr.FieldDefn("type", ogr.OFTString))

        # Elementu bakarra idatzi
        feat = ogr.Feature(final_layer.GetLayerDefn())
        feat.SetGeometry(union_geom)
        feat.SetField("type", "other")
        final_layer.CreateFeature(feat)
        feat = None

        dst_ds = None
        src_ds = None

        elapsed = time.time() - start_time
        log.info(f"Eginda. Denbora: {elapsed:.2f} segundo")
        log.info(f"Irteerako fitxategia: {dst_path}")
        log.info(f"Geruzaren izena: {layer_name}")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
