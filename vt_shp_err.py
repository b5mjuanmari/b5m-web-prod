#!/usr/bin/env python3

import csv
import json
import os
import sys

import fiona
from shapely.geometry import shape
from shapely.validation import explain_validity


def scan_shapefile(shp_path, writer):
    """
    Shapefile baten feature guztiak aztertzen ditu eta
    aurkitutako erroreak CSVra idazten ditu.
    """

    try:
        with fiona.open(shp_path) as src:

            for feature_id, feat in enumerate(src):

                feature_fid = feat.get("id", "")

                properties = (
                    dict(feat["properties"])
                    if feat.get("properties")
                    else {}
                )

                geometry = feat.get("geometry")

                try:

                    if geometry is None:
                        writer.writerow([
                            shp_path,
                            feature_id,
                            feature_fid,
                            "NULL_GEOMETRY",
                            "Geometry is NULL",
                            f"Propietateak: {json.dumps(properties, ensure_ascii=False)}",
                            ""
                        ])
                        continue

                    geom = shape(geometry)

                    if not geom.is_valid:
                        writer.writerow([
                            shp_path,
                            feature_id,
                            feature_fid,
                            "INVALID_GEOMETRY",
                            explain_validity(geom),
                            f"Propietateak: {json.dumps(properties, ensure_ascii=False)}",
                            ""
                        ])

                except Exception as e:

                    err_msg = str(e)

                    if err_msg == "A LinearRing must have at least 3 coordinate tuples":
                        geom_txt = (
                            "Geometria: "
                            + json.dumps(geometry, ensure_ascii=False)
                        )
                    else:
                        geom_txt = ""

                    writer.writerow([
                        shp_path,
                        feature_id,
                        feature_fid,
                        "FEATURE_ERROR",
                        err_msg,
                        f"Propietateak: {json.dumps(properties, ensure_ascii=False)}",
                        geom_txt
                    ])

    except Exception as e:

        writer.writerow([
            shp_path,
            "",
            "",
            "FILE_ERROR",
            str(e),
            "",
            ""
        ])


def find_shapefiles(root_dir):
    """
    Karpeta eta azpikarpetetako .shp guztiak aurkitzen ditu.
    """

    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith(".shp"):
                yield os.path.join(root, filename)


def main():

    if len(sys.argv) != 3:
        print(
            f"Erabilera: {os.path.basename(sys.argv[0])} "
            "<shapefile_karpeta> <txostena.csv>"
        )
        sys.exit(1)

    root_dir = sys.argv[1]
    report_csv = sys.argv[2]

    if not os.path.isdir(root_dir):
        print(f"ERROR: Karpeta ez da existitzen: {root_dir}")
        sys.exit(1)

    if os.path.exists(report_csv):
        os.remove(report_csv)

    total_shp = 0

    with open(report_csv, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            "shapefile",
            "feature_id",
            "feature_fid",
            "error_type",
            "details",
            "properties",
            "geometry"
        ])

        for shp_path in find_shapefiles(root_dir):

            total_shp += 1
            print(f"Aztertzen: {shp_path}")

            scan_shapefile(shp_path, writer)

    print()
    print(f"Aztertutako shapefile kopurua: {total_shp}")
    print(f"Txostena: {report_csv}")


if __name__ == "__main__":
    main()
