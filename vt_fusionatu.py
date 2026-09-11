#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

import geopandas as gpd
import pandas as pd

from shapely.ops import unary_union, snap

# Shapely bateragarritasuna
try:
    from shapely import make_valid
except ImportError:
    try:
        from shapely.validation import make_valid
    except ImportError:
        make_valid = None

# Parametro topologikoak
SNAP_DISTANCE = 0.50
MIN_AREA = 1.0

# Log
from logger import c_log

log = c_log(__file__)


def fix_geom(geom):

    if geom is None:
        return None

    try:
        if geom.is_valid:
            return geom
    except Exception:
        return geom

    if make_valid is not None:
        try:
            return make_valid(geom)
        except Exception:
            pass

    try:
        return geom.buffer(0)
    except Exception:
        return geom


def find_shapefiles(folder):

    shp_files = []

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(".shp"):

                shp_files.append(
                    os.path.join(root, file)
                )

    shp_files.sort()

    return shp_files


def read_shapefile(shp):

    try:
        return gpd.read_file(shp)

    except UnicodeDecodeError:

        try:
            return gpd.read_file(
                shp,
                encoding="latin1"
            )

        except Exception:

            return gpd.read_file(
                shp,
                encoding="cp1252"
            )


def sanitize_columns(gdf):

    rename_map = {}

    for col in gdf.columns:

        if col == "geometry":
            continue

        if col.lower() == "fid":

            rename_map[col] = "source_fid"

    if rename_map:

        for old_name, new_name in rename_map.items():

            log(
                f"Eremua berrizendatzen: "
                f"{old_name} -> {new_name}"
            )

        gdf = gdf.rename(columns=rename_map)

    return gdf


def clean_topology(gdf, snap_distance, min_area):

    log("Geometriak balioztatzen...")

    gdf["geometry"] = gdf.geometry.apply(fix_geom)

    valid_geoms = [
        geom
        for geom in gdf.geometry
        if geom is not None
    ]

    if len(valid_geoms) > 0:

        log("Snap sare globala sortzen...")

        union_geom = unary_union(valid_geoms)

        snapped = []

        for geom in gdf.geometry:

            if geom is None:

                snapped.append(None)

                continue

            try:

                snapped.append(
                    snap(
                        geom,
                        union_geom,
                        snap_distance
                    )
                )

            except Exception:

                snapped.append(geom)

        gdf["geometry"] = snapped

    log("Bigarren balidazioa...")

    gdf["geometry"] = gdf.geometry.apply(
        fix_geom
    )

    log(
        f"Azalera < {min_area} "
        f"duten poligonoak kentzen..."
    )

    gdf = gdf[
        (gdf.geometry.notnull()) &
        (~gdf.geometry.is_empty) &
        (gdf.geometry.area >= min_area)
    ].copy()

    return gdf


def main():

    script_name = os.path.basename(
        sys.argv[0]
    )

    if len(sys.argv) != 3:

        log(
            f"Erabilera:\n"
            f"python3 {script_name} "
            f"<shp_karpeta> <irteera.gpkg>"
        )

        sys.exit(1)

    shp_folder = sys.argv[1]
    output_gpkg = sys.argv[2]

    if not os.path.isdir(shp_folder):

        log(
            f"Errorea: ez da karpeta aurkitu -> "
            f"{shp_folder}"
        )

        sys.exit(1)

    shp_files = find_shapefiles(
        shp_folder
    )

    if len(shp_files) == 0:

        log(
            "Ez da shapefilerik aurkitu."
        )

        sys.exit(1)

    log(
        f"{len(shp_files)} shapefile "
        f"aurkitu dira "
        f"(azpidirektorioak barne)."
    )

    try:

        if os.path.exists(output_gpkg):

            log(
                f"Lehendik dagoen GPKG "
                f"ezabatzen: {output_gpkg}"
            )

            os.remove(output_gpkg)

    except Exception as e:

        log(
            f"Ezin izan da GPKG "
            f"ezabatu: {e}"
        )

        sys.exit(1)

    gdfs = []

    for shp in shp_files:

        try:

            log(
                f"Irakurtzen: "
                f"{os.path.relpath(shp, shp_folder)}"
            )

            gdf = read_shapefile(shp)

            if gdf is None:
                continue

            if gdf.empty:
                continue

            gdfs.append(gdf)

        except Exception as e:

            log(
                f"Errorea '{shp}' "
                f"irakurtzean: {e}"
            )

    if len(gdfs) == 0:

        log(
            "Ez dago fusionatzeko daturik."
        )

        sys.exit(1)

    log("Fusionatzen...")

    merged = gpd.GeoDataFrame(
        pd.concat(
            gdfs,
            ignore_index=True
        ),
        crs=gdfs[0].crs
    )

    merged = sanitize_columns(
        merged
    )

    try:

        if (
            merged.crs
            and merged.crs.is_geographic
        ):

            log(
                "ABISUA: CRS geografikoa da. "
                "Azalerak gradu karratuetan "
                "kalkulatzen dira."
            )

    except Exception:
        pass

    #merged = clean_topology(
    #    merged,
    #    SNAP_DISTANCE,
    #    MIN_AREA
    #)

    layer_name = os.path.splitext(
        os.path.basename(output_gpkg)
    )[0]

    log("GPKG idazten...")

    merged.to_file(
        output_gpkg,
        driver="GPKG",
        layer=layer_name,
        index=False
    )

    log(
        f"Eginda: {output_gpkg}"
    )

    log(
        f"Azken elementuak: "
        f"{len(merged)}"
    )


if __name__ == "__main__":
    main()
