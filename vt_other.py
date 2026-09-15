#!/usr/bin/env python3
import os
import sys
import time
from osgeo import ogr


def main():
    script_name = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        print(f"Erabilera: {script_name} <sarrera.shp> <irteera.gpkg>", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    dst_path = sys.argv[2]

    # Irteerako geruzaren izena: fitxategiaren basename-a, .gpkg gabe
    layer_name = os.path.splitext(os.path.basename(dst_path))[0]

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

    # Geometria guztiak batu (disoluzioa)
    print("Geometriak batzen...")
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
            print(f"  {count} elementu prozesatuta...")

    print(f"  {count} elementu batu dira guztira.")

    if union_geom is None:
        print("Errorea: ez da geometriarik aurkitu.", file=sys.stderr)
        sys.exit(1)

    # Irteerako GPKG-a sortu
    dst_driver = ogr.GetDriverByName("GPKG")
    dst_ds = dst_driver.CreateDataSource(dst_path)
    if dst_ds is None:
        print(f"Errorea: ezin izan da irteerako GPKG-a sortu: {dst_path}", file=sys.stderr)
        sys.exit(1)

    # Geruza: izena fitxategiarena (.gpkg gabe)
    final_layer = dst_ds.CreateLayer(
        layer_name,
        srs=src_srs,
        geom_type=union_geom.GetGeometryType(),
        options=["SPATIAL_INDEX=YES"],
    )
    if final_layer is None:
        print(f"Errorea: ezin izan da '{layer_name}' geruza sortu.", file=sys.stderr)
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
    print(f"Eginda. Denbora: {elapsed:.2f} segundo")
    print(f"Irteerako fitxategia: {dst_path}")
    print(f"Geruzaren izena: {layer_name}")


if __name__ == "__main__":
    main()
