#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poligono Shapefile guztiak (azpikarpetak barne) GPKG fitxategi bakar batean fusionatu.

GPKG-aren layer izena fitxategiaren izenetik eratortzen da (.gpkg atzizkia kenduta).

Erabilera:
    python script.py <shapefile_karpeta> <gpkg_bidea> [iragazkia]

Hirugarren parametroa aukerakoa da:
  - Ematen bada: izenean kate hori duten Shapefile-ak soilik hartuko dira.
  - Ez bada ematen: Shapefile guztiak hartuko dira.
"""

import os
import sys
import time
from osgeo import ogr


# type balioaren mapaketa
TYPE_MAP = {
    "arb": "tree",
    "for": "forest",
    "mat": "scrub",
    "pra": "meadow",
}


def main():
    script_izena = os.path.basename(sys.argv[0])

    if len(sys.argv) not in (3, 4):
        print(f"Erabilera: {script_izena} <shapefile_karpeta> <gpkg_bidea> [iragazkia]",
              file=sys.stderr)
        sys.exit(1)

    karpeta = sys.argv[1]
    gpkg_bidea = sys.argv[2]
    iragazkia = sys.argv[3] if len(sys.argv) == 4 else None

    if not os.path.isdir(karpeta):
        print(f"Errorea: '{karpeta}' ez da karpeta baliogarri bat.", file=sys.stderr)
        sys.exit(1)

    # GPKG-aren layer izena: fitxategiaren izena .gpkg atzizkia gabe
    layer_izena = os.path.splitext(os.path.basename(gpkg_bidea))[0]

    # GPKG driver-a egiaztatu aurretik
    driver = ogr.GetDriverByName("GPKG")
    if driver is None:
        print("Errorea: GPKG driver-a ez dago erabilgarri.", file=sys.stderr)
        sys.exit(1)

    if iragazkia:
        print(f"Iragazkia: izenean '{iragazkia}' katea duten Shapefile-ak soilik")
    else:
        print("Iragazkirik ez: Shapefile guztiak hartuko dira")

    # Shapefile-ak bilatu (azpikarpetak barne), iragazkia aplikatuta
    shp_zerrenda = []
    iragazkia_lower = iragazkia.lower() if iragazkia else None
    for erroa, _, fitxategiak in os.walk(karpeta):
        for fitxategia in fitxategiak:
            if not fitxategia.lower().endswith(".shp"):
                continue
            if iragazkia_lower and iragazkia_lower not in fitxategia.lower():
                continue
            shp_zerrenda.append(os.path.join(erroa, fitxategia))

    shp_zerrenda.sort()

    if not shp_zerrenda:
        if iragazkia:
            print(f"Ez da '{iragazkia}' katea duen Shapefile-ik aurkitu.")
        else:
            print("Ez da Shapefile-ik aurkitu.")
        sys.exit(0)

    print(f"{len(shp_zerrenda)} Shapefile aurkitu dira.")
    print(f"GPKG-aren layer izena: '{layer_izena}'")

    # GPKG-a ezabatu aurretik badago
    if os.path.exists(gpkg_bidea):
        os.remove(gpkg_bidea)
        print(f"Aurreko GPKG ezabatu da: {gpkg_bidea}")

    # GPKG-a sortu
    ds_out = driver.CreateDataSource(gpkg_bidea)
    if ds_out is None:
        print(f"Errorea: ezin izan da GPKG-a sortu: {gpkg_bidea}", file=sys.stderr)
        sys.exit(1)

    layer_out = None
    srs_ref = None
    denbora_hasiera = time.time()

    for idx, shp_bidea in enumerate(shp_zerrenda, 1):
        hasiera = time.time()
        izen_garbia = os.path.splitext(os.path.basename(shp_bidea))[0]

        # 'type' balioa: lehenengo bi hizkiak kendu eta azpimarra kendu
        type_gordina = izen_garbia[2:].lstrip("_") if len(izen_garbia) > 2 else izen_garbia
        # Mapaketa aplikatu (ez badago, jatorrizkoa)
        type_balioa = TYPE_MAP.get(type_gordina.lower(), type_gordina)

        print(f"[{idx}/{len(shp_zerrenda)}] {os.path.basename(shp_bidea)} -> type='{type_balioa}'")

        ds_in = ogr.Open(shp_bidea, 0)
        if ds_in is None:
            print(f"  Abisua: ezin izan da ireki.", file=sys.stderr)
            continue

        layer_in = ds_in.GetLayer(0)
        if layer_in is None:
            print(f"  Abisua: ez du layer-ik.", file=sys.stderr)
            ds_in = None
            continue

        srs_in = layer_in.GetSpatialRef()

        # Irteerako layer-a sortu (lehenengo aldian)
        if layer_out is None:
            srs_ref = srs_in
            layer_out = ds_out.CreateLayer(
                layer_izena, srs_ref, ogr.wkbMultiPolygon
            )

            # Eremuak: fid automatikoa + type (String)
            field_type = ogr.FieldDefn("type", ogr.OFTString)
            field_type.SetWidth(64)
            layer_out.CreateField(field_type)
        else:
            # SRS-aren egiaztapena
            if (srs_in is None) != (srs_ref is None):
                print(f"  Abisua: SRS desberdina edo falta: {shp_bidea}", file=sys.stderr)
            elif srs_in is not None and not srs_in.IsSame(srs_ref):
                print(f"  Abisua: SRS desberdina: {shp_bidea}", file=sys.stderr)

        layer_defn_out = layer_out.GetLayerDefn()
        type_idx_out = layer_defn_out.GetFieldIndex("type")

        layer_in.ResetReading()
        kargatutakoa = 0
        baztertutakoa = 0

        layer_out.StartTransaction()
        for feature_in in layer_in:
            geom = feature_in.GetGeometryRef()
            if geom is None or geom.IsEmpty():
                baztertutakoa += 1
                continue

            # Soilik poligonoak
            geom_izena = geom.GetGeometryName()
            if geom_izena not in ("POLYGON", "MULTIPOLYGON"):
                baztertutakoa += 1
                continue

            # buffer(0) geometria baliogabeak konpontzeko (GEOS 3.8 baino zaharragoentzat ere bai)
            g = geom.Clone().Buffer(0)
            if g is None or g.IsEmpty():
                baztertutakoa += 1
                continue

            # Poligonoa Multipoligono bihurtu
            if geom_izena == "POLYGON":
                multi = ogr.Geometry(ogr.wkbMultiPolygon)
                if multi.AddGeometry(g) != ogr.OGRERR_NONE:
                    baztertutakoa += 1
                    continue
                geom_finala = multi
            else:
                geom_finala = g

            feature_out = ogr.Feature(layer_defn_out)
            feature_out.SetGeometry(geom_finala)
            feature_out.SetField(type_idx_out, type_balioa)

            if layer_out.CreateFeature(feature_out) != ogr.OGRERR_NONE:
                baztertutakoa += 1
            else:
                kargatutakoa += 1
            feature_out = None
        layer_out.CommitTransaction()

        ds_in = None  # itxi

        igarotakoa = time.time() - hasiera
        print(f"  {kargatutakoa} poligono kargatu, {baztertutakoa} baztertu -> {igarotakoa:.2f} s")

    ds_out = None  # GPKG-a itxi

    denbora_totala = time.time() - denbora_hasiera
    print(f"\nProzesu osoak {denbora_totala:.2f} segundo behar izan ditu.")
    print(f"GPKG sortuta: {gpkg_bidea}")


if __name__ == "__main__":
    main()
