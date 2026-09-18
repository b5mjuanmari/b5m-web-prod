#!/usr/bin/env python3
"""
Shapefile bat irakurri eta GPKG bat sortu, atributu taula sinplifikatua duena.

Erabilera:
    vt_beach.py <sarrera.shp> <irteera.gpkg> [log_fitxategia]

- Sarrerako Shapefile-a existitzen dela egiaztatzen du.
- Irteerako GPKG-a existitzen bada, ezabatu egiten du.
- Irteerako geruzak bi eremu baino ez ditu: 'fid' (automatikoa) eta 'type'.
- 'type' eremua jatorrizko 'TIPO_E' eremutik eratortzen da:
    * 'hondartza_orogra'      -> 'beach'
    * 'marearteko hondartza'  -> 'intertidal beach'
- Beste balio guztiak baztertu egiten dira.
- Exekuzio denbora neurtzen du.
"""

import os
import sys
import time
from osgeo import ogr

from log_utils import Log


# TIPO_E -> type balioen mapaketa
TYPE_MAP = {
    "hondartza_orogra": "beach",
    "marearteko hondartza": "intertidal beach",
}


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

        # TIPO_E eremua existitzen dela egiaztatu
        src_defn = src_layer.GetLayerDefn()
        if src_defn.GetFieldIndex("TIPO_E") < 0:
            log.errorea(
                "Sarrerako geruzak ez du 'TIPO_E' eremurik."
            )
            sys.exit(1)

        # Irteerako GPKG-a sortu
        dst_driver = ogr.GetDriverByName("GPKG")
        dst_ds = dst_driver.CreateDataSource(dst_path)
        if dst_ds is None:
            log.errorea(f"Ezin izan da irteerako GPKG-a sortu: {dst_path}")
            sys.exit(1)

        # Geruza: fitxategiaren izena, .gpkg gabe
        layer_name = os.path.splitext(os.path.basename(dst_path))[0]
        dst_layer = dst_ds.CreateLayer(
            layer_name,
            srs=src_srs,
            geom_type=geom_type,
            options=["SPATIAL_INDEX=YES"],
        )
        if dst_layer is None:
            log.errorea(f"Ezin izan da '{layer_name}' geruza sortu.")
            sys.exit(1)

        # 'type' eremua
        type_field = ogr.FieldDefn("type", ogr.OFTString)
        type_field.SetWidth(64)
        dst_layer.CreateField(type_field)

        dst_defn = dst_layer.GetLayerDefn()
        dst_layer.StartTransaction()

        count_in = 0
        count_out = 0
        skipped = 0

        for src_feat in src_layer:
            count_in += 1

            tipo = src_feat.GetField("TIPO_E")
            if tipo is None:
                skipped += 1
                continue

            tipo_norm = tipo.strip()
            new_type = TYPE_MAP.get(tipo_norm)
            if new_type is None:
                skipped += 1
                continue

            geom = src_feat.GetGeometryRef()
            if geom is None:
                skipped += 1
                continue

            out_feat = ogr.Feature(dst_defn)
            out_feat.SetGeometry(geom.Clone())
            out_feat.SetField("type", new_type)

            if dst_layer.CreateFeature(out_feat) != ogr.OGRERR_NONE:
                log.abisua("Elementu bat ezin izan da idatzi.")
            else:
                count_out += 1

            out_feat = None

        dst_layer.CommitTransaction()

        dst_ds = None
        src_ds = None

        elapsed = time.time() - start_time
        log.info(f"Eginda. Denbora: {elapsed:.2f} segundo")
        log.info(f"  Sarrerako elementuak:  {count_in}")
        log.info(f"  Idatzitako elementuak: {count_out}")
        log.info(f"  Baztertutakoak:        {skipped}")
        log.info(f"Irteerako fitxategia: {dst_path}")
        log.info(f"Geruzaren izena: {layer_name}")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
