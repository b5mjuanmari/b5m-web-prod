#!/usr/bin/env python3
"""
Scripta: poligono SHAPEFILE bat hartu, 'type' eremu bat sortu 'other'
balioarekin, eta 'type' eremuaren arabera disolbatu.

Irteerako GPKG-ak bi eremu izango ditu:
  - fid  : sistemak (OGR/GDAL) sortutako identifikatzailea
  - type : scriptak sortutako eremua

Irteerako geruzaren izena fitxategiaren izena izango da, .gpkg atzizkia gabe.

Erabilera:
    python3 vt_disolbatu2.py <sarrera_shp> <irteera_gpkg> [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)
"""

import sys
import os
import time

import geopandas as gpd

from log_utils import Log


def main():
    hasiera = time.time()

    # --- Argumentuak egiaztatu ---
    # Gutxienez 2 argumentu behar dira (sarrera + irteera).
    # Hirugarrena (log fitxategia) aukerakoa da.
    if len(sys.argv) not in (3, 4):
        script_izena = os.path.basename(sys.argv[0])
        print(
            f"Erabilera: {script_izena} "
            f"<sarrera_shp> <irteera_gpkg> [log_fitxategia]"
        )
        sys.exit(1)

    script_izena = os.path.basename(sys.argv[0])
    sarrera_bidea = sys.argv[1]
    irteera_bidea = sys.argv[2]
    log_bidea = sys.argv[3] if len(sys.argv) == 4 else None

    # --- Log sistema abiarazi ---
    log = Log(log_bidea, script_izena, sys.argv[1:])

    try:
        # --- Sarrerako fitxategia existitzen den egiaztatu ---
        if not os.path.isfile(sarrera_bidea):
            log.errorea(f"Ez da fitxategia aurkitu: {sarrera_bidea}")
            sys.exit(1)

        # --- Irteerako fitxategia existitzen bada, ezabatu ---
        if os.path.exists(irteera_bidea):
            try:
                os.remove(irteera_bidea)
                log.info(f"Aurreko irteera ezabatu da: {irteera_bidea}")
            except OSError as e:
                log.errorea(f"Ezin izan da irteera ezabatu: {e}")
                sys.exit(1)

        # --- Irteerako geruzaren izena: fitxategiaren izena .gpkg gabe ---
        layer_izena = os.path.splitext(os.path.basename(irteera_bidea))[0]
        log.info(f"Irteerako geruzaren izena: {layer_izena}")

        # --- Shapefile irakurri ---
        log.info(f"{sarrera_bidea} irakurtzen...")
        gdf = gpd.read_file(sarrera_bidea)
        log.info(f"Sarrerako elementuak: {len(gdf)}")
        log.info(f"CRS: {gdf.crs}")

        # --- 'type' eremua sortu eta 'other' balioa jarri ---
        gdf["type"] = "other"
        log.info("'type' eremua sortu da 'other' balioarekin.")

        # --- 'type' eremuaren arabera disolbatu ---
        log.info("'type' eremuaren arabera disolbatzen...")
        gdf_disolbatu = gdf.dissolve(by="type").reset_index()

        # --- Emaitzan soilik 'type' eremua mantendu ---
        gdf_disolbatu = gdf_disolbatu[["type", "geometry"]]
        gdf_disolbatu = gpd.GeoDataFrame(
            gdf_disolbatu, geometry="geometry", crs=gdf.crs
        )

        log.info(f"Disolbatu ondorengo elementuak: {len(gdf_disolbatu)}")

        # --- Irteera gorde GPKG gisa ---
        gdf_disolbatu.to_file(
            irteera_bidea, driver="GPKG", layer=layer_izena, index=False
        )
        log.info(f"Irteera gorde da: {irteera_bidea} (layer: {layer_izena})")

        # --- Denbora kontagailua ---
        iraupena = time.time() - hasiera
        log.info(f"Exekuzio denbora: {iraupena:.2f} segundo")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
