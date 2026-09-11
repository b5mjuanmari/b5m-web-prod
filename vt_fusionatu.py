#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.ops import unary_union, snap


# Parametro topologikoak
SNAP_DISTANCE = 0.50      # mapako unitateetan (metroak normalean)
MIN_AREA = 1.0            # m² edo CRSaren unitate karratuak

# Log
from logger import c_log
log = c_log(__file__)

def clean_topology(gdf, snap_distance, min_area):
    """
    Topologia-garbiketa:
      - geometria baliogabeak konpondu
      - snap egin ertzak bateratzeko
      - poligono txikiak kendu
    """

    log("Geometriak balioztatzen...")

    gdf["geometry"] = gdf.geometry.apply(
        lambda geom: make_valid(geom) if geom and not geom.is_valid else geom
    )

    log("Snap sare globala sortzen...")

    union_geom = unary_union(gdf.geometry)

    snapped_geoms = []

    for geom in gdf.geometry:
        if geom is None:
            snapped_geoms.append(None)
        else:
            snapped_geoms.append(
                snap(geom, union_geom, snap_distance)
            )

    gdf["geometry"] = snapped_geoms

    log("Bigarren balidazioa...")

    gdf["geometry"] = gdf.geometry.apply(
        lambda geom: make_valid(geom) if geom else geom
    )

    log(f"Azalera < {min_area} duten poligonoak kentzen...")

    gdf = gdf[gdf.geometry.area >= min_area].copy()

    return gdf


def main():

    script_name = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        log(
            f"Erabilera:\n"
            f"  /opt/miniconda3/bin/python3 {script_name} <shp_karpeta> <irteera.gpkg>"
        )
        sys.exit(1)

    shp_folder = sys.argv[1]
    output_gpkg = sys.argv[2]

    if not os.path.isdir(shp_folder):
        log(f"Errorea: ez da karpeta aurkitu -> {shp_folder}")
        sys.exit(1)

    shp_files = glob.glob(os.path.join(shp_folder, "*.shp"))

    if not shp_files:
        log("Ez da shapefilerik aurkitu.")
        sys.exit(1)

    log(f"{len(shp_files)} shapefile aurkitu dira.")

    if os.path.exists(output_gpkg):
        log(f"Lehendik dagoen GPKG ezabatzen: {output_gpkg}")
        os.remove(output_gpkg)

    gdfs = []

    for shp in shp_files:
        log(f"Irakurtzen: {os.path.basename(shp)}")
        gdf = gpd.read_file(shp)

        if gdf.empty:
            continue

        gdfs.append(gdf)

    if not gdfs:
        log("Ez dago fusionatzeko daturik.")
        sys.exit(1)

    log("Fusionatzen...")

    merged = gpd.GeoDataFrame(
        pd.concat(gdfs, ignore_index=True),
        crs=gdfs[0].crs
    )

    merged = clean_topology(
        merged,
        snap_distance=SNAP_DISTANCE,
        min_area=MIN_AREA
    )

    layer_name = os.path.splitext(
        os.path.basename(output_gpkg)
    )[0]

    log("GPKG idazten...")

    merged.to_file(
        output_gpkg,
        layer=layer_name,
        driver="GPKG"
    )

    log(f"Eginda: {output_gpkg}")
    log(f"Azken elementuak: {len(merged)}")

if __name__ == "__main__":
    main()
