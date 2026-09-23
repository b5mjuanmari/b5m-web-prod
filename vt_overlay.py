#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bi GPKG gainjartzen ditu (QGISeko "Batuketa" / Union algoritmoaren antzera)
eta hirugarren bat sortzen du.

Irteerako GPKGak sarrerako bi GPKG-en eremuak izango ditu:
  - Lehenengo GPKGtik datozen eremuek '_1' atzizkia izango dute.
  - Bigarren GPKGtik datozen eremuek '_2' atzizkia izango dute.
Geometria-eremua (geometry) ez da aldatzen.

Erabilera:
    python3 vt_overlay.py <sarrera1.gpkg> <sarrera2.gpkg> <irteera.gpkg> [log_fitxategia]

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
    # Script-aren izena argv-tik hartu
    izena = os.path.basename(sys.argv[0])
    erabilera = (
        f"Erabilera: {izena} <sarrera1.gpkg> <sarrera2.gpkg> "
        f"<irteera.gpkg> [log_fitxategia]"
    )

    # Argumentu-kopurua egiaztatu
    if len(sys.argv) not in (4, 5):
        print(erabilera, file=sys.stderr)
        sys.exit(1)

    sarrera1 = sys.argv[1]
    sarrera2 = sys.argv[2]
    irteera = sys.argv[3]
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, izena, sys.argv[1:])

    try:
        # Bi sarrerako fitxategiak existitzen diren egiaztatu
        if not os.path.isfile(sarrera1):
            log.errorea(
                f"Lehen sarrerako fitxategia ez da existitzen: {sarrera1}"
            )
            sys.exit(1)

        if not os.path.isfile(sarrera2):
            log.errorea(
                f"Bigarren sarrerako fitxategia ez da existitzen: {sarrera2}"
            )
            sys.exit(1)

        # Irteerako fitxategia existitzen bada, ezabatu
        if os.path.exists(irteera):
            os.remove(irteera)
            log.info(
                f"Existitzen zen irteerako fitxategia ezabatu da: {irteera}"
            )

        # Denbora-kontagailua hasi
        hasiera = time.time()

        # Bi GPKG-ak irakurri
        log.info(f"Lehen sarrerako fitxategia irakurtzen: {sarrera1}")
        gdf1 = gpd.read_file(sarrera1)

        log.info(f"Bigarren sarrerako fitxategia irakurtzen: {sarrera2}")
        gdf2 = gpd.read_file(sarrera2)

        log.info(f"  Lehen GPKG-ko eremuak: {list(gdf1.columns)}")
        log.info(f"  Bigarren GPKG-ko eremuak: {list(gdf2.columns)}")

        # Geometria-eremuaren izena gorde (normalean 'geometry')
        geom_col_1 = gdf1.geometry.name
        geom_col_2 = gdf2.geometry.name

        # Eremuak berrizendatu, '_1' eta '_2' atzizkiekin.
        # Geometria-eremua ez da berrizendatzen.
        gdf1_renamed = gdf1.rename(
            columns={
                c: f"{c}_1"
                for c in gdf1.columns
                if c != geom_col_1
            }
        )
        gdf2_renamed = gdf2.rename(
            columns={
                c: f"{c}_2"
                for c in gdf2.columns
                if c != geom_col_2
            }
        )

        log.info(
            f"  Lehen GPKG-ko eremuak berrizendatu: "
            f"{list(gdf1_renamed.columns)}"
        )
        log.info(
            f"  Bigarren GPKG-ko eremuak berrizendatu: "
            f"{list(gdf2_renamed.columns)}"
        )

        # CRS-a egiaztatu eta behar izanez gero bigarrena proiektatu
        if gdf1.crs != gdf2.crs:
            log.info(
                f"Oharra: CRS desberdinak dira. "
                f"Lehen: {gdf1.crs}, Bigarren: {gdf2.crs}. "
                f"Bigarrena lehenengora proiektatuko da."
            )
            gdf2_renamed = gdf2_renamed.to_crs(gdf1.crs)

        # Bi geruzak gainjarri (QGISeko "Batuketa" / Union)
        log.info("Bi GPKG-ak gainjartzen (union)...")
        gdf_overlay = gpd.overlay(
            gdf1_renamed,
            gdf2_renamed,
            how='union',
            keep_geom_type=True
        )

        # Geometria-eremuaren izena 'geometry' dela ziurtatu (behar izanez gero)
        if gdf_overlay.geometry.name != 'geometry':
            gdf_overlay = gdf_overlay.rename_geometry('geometry')

        log.info(f"  Emaitzako eremuak: {list(gdf_overlay.columns)}")
        log.info(f"  Geometria kopurua: {len(gdf_overlay)}")

        # Irteerako geruzaren izena: GPKG fitxategiaren izena .gpkg gabe
        geruza_izena = os.path.splitext(os.path.basename(irteera))[0]

        # Irteerako GPKG-a idatzi
        log.info(f"Idazten: {irteera} (geruza: {geruza_izena})")
        gdf_overlay.to_file(irteera, layer=geruza_izena, driver="GPKG")

        # Denbora-kontagailua amaitu
        iraupena = time.time() - hasiera
        log.info(f"Eginda. Denbora: {iraupena:.2f} segundo")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
