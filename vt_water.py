#!/usr/bin/env python3
"""
Shapefile bat irakurri eta GPKG bat sortu, atributu taula sinplifikatua duena.

Erabilera:
    script.py <sarrera.shp> <irteera.gpkg>

- Sarrerako Shapefile-a existitzen dela egiaztatzen du.
- Irteerako GPKG-a existitzen bada, ezabatu egiten du.
- Irteerako geruzak hiru eremu ditu: 'fid' (automatikoa), 'type' eta 'subtype'.
- 'type' eremua beti 'water' da.
- 'subtype' eremua jatorrizko 'SUBTIPO_E' eremutik eratortzen da:
    * 'baltsa'          -> 'pond'
    * 'bestelako ura'   -> 'water other'
    * 'igerilekuko ura' -> 'swimming pool'
    * 'itsasoa'         -> 'sea'
    * 'mareartekoa'     -> 'intertidal'
    * 'urmaela'         -> 'pool'
    * 'urtegia'         -> 'reservoir'
- Beste balio guztiak baztertu egiten dira.
- Exekuzio denbora neurtzen du.
"""

import os
import sys
import time
from osgeo import ogr


# SUBTIPO_E -> subtype balioen mapaketa
SUBTYPE_MAP = {
    "baltsa": "pond",
    "bestelako ura": "water other",
    "igerilekuko ura": "swimming pool",
    "itsasoa": "sea",
    "mareartekoa": "intertidal",
    "urmaela": "pool",
    "urtegia": "reservoir",
}

TYPE_VALUE = "water"


def main():
    script_name = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        print(f"Erabilera: {script_name} <sarrera.shp> <irteera.gpkg>", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    dst_path = sys.argv[2]

    # Sarrerako fitxategia egiaztatu
    if not os.path.isfile(src_path):
        print(f"Errorea: sarrerako fitxategia ez da existitzen: {src_path}", file=sys.stderr)
        sys.exit(1)

    # Irteerako fitxategia existitzen bada, ezabatu
    if os.path.exists(dst_path):
        try:
            os.remove(dst_path)
            print(f"Existitzen zen irteerako fitxategia ezabatu da: {dst_path}")
        except OSError as e:
            print(f"Errorea irteerako fitxategia ezabatzean: {e}", file=sys.stderr)
            sys.exit(1)

    start_time = time.time()

    # Sarrera ireki
    src_ds = ogr.Open(src_path, 0)
    if src_ds is None:
        print(f"Errorea: ezin izan da Shapefile-a ireki: {src_path}", file=sys.stderr)
        sys.exit(1)

    src_layer = src_ds.GetLayer(0)
    src_srs = src_layer.GetSpatialRef()
    geom_type = src_layer.GetGeomType()

    # SUBTIPO_E eremua existitzen dela egiaztatu
    src_defn = src_layer.GetLayerDefn()
    if src_defn.GetFieldIndex("SUBTIPO_E") < 0:
        print("Errorea: sarrerako geruzak ez du 'SUBTIPO_E' eremurik.", file=sys.stderr)
        sys.exit(1)

    # Irteerako GPKG-a sortu
    dst_driver = ogr.GetDriverByName("GPKG")
    dst_ds = dst_driver.CreateDataSource(dst_path)
    if dst_ds is None:
        print(f"Errorea: ezin izan da irteerako GPKG-a sortu: {dst_path}", file=sys.stderr)
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
        print(f"Errorea: ezin izan da '{layer_name}' geruza sortu.", file=sys.stderr)
        sys.exit(1)

    # 'type' eta 'subtype' eremuak
    type_field = ogr.FieldDefn("type", ogr.OFTString)
    type_field.SetWidth(32)
    dst_layer.CreateField(type_field)

    subtype_field = ogr.FieldDefn("subtype", ogr.OFTString)
    subtype_field.SetWidth(64)
    dst_layer.CreateField(subtype_field)

    dst_defn = dst_layer.GetLayerDefn()
    dst_layer.StartTransaction()

    count_in = 0
    count_out = 0
    skipped = 0

    for src_feat in src_layer:
        count_in += 1

        subtipo = src_feat.GetField("SUBTIPO_E")
        if subtipo is None:
            skipped += 1
            continue

        subtipo_norm = subtipo.strip()
        new_subtype = SUBTYPE_MAP.get(subtipo_norm)
        if new_subtype is None:
            skipped += 1
            continue

        geom = src_feat.GetGeometryRef()
        if geom is None:
            skipped += 1
            continue

        out_feat = ogr.Feature(dst_defn)
        out_feat.SetGeometry(geom.Clone())
        out_feat.SetField("type", TYPE_VALUE)
        out_feat.SetField("subtype", new_subtype)

        if dst_layer.CreateFeature(out_feat) != ogr.OGRERR_NONE:
            print("Abisua: elementu bat ezin izan da idatzi.", file=sys.stderr)
        else:
            count_out += 1

        out_feat = None

    dst_layer.CommitTransaction()

    dst_ds = None
    src_ds = None

    elapsed = time.time() - start_time
    print(f"Eginda. Denbora: {elapsed:.2f} segundo")
    print(f"  Sarrerako elementuak:  {count_in}")
    print(f"  Idatzitako elementuak: {count_out}")
    print(f"  Baztertutakoak:        {skipped}")
    print(f"Irteerako fitxategia: {dst_path}")
    print(f"Geruzaren izena: {layer_name}")


if __name__ == "__main__":
    main()
