#!/usr/bin/env python3
"""
GPKG fitxategi bateko poligonoak disolbatzeko script-a.
Disolbatzea 'type' eremuaren arabera egiten da.
Irteerako layer-aren izena irteerako GPKG fitxategiaren izenetik eratortzen da.
"""

import sys
import os
import time
from osgeo import ogr, gdal


def main():
    # Denbora kontagailua hasieratu
    hasiera = time.time()

    # Script-aren izena argv-tik hartu
    script_izena = os.path.basename(sys.argv[0])

    # Argumentuak egiaztatu
    if len(sys.argv) != 3:
        print(f"Erabilera: {script_izena} <sarrerako_gpkg> <irteerako_gpkg>")
        sys.exit(1)

    sarrera_gpkg = sys.argv[1]
    irteera_gpkg = sys.argv[2]

    # Sarrerako fitxategia existitzen den egiaztatu
    if not os.path.isfile(sarrera_gpkg):
        print(f"Errorea: Sarrerako fitxategia ez da existitzen: {sarrera_gpkg}")
        sys.exit(1)

    # Irteerako fitxategia existitzen bada, ezabatu
    if os.path.exists(irteera_gpkg):
        print(f"Informazioa: Irteerako fitxategia existitzen da, ezabatu egiten: {irteera_gpkg}")
        os.remove(irteera_gpkg)

    # Irteerako layer-aren izena: GPKG fitxategiaren izena .gpkg atzizkirik gabe
    irteera_layer_izena = os.path.splitext(os.path.basename(irteera_gpkg))[0]
    print(f"Irteerako layer-aren izena: '{irteera_layer_izena}'")

    # GPKG driver-a lortu
    driver = ogr.GetDriverByName("GPKG")
    if driver is None:
        print("Errorea: GPKG driver-a ez dago eskuragarri.")
        sys.exit(1)

    # Sarrerako datu-itura ireki
    sarrera_ds = ogr.Open(sarrera_gpkg, 0)  # 0 = irakurketa modua
    if sarrera_ds is None:
        print(f"Errorea: Ezin izan da sarrerako GPKG-a ireki: {sarrera_gpkg}")
        sys.exit(1)

    # Irteerako datu-itura sortu
    irteera_ds = driver.CreateDataSource(irteera_gpkg)
    if irteera_ds is None:
        print(f"Errorea: Ezin izan da irteerako GPKG-a sortu: {irteera_gpkg}")
        sarrera_ds = None
        sys.exit(1)

    # Sarrerako layer guztiak zeharkatu
    layer_kopurua = sarrera_ds.GetLayerCount()
    print(f"Sarrerako layer kopurua: {layer_kopurua}")

    # Poligonoak dituzten eta 'type' eremua duten layer-ak bildu
    poligono_layerrak = []
    for i in range(layer_kopurua):
        sarrera_layer = sarrera_ds.GetLayerByIndex(i)
        layer_izena = sarrera_layer.GetName()
        geom_type = sarrera_layer.GetGeomType()

        if geom_type not in (ogr.wkbPolygon, ogr.wkbMultiPolygon):
            print(f"  Abisua: '{layer_izena}' ez da poligono layer bat. Saltatzen.")
            continue

        layer_defn = sarrera_layer.GetLayerDefn()
        if layer_defn.GetFieldIndex("type") == -1:
            print(f"  Abisua: 'type' eremua ez da aurkitu '{layer_izena}' layer-ean. Saltatzen.")
            continue

        poligono_layerrak.append(sarrera_layer)

    if not poligono_layerrak:
        print("Errorea: Ez da 'type' eremua duen poligono layer-rik aurkitu.")
        sarrera_ds = None
        irteera_ds = None
        sys.exit(1)

    # Irteerako layer-a sortu behin bakarrik
    lehen_layer = poligono_layerrak[0]
    srs = lehen_layer.GetSpatialRef()
    irteera_layer = irteera_ds.CreateLayer(
        irteera_layer_izena, srs, geom_type=ogr.wkbMultiPolygon
    )

    # Eremuak kopiatu
    layer_defn = lehen_layer.GetLayerDefn()
    type_field_defn = None
    for j in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(j)
        irteera_layer.CreateField(field_defn)
        if field_defn.GetName() == "type":
            type_field_defn = field_defn

    irteera_layer_defn = irteera_layer.GetLayerDefn()

    print(f"\nPoligono layer baliodunak: {len(poligono_layerrak)}")

    # 'type' balio desberdinak bildu
    type_balioak = set()
    for sarrera_layer in poligono_layerrak:
        sarrera_layer.ResetReading()
        for feature in sarrera_layer:
            type_balioak.add(feature.GetField("type"))

    print(f"'type' balio desberdinak: {len(type_balioak)}")

    # 'type' balio bakoitzeko, geometriak bildu eta disolbatu
    for type_balioa in type_balioak:
        if type_balioa is None:
            iragazkia = "type IS NULL"
        else:
            balioa_str = str(type_balioa).replace("'", "''")
            iragazkia = f"type = '{balioa_str}'"

        # Geometria guztiak bildu MultiPolygon batean
        geometria_multzoa = ogr.Geometry(ogr.wkbMultiPolygon)
        feature_kopurua = 0

        for sarrera_layer in poligono_layerrak:
            sarrera_layer.SetAttributeFilter(iragazkia)
            for feature in sarrera_layer:
                geom = feature.GetGeometryRef()
                if geom is None:
                    continue

                geom_clone = geom.Clone()
                # Geometria motaren arabera MultiPolygon-era gehitu
                geom_mota = geom_clone.GetGeometryType()
                if geom_mota == ogr.wkbPolygon:
                    geometria_multzoa.AddGeometry(geom_clone)
                elif geom_mota == ogr.wkbMultiPolygon:
                    for k in range(geom_clone.GetGeometryCount()):
                        geometria_multzoa.AddGeometry(geom_clone.GetGeometryRef(k).Clone())
                feature_kopurua += 1

            sarrera_layer.SetAttributeFilter(None)

        if feature_kopurua == 0 or geometria_multzoa.GetGeometryCount() == 0:
            print(f"  - type='{type_balioa}': ez dago geometriarik, saltatzen.")
            continue

        # Disolbatu
        disolbatua = geometria_multzoa.UnionCascaded()

        if disolbatua is None or disolbatua.IsEmpty():
            print(f"  - type='{type_balioa}': disolbatzeak geometria hutsa eman du, saltatzen.")
            continue

        # Ziurtatu MultiPolygon motakoa dela
        if disolbatua.GetGeometryType() == ogr.wkbPolygon:
            multi = ogr.Geometry(ogr.wkbMultiPolygon)
            multi.AddGeometry(disolbatua)
            disolbatua = multi

        # Irteerako feature-a sortu
        irteera_feature = ogr.Feature(irteera_layer_defn)
        irteera_feature.SetGeometry(disolbatua)
        irteera_feature.SetField("type", type_balioa)

        irteera_layer.CreateFeature(irteera_feature)
        irteera_feature = None

        print(f"  - type='{type_balioa}': {feature_kopurua} feature disolbatu")

    # Layer sinkronizatu
    irteera_layer.SyncToDisk()

    # Baliabideak askatu
    sarrera_ds = None
    irteera_ds = None

    # Denbora kontagailua amaitu
    amaiera = time.time()
    denbora_totala = amaiera - hasiera

    print(f"\n{'='*50}")
    print(f"Prozesua amaituta.")
    print(f"Iraupena: {denbora_totala:.2f} segundo")
    print(f"Irteerako fitxategia: {irteera_gpkg}")
    print(f"Irteerako layer-aren izena: {irteera_layer_izena}")


if __name__ == "__main__":
    main()
