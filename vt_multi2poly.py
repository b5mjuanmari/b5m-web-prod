#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG bateko multipoligonoak poligonetara bihurtzen ditu.

Erabilera:
    python script.py <sarrerako.gpkg> <irteerako.gpkg>
"""

import sys
import os
import time
import geopandas as gpd


def main():
    # Script-aren izena argv-tik hartu (kodea ez da aldatu behar izena aldatuta)
    izena = os.path.basename(sys.argv[0])
    erabilera = f"Erabilera: {izena} <sarrerako.gpkg> <irteerako.gpkg>"

    # Argumentu-kopurua egiaztatu
    if len(sys.argv) != 3:
        print(erabilera, file=sys.stderr)
        sys.exit(1)

    sarrera = sys.argv[1]
    irteera = sys.argv[2]

    # Sarrerako fitxategia existitzen den egiaztatu
    if not os.path.isfile(sarrera):
        print(f"Errorea: sarrerako fitxategia ez da existitzen: {sarrera}", file=sys.stderr)
        sys.exit(1)

    # Irteerako fitxategia existitzen bada, ezabatu
    if os.path.exists(irteera):
        os.remove(irteera)
        print(f"Existitzen zen irteerako fitxategia ezabatu da: {irteera}")

    # Denbora-kontagailua hasi
    hasiera = time.time()

    # Sarrerako GPKG-a irakurri
    print(f"Sarrerako fitxategia irakurtzen: {sarrera}")
    gdf = gpd.read_file(sarrera)

    # Multipoligonoak poligonetara bihurtu: explode()
    # explode() funtzioak geometria bakoitzeko zati bakarra uzten du
    gdf_pol = gdf.explode(index_parts=False).reset_index(drop=True)

    # Irteerako geruzaren izena: GPKG fitxategiaren izena .gpkg gabe
    geruza_izena = os.path.splitext(os.path.basename(irteera))[0]

    # Irteerako GPKG-a idatzi
    print(f"Idazten: {irteera} (geruza: {geruza_izena})")
    gdf_pol.to_file(irteera, layer=geruza_izena, driver="GPKG")

    # Denbora-kontagailua amaitu
    iraupena = time.time() - hasiera
    print(f"Eginda. Denbora: {iraupena:.2f} segundo")
    print(f"  Geometria kopurua (sarrera): {len(gdf)}")
    print(f"  Geometria kopurua (irteera): {len(gdf_pol)}")


if __name__ == "__main__":
    main()
