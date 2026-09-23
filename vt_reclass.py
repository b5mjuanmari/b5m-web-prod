#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG bateko datuak bersailkatzen ditu:
  - 'type' eremu berria sortu eta balioak esleitu:
      1. type_1 == 'intertidal' eta type_2 == 'meadow' -> type = 'marsh'
      2. type_1 != 'intertidal' eta type_2 == 'meadow' -> type = type_1
      3. type_1 ez null eta type_2 != 'meadow'         -> type = type_1
      4. type_1 ez null eta type_2 null                 -> type = type_1
      5. type_1 null eta type_2 ez null                 -> type = type_2
  - Ondoren 'type_1' eta 'type_2' eremuak ezabatu.

Erabilera:
    python3 vt_reclass.py <sarrerako.gpkg> <irteerako.gpkg> [log_fitxategia]

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

        log.info(f"Jatorrizko eremuak: {list(gdf.columns)}")

        # Beharrezko eremuak existitzen diren egiaztatu
        beharrezkoak = ['type_1', 'type_2']
        falta = [c for c in beharrezkoak if c not in gdf.columns]
        if falta:
            log.errorea(
                f"Beharrezko eremuak falta dira: {falta}"
            )
            sys.exit(1)

        # 'type' eremu berria sortu, hasieran balio nuluekin
        gdf['type'] = None

        # Maskarak prestatu
        type_1_ez_null = gdf['type_1'].notna()
        type_2_ez_null = gdf['type_2'].notna()
        type_1_intertidal = gdf['type_1'] == 'intertidal'
        type_2_meadow = gdf['type_2'] == 'meadow'

        # 1. kasua: type_1 == 'intertidal' eta type_2 == 'meadow'
        mask1 = type_1_intertidal & type_2_meadow
        # 2. kasua: type_1 != 'intertidal' eta type_2 == 'meadow'
        mask2 = ~type_1_intertidal & type_2_meadow
        # 4. kasua: type_1 ez null eta type_2 null
        mask4 = type_1_ez_null & ~type_2_ez_null
        # 5. kasua: type_1 null eta type_2 ez null
        mask5 = ~type_1_ez_null & type_2_ez_null
        # 3. kasua: type_1 ez null eta type_2 != 'meadow'
        #    (2., 4. eta 5. kasuak kanpoan utzita)
        mask3 = (
            type_1_ez_null
            & ~type_2_meadow
            & ~mask2
            & ~mask4
            & ~mask5
        )

        # Balioak esleitu maskararen arabera
        # 1. kasua: type = 'marsh'
        gdf.loc[mask1, 'type'] = 'marsh'
        # 2. kasua: type = type_1
        gdf.loc[mask2, 'type'] = gdf.loc[mask2, 'type_1']
        # 3. kasua: type = type_1
        gdf.loc[mask3, 'type'] = gdf.loc[mask3, 'type_1']
        # 4. kasua: type = type_1
        gdf.loc[mask4, 'type'] = gdf.loc[mask4, 'type_1']
        # 5. kasua: type = type_2
        gdf.loc[mask5, 'type'] = gdf.loc[mask5, 'type_2']

        log.info(f"  'type' eremua sortu eta balioak esleitu:")
        log.info(
            f"    1. kasua (intertidal + meadow -> marsh): {mask1.sum()}"
        )
        log.info(
            f"    2. kasua (!intertidal + meadow): {mask2.sum()}"
        )
        log.info(
            f"    3. kasua (type_1 + type_2 != meadow): {mask3.sum()}"
        )
        log.info(
            f"    4. kasua (type_1 + type_2 null): {mask4.sum()}"
        )
        log.info(
            f"    5. kasua (type_1 null + type_2 ez null): {mask5.sum()}"
        )

        # Ezabatu beharreko eremuak: type_1 eta type_2
        ezabatzeko = [c for c in ['type_1', 'type_2']
                      if c in gdf.columns]
        if ezabatzeko:
            gdf = gdf.drop(columns=ezabatzeko)
            log.info(f"  Eremuak ezabatu: {ezabatzeko}")
        else:
            log.info("  Oharra: ez dago ezabatzeko eremurik.")

        log.info(f"Emaitzako eremuak: {list(gdf.columns)}")
        log.info(f"  Geometria kopurua: {len(gdf)}")

        # Irteerako geruzaren izena: GPKG fitxategiaren izena .gpkg gabe
        geruza_izena = os.path.splitext(os.path.basename(irteera))[0]

        # Irteerako GPKG-a idatzi
        log.info(f"Idazten: {irteera} (geruza: {geruza_izena})")
        gdf.to_file(irteera, layer=geruza_izena, driver="GPKG")

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
