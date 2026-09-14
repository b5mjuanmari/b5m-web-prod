#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poligono Shapefile guztiak (azpikarpetak barne) GPKG fitxategi bakar batean fusionatu.

Erabilera:
    python script.py <shapefile_karpeta> <gpkg_bidea>
"""

import os
import sys
import time
from osgeo import ogr


def main():
    script_izena = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        print(f"Erabilera: python {script_izena} <shapefile_karpeta> <gpkg_bidea>")
        sys.exit(1)

    karpeta = sys.argv[1]
    gpkg_bidea = sys.argv[2]

    if not os.path.isdir(karpeta):
        print(f"Errorea: '{karpeta}' ez da karpeta baliogarri bat.")
        sys.exit(1)

    # GPKG-a ezabatu aurretik badago
    if os.path.exists(gpkg_bidea):
        os.remove(gpkg_bidea)
        print(f"Aurreko GPKG ezabatu da: {gpkg_bidea}")

    # Shapefile guztiak bilatu (azpikarpetak barne)
    shp_zerrenda = []
    for erroa, _, fitxategiak in os.walk(karpeta):
        for fitxategia in fitxategiak:
            if fitxategia.lower().endswith(".shp"):
                shp_zerrenda.append(os.path.join(erroa, fitxategia))

    if not shp_zerrenda:
        print("Ez da Shapefile-ik aurkitu.")
        sys.exit(0)

    print(f"{len(shp_zerrenda)} Shapefile aurkitu dira.\n")

    # GPKG driver-a
    driver = ogr.GetDriverByName("GPKG")
    if driver is None:
        print("Errorea: GPKG driver-a ez dago erabilgarri.")
        sys.exit(1)

    # GPKG-a sortu
    ds_out = driver.CreateDataSource(gpkg_bidea)
    if ds_out is None:
        print(f"Errorea: ezin izan da GPKG-a sortu: {gpkg_bidea}")
        sys.exit(1)

    layer_out = None

    denbora_totala_hasiera = time.time()

    for idx, shp_bidea in enumerate(shp_zerrenda, 1):
        hasiera = time.time()
        shp_izena = os.path.basename(shp_bidea)
        izen_garbia = os.path.splitext(shp_izena)[0]

        # 'type' balioa: lehenengo bi hizkiak kendu
        if len(izen_garbia) > 2:
            type_balioa = izen_garbia[2:]
        else:
            type_balioa = izen_garbia

        print(f"[{idx}/{len(shp_zerrenda)}] {shp_izena} -> type='{type_balioa}'")

        ds_in = ogr.Open(shp_bidea, 0)
        if ds_in is None:
            print(f"  Abisua: ezin izan da ireki: {shp_bidea}")
            continue

        layer_in = ds_in.GetLayer(0)
        if layer_in is None:
            print(f"  Abisua: ez du layer-ik: {shp_bidea}")
            ds_in = None
            continue

        # Irteerako layer-a sortu (lehenengo aldian)
        if layer_out is None:
            srs = layer_in.GetSpatialRef()
            layer_out = ds_out.CreateLayer(
                "polygons", srs, ogr.wkbMultiPolygon
            )

            # Eremuak: fid automatikoa + type (String)
            field_type = ogr.FieldDefn("type", ogr.OFTString)
            field_type.SetWidth(254)
            layer_out.CreateField(field_type)

        layer_defn_out = layer_out.GetLayerDefn()
        type_idx_out = layer_defn_out.GetFieldIndex("type")

        layer_in.ResetReading()
        kargatutako_kopurua = 0

        for feature_in in layer_in:
            geom = feature_in.GetGeometryRef()
            if geom is None:
                continue

            # Soilik poligonoak
            geom_izena = geom.GetGeometryName()
            if geom_izena not in ("POLYGON", "MULTIPOLYGON"):
                continue

            # Poligonoa Multipoligono bihurtu
            if geom_izena == "POLYGON":
                multi = ogr.Geometry(ogr.wkbMultiPolygon)
                multi.AddGeometry(geom.Clone())
                geom_finala = multi
            else:
                geom_finala = geom.Clone()

            feature_out = ogr.Feature(layer_defn_out)
            feature_out.SetGeometry(geom_finala)
            feature_out.SetField(type_idx_out, type_balioa)

            layer_out.CreateFeature(feature_out)
            feature_out = None
            kargatutako_kopurua += 1

        ds_in = None  # itxi

        igarotakoa = time.time() - hasiera
        print(f"  {kargatutako_kopurua} poligono kargatu -> {igarotakoa:.2f} s")

    ds_out = None  # GPKG-a itxi

    denbora_totala = time.time() - denbora_totala_hasiera
    print(f"\nProzesu osoak {denbora_totala:.2f} segundo behar izan ditu.")
    print(f"GPKG sortuta: {gpkg_bidea}")


if __name__ == "__main__":
    main()
