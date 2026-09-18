#!/usr/bin/env python3
"""
Scripta: poligono SHAPEFILE bat hartu, 'type' eremu bat sortu 'other'
balioarekin, eta 'type' eremuaren arabera disolbatu.

Irteerako GPKG-ak bi eremu izango ditu:
  - fid  : sistemak (OGR/GDAL) sortutako identifikatzailea
  - type : scriptak sortutako eremua

Irteerako geruzaren izena fitxategiaren izena izango da, .gpkg atzizkia gabe.

Erabilera:
    python3 script.py <sarrera_shp> <irteera_gpkg>
"""

import sys
import os
import time

import geopandas as gpd


def main():
    hasiera = time.time()

    # --- Argumentuak egiaztatu ---
    if len(sys.argv) != 3:
        script_izena = os.path.basename(sys.argv[0])
        print(f"Erabilera: {script_izena} <sarrera_shp> <irteera_gpkg>")
        sys.exit(1)

    script_izena = os.path.basename(sys.argv[0])
    sarrera_bidea = sys.argv[1]
    irteera_bidea = sys.argv[2]

    # --- Sarrerako fitxategia existitzen den egiaztatu ---
    if not os.path.isfile(sarrera_bidea):
        print(f"[ERROREA] Ez da fitxategia aurkitu: {sarrera_bidea}")
        sys.exit(1)

    # --- Irteerako fitxategia existitzen bada, ezabatu ---
    if os.path.exists(irteera_bidea):
        try:
            os.remove(irteera_bidea)
            print(f"[INFO] Aurreko irteera ezabatu da: {irteera_bidea}")
        except OSError as e:
            print(f"[ERROREA] Ezin izan da irteera ezabatu: {e}")
            sys.exit(1)

    # --- Irteerako geruzaren izena: fitxategiaren izena .gpkg gabe ---
    layer_izena = os.path.splitext(os.path.basename(irteera_bidea))[0]
    print(f"[INFO] Irteerako geruzaren izena: {layer_izena}")

    # --- Shapefile irakurri ---
    print(f"[INFO] {sarrera_bidea} irakurtzen...")
    gdf = gpd.read_file(sarrera_bidea)
    print(f"[INFO] Sarrerako elementuak: {len(gdf)}")
    print(f"[INFO] CRS: {gdf.crs}")

    # --- 'type' eremua sortu eta 'other' balioa jarri ---
    gdf["type"] = "other"
    print("[INFO] 'type' eremua sortu da 'other' balioarekin.")

    # --- 'type' eremuaren arabera disolbatu ---
    print("[INFO] 'type' eremuaren arabera disolbatzen...")
    gdf_disolbatu = gdf.dissolve(by="type").reset_index()

    # --- Emaitzan soilik 'type' eremua mantendu ---
    gdf_disolbatu = gdf_disolbatu[["type", "geometry"]]
    gdf_disolbatu = gpd.GeoDataFrame(
        gdf_disolbatu, geometry="geometry", crs=gdf.crs
    )

    print(f"[INFO] Disolbatu ondorengo elementuak: {len(gdf_disolbatu)}")

    # --- Irteera gorde GPKG gisa ---
    # 'fid' eremua OGR/GDAL driver-ak automatikoki gehitzen du idaztean.
    # index=False erabili, indize-oihartzerik egon ez dadin.
    gdf_disolbatu.to_file(
        irteera_bidea, driver="GPKG", layer=layer_izena, index=False
    )
    print(f"[INFO] Irteera gorde da: {irteera_bidea} (layer: {layer_izena})")

    # --- Denbora kontagailua ---
    iraupena = time.time() - hasiera
    print(f"[INFO] Exekuzio denbora: {iraupena:.2f} segundo")


if __name__ == "__main__":
    main()
