#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG bateko 'type' eremua ezabatu eta 'subtype' eremua 'type' gisa berrizendatu.

Erabilera:
    python3 vt_rename_subtype.py <sarrerako.gpkg> <irteerako.gpkg> [log_fitxategia]

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
        f"Erabilera: {izena} <sarrerako.gpkg> <irteerako.gpkg> "
        f"[log_fitxategia]"
    )

    # Argumentu-kopurua egiaztatu
    if len(sys.argv) not in (3, 4):
        print(erabilera, file=sys.stderr)
        sys.exit(1)

    sarrera = sys.argv[1]
    irteera = sys.argv[2]
    log_path = sys.argv[3] if len(sys.argv) == 4 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, izena, sys.argv[1:])

    try:
        # Sarrerako fitxategia existitzen den egiaztatu
        if not os.path.isfile(sarrera):
            log.errorea(
                f"Sarrerako fitxategia ez da existitzen: {sarrera}"
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

        # Sarrerako GPKG-a irakurri
        log.info(f"Sarrerako fitxategia irakurtzen: {sarrera}")
        gdf = gpd.read_file(sarrera)

        # Jatorrizko zutabeak erakutsi (kontrolerako)
        log.info(f"Jatorrizko eremuak: {list(gdf.columns)}")

        # 'type' eremua ezabatu (existitzen bada)
        if 'type' in gdf.columns:
            gdf = gdf.drop(columns=['type'])
            log.info("'type' eremua ezabatu da.")
        else:
            log.info("Oharra: 'type' eremua ez da aurkitu, ez da ezer ezabatu.")

        # 'subtype' eremua 'type' gisa berrizendatu (existitzen bada)
        if 'subtype' in gdf.columns:
            gdf = gdf.rename(columns={'subtype': 'type'})
            log.info("'subtype' eremua 'type' gisa berrizendatu da.")
        else:
            log.info(
                "Oharra: 'subtype' eremua ez da aurkitu, ez da ezer berrizendatu."
            )

        # Emaitzako zutabeak erakutsi
        log.info(f"Emaitzako eremuak: {list(gdf.columns)}")

        # Irteerako geruzaren izena: GPKG fitxategiaren izena .gpkg gabe
        geruza_izena = os.path.splitext(os.path.basename(irteera))[0]

        # Irteerako GPKG-a idatzi
        log.info(f"Idazten: {irteera} (geruza: {geruza_izena})")
        gdf.to_file(irteera, layer=geruza_izena, driver="GPKG")

        # Denbora-kontagailua amaitu
        iraupena = time.time() - hasiera
        log.info(f"Eginda. Denbora: {iraupena:.2f} segundo")
        log.info(f"  Geometria kopurua: {len(gdf)}")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
