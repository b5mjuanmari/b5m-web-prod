#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG bateko datuak bersailkatzen ditu konfigurazio CSV bat erabiliz,
eta emaitza type eremuaren arabera disolbatuta gordetzen du.

Birsailkapenaren logika (CSVko errenkada bakoitzeko):
  1. CSV_ID_COBERTURA_MAX == GPKG_ID_COBERTURA_MAX
     eta CSV_TIPESTR null  ->  type = CSV_TYPE
  2. CSV_ID_COBERTURA_MAX == GPKG_ID_COBERTURA_MAX
     eta CSV_TIPESTR == GPKG_TIPESTR  ->  type = CSV_TYPE

Lehentasuna: TIPESTR zehatza duten arauek (2) irabazten dute
TIPESTR null duten arauen (1) aurrean.

Irteerako GPKG-ak bi eremu baino ez ditu izango: fid (automatikoa) eta type.
Amaieran, dissolve bat egiten da type eremuaren arabera.

Erabilera:
    python3 vt_reclass_siosear.py <sarrerako.gpkg> <konfigurazioa.csv> <irteerako.gpkg> [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)
"""

import sys
import os
import time
import pandas as pd
import geopandas as gpd

from log_utils import Log


# CSV-ko beharrezko zutabeak
CSV_BEHARREZKOA = [
    'ID_COBERTURA_MAX',
    'TIPESTR',
    'ID_TYPE',
    'TYPE',
]

# GPKG-ko beharrezko eremuak
GPKG_BEHARREZKOA = ['ID_COBERTURA_MAX', 'TIPESTR']

def normalize_int_str(x):
    """
    Balio bat modu koherentean normalizatzen du:
      - NULL/NaN/'' -> None
      - 35, 35.0, '35', '35.0' -> '35'   (str garbia)
      - 'Bidea' -> 'Bidea'               (testua ez da ukitzen)
    """
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s in ('', 'nan', 'None', 'NaN'):
        return None
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
        return s
    except (ValueError, TypeError):
        return s

def main():
    izena = os.path.basename(sys.argv[0])
    erabilera = (
        f"Erabilera: {izena} <sarrerako.gpkg> <konfigurazioa.csv> "
        f"<irteerako.gpkg> [log_fitxategia]"
    )

    # Argumentu-kopurua egiaztatu
    if len(sys.argv) not in (4, 5):
        print(erabilera, file=sys.stderr)
        sys.exit(1)

    sarrera = sys.argv[1]
    csv_path = sys.argv[2]
    irteera = sys.argv[3]
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, izena, sys.argv[1:])

    try:
        # Sarrerako fitxategiak existitzen diren egiaztatu
        if not os.path.isfile(sarrera):
            log.errorea(
                f"Sarrerako GPKG-a ez da existitzen: {sarrera}"
            )
            sys.exit(1)
        if not os.path.isfile(csv_path):
            log.errorea(
                f"Konfigurazio CSVa ez da existitzen: {csv_path}"
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

        # --- Konfigurazio CSVa irakurri ---
        log.info(f"Konfigurazio CSVa irakurtzen: {csv_path}")
        cfg = pd.read_csv(csv_path, dtype=str)

        log.info(f"CSVko zutabeak: {list(cfg.columns)}")
        falta_csv = [c for c in CSV_BEHARREZKOA if c not in cfg.columns]
        if falta_csv:
            log.errorea(
                f"CSVn beharrezko zutabeak falta dira: {falta_csv}"
            )
            sys.exit(1)

        # CSVan hutsik dauden TIPESTR -> None
        cfg.loc[cfg['TIPESTR'].isin(['', 'nan', 'None', 'NaN']),
                'TIPESTR'] = None

        log.info(f"CSV errenkada kopurua: {len(cfg)}")

        # --- Sarrerako GPKG-a irakurri ---
        log.info(f"Sarrerako GPKG-a irakurtzen: {sarrera}")
        gdf = gpd.read_file(sarrera)

        # ID eremuak normalizatu (string, zuriuneak kendu)
        for col in ['TIPESTR', 'ID_COBERTURA_MAX']:
            gdf[col] = gdf[col].apply(normalize_int_str)
            cfg[col] = cfg[col].apply(normalize_int_str)

        log.info(f"Jatorrizko eremuak: {list(gdf.columns)}")

        falta_gpkg = [c for c in GPKG_BEHARREZKOA
                      if c not in gdf.columns]
        if falta_gpkg:
            log.errorea(
                f"GPKGn beharrezko eremuak falta dira: {falta_gpkg}"
            )
            sys.exit(1)

        # ID eremuak normalizatu (string, zuriuneak kendu)
        gdf['ID_COBERTURA_MAX'] = (
            gdf['ID_COBERTURA_MAX'].astype(str).str.strip()
        )
        gdf['TIPESTR'] = (
            gdf['TIPESTR'].astype(str).str.strip()
        )
        # GPKGan hutsik dauden TIPESTR -> None
        gdf.loc[gdf['TIPESTR'].isin(['', 'nan', 'None', 'NaN']),
                'TIPESTR'] = None

        # --- Birsailkapena CSVaren arabera ---
        log.info("Birsailkapena egiten CSVaren arabera...")

        # 'type' eremu berria sortu, None-rekin (pandas zaharrarekin
        # bateragarritasun hobea lortzeko)
        gdf['type'] = None
        gdf['type'] = gdf['type'].astype(object)

        # Arauak bi multzotan banatu:
        #  - zehatzak: TIPESTR ez null
        #  - nullak:   TIPESTR null
        cfg_zehatz = cfg[cfg['TIPESTR'].notna()]
        cfg_null = cfg[cfg['TIPESTR'].isna()]

        log.info(
            f"CSVan TIPESTR zehatza duten arauak: {len(cfg_zehatz)}"
        )
        log.info(
            f"CSVan TIPESTR null duten arauak: {len(cfg_null)}"
        )

        # 1) Zehatzak lehenik (lehentasuna dute)
        for _, row in cfg_zehatz.iterrows():
            mask = (
                (gdf['ID_COBERTURA_MAX'] == row['ID_COBERTURA_MAX'])
                & (gdf['TIPESTR'] == row['TIPESTR'])
            )
            gdf.loc[mask, 'type'] = row['TYPE']

        # 2) Nullak geroago, baina soilik type oraindik null dutenentzat
        #    (horrela ez dute zehatzek esleitutakoa gainidazten)
        for _, row in cfg_null.iterrows():
            mask = (
                (gdf['ID_COBERTURA_MAX'] == row['ID_COBERTURA_MAX'])
                & (gdf['type'].isna())
            )
            gdf.loc[mask, 'type'] = row['TYPE']

        # Emaitzaren estatistikak
        esleituak = int(gdf['type'].notna().sum())
        esleitu_gabe = int(gdf['type'].isna().sum())
        log.info(f"  type esleitua: {esleituak}")
        log.info(f"  type esleitu gabe: {esleitu_gabe}")

        if esleitu_gabe > 0:
            log.info(
                "  Oharra: esleitu gabeko errenkadak 'type' nullarekin "
                "geratzen dira eta dissolvean ez dira agertuko."
            )

        # --- Irteerako GPKG-rako prestatu: type + geometry ---
        gdf = gdf[['type', 'geometry']].copy()

        log.info(
            f"  type balioak: "
            f"{sorted(gdf['type'].astype(str).unique().tolist())}"
        )

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
