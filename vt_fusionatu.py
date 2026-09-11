#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import geopandas as gpd
import pandas as pd

from shapely.ops import unary_union, snap

# ----------------------------------------------------------------------
# Shapely bateragarritasuna
# ----------------------------------------------------------------------

try:
    from shapely import make_valid
except ImportError:
    try:
        from shapely.validation import make_valid
    except ImportError:
        make_valid = None

# ----------------------------------------------------------------------
# Parametroak
# ----------------------------------------------------------------------

SNAP_DISTANCE = 0.50
MIN_AREA = 1.0

# ----------------------------------------------------------------------
# Log
# ----------------------------------------------------------------------

from logger import c_log

log = c_log(__file__)

# ----------------------------------------------------------------------
# Geometriak
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# Shapefile bilaketa
# ----------------------------------------------------------------------

def find_shapefiles(root_folder):

    shp_files = []

    for root, dirs, files in os.walk(root_folder):

        for filename in files:

            if filename.lower().endswith(".shp"):

                shp_files.append(
                    os.path.join(root, filename)
                )

    shp_files.sort()

    return shp_files


# ----------------------------------------------------------------------
# Shapefile irakurketa
# ----------------------------------------------------------------------

def read_shapefile(shp):

    encodings = [
        None,
        "utf-8",
        "latin1",
        "cp1252"
    ]

    last_error = None

    for encoding in encodings:

        try:

            if encoding is None:
                return gpd.read_file(shp)

            return gpd.read_file(
                shp,
                encoding=encoding
            )

        except Exception as e:

            last_error = e

    raise last_error


# ----------------------------------------------------------------------
# Topologia
# ----------------------------------------------------------------------

def clean_topology(
    gdf,
    snap_distance,
    min_area
):

    log("Geometriak balioztatzen...")

    gdf["geometry"] = gdf.geometry.apply(
        fix_geom
    )

    valid_geoms = [
        g
        for g in gdf.geometry
        if g is not None
    ]

    if len(valid_geoms) > 0:

        log("Snap sare globala sortzen...")

        union_geom = unary_union(
            valid_geoms
        )

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

                snapped.append(
                    geom
                )

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
        gdf.geometry.notnull()
    ].copy()

    gdf = gdf[
        ~gdf.geometry.is_empty
    ].copy()

    gdf = gdf[
        gdf.geometry.area >= min_area
    ].copy()

    return gdf


# ----------------------------------------------------------------------
# Programa nagusia
# ----------------------------------------------------------------------

def main():

    script_name = os.path.basename(
        sys.argv[0]
    )

    if len(sys.argv) != 3:

        log(
            f"Erabilera:\n"
            f"python3 {script_name} "
            f"<shp_karpeta> "
            f"<irteera.gpkg>"
        )

        sys.exit(1)

    shp_folder = sys.argv[1]
    output_gpkg = sys.argv[2]

    if not os.path.isdir(shp_folder):

        log(
            f"Ez da karpeta aurkitu: "
            f"{shp_folder}"
        )

        sys.exit(1)

    shp_files = find_shapefiles(
        shp_folder
    )

    if not shp_files:

        log(
            "Ez da shapefilerik aurkitu."
        )

        sys.exit(1)

    log(
        f"{len(shp_files)} shapefile "
        f"aurkitu dira "
        f"(azpidirektorioak barne)."
    )

    if os.path.exists(output_gpkg):

        log(
            f"Lehendik dagoen GPKG "
            f"ezabatzen: {output_gpkg}"
        )

        os.remove(output_gpkg)

    gdfs = []

    for shp in shp_files:

        try:

            rel_path = os.path.relpath(
                shp,
                shp_folder
            )

            log(
                f"Irakurtzen: {rel_path}"
            )

            gdf = read_shapefile(
                shp
            )

            if gdf is None:
                continue

            if gdf.empty:
                continue

            shp_name = os.path.splitext(
                os.path.basename(shp)
            )[0]

            if len(shp_name) > 2:
                type_value = shp_name[2:]
            else:
                type_value = shp_name

            tmp = gpd.GeoDataFrame(
                {
                    "type": [type_value] * len(gdf)
                },
                geometry=gdf.geometry,
                crs=gdf.crs
            )

            gdfs.append(tmp)

        except Exception as e:

            log(
                f"Errorea '{shp}' "
                f"irakurtzean: {e}"
            )

    if not gdfs:

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

    try:

        if (
            merged.crs
            and merged.crs.is_geographic
        ):

            log(
                "ABISUA: CRS geografikoa da. "
                "Azalerak gradu karratuetan "
                "kalkulatuko dira."
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
