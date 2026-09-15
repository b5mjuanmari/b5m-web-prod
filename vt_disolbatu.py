#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG fitxategi baten poligonoak 'type' eremuaren arabera disolbatzen ditu.

Erabilera:
    python3 <script_izena> sarrera.gpkg irteera.gpkg
"""

import argparse
import os
import sys
import time

import geopandas as gpd
from shapely.ops import unary_union

FIELD = "type"  # Disolbatzeko eremua

# Batzeko tolerantzia (geometriaren unitatean, adib. metrotan EPSG:25830-ean).
# Poligonoen artean geratzen diren zirrikitu mikroskopikoak ixteko erabiltzen
# da: lehenik poligonoak EPS-ekin handitu, gero bateratu, eta azkenik EPS
# beraekin txikitu, tamaina jatorrira itzuliz. Balio txikia izan behar du,
# poligono errealen forma alda ez dezan.
EPS = 0.01


def parseatu_argumentuak():
    # argparse-k berak hartzen du script-aren izena sys.argv[0]-tik
    # 'usage' mezuetarako, beraz script-a berrizendatuz gero ez da
    # kodea aldatu behar.
    parser = argparse.ArgumentParser(
        description="GPKG baten poligonoak 'type' eremuaren arabera disolbatu."
    )
    parser.add_argument("sarrera_gpkg", help="Sarrerako GPKG fitxategiaren bidea")
    parser.add_argument("irteera_gpkg", help="Irteerako GPKG fitxategiaren bidea")
    return parser.parse_args()


def egiaztatu_sarrera(bidea):
    if not os.path.isfile(bidea):
        sys.exit("ERROREA: sarrerako fitxategia ez da existitzen: {}".format(bidea))


def ezabatu_irteera_baldin_badago(bidea):
    if os.path.exists(bidea):
        os.remove(bidea)
        print("Aurretik zegoen irteerako fitxategia ezabatu da: {}".format(bidea))


def disolbatu(gdf, eremua):
    """
    Poligonoak 'eremua' zutabearen arabera disolbatu, eta talde bakoitzeko
    poligonoen artean gera daitezkeen barne-mugak kendu.

    Poligono jatorrizkoek zehazki ertz bera partekatzen ez badute (topologia
    akats arruntak, LiDAR/kartografia datuetan ohikoak), unary_union hutsak
    ez ditu erabat bateratzen, eta jatorrizko mugen arrastoak gera daitezke.
    Hori saihesteko, "buffer trick" erabiltzen da: poligonoak EPS-ekin
    handitu, bateratu, eta gero EPS beraekin txikitu, tamaina jatorrira
    itzuliz. Horrela, EPS baino txikiagoak diren zirrikituak ixten dira eta
    barne-mugak erabat desagertzen dira.
    """
    disolbatuak = []
    balioak = []

    for balioa, taldea in gdf.groupby(eremua):
        handituak = [geom.buffer(EPS) for geom in taldea.geometry.values]
        geometria_batua = unary_union(handituak)
        geometria_garbia = geometria_batua.buffer(-EPS)

        disolbatuak.append(geometria_garbia)
        balioak.append(balioa)

    emaitza = gpd.GeoDataFrame(
        {eremua: balioak, "geometry": disolbatuak}, crs=gdf.crs
    )
    return emaitza


def main():
    argumentuak = parseatu_argumentuak()

    egiaztatu_sarrera(argumentuak.sarrera_gpkg)
    ezabatu_irteera_baldin_badago(argumentuak.irteera_gpkg)

    hasiera = time.time()

    print("Irakurtzen: {}".format(argumentuak.sarrera_gpkg))
    gdf = gpd.read_file(argumentuak.sarrera_gpkg)

    if FIELD not in gdf.columns:
        sys.exit("ERROREA: '{}' eremua ez dago sarrerako fitxategian".format(FIELD))

    print("Disolbatzen '{}' eremuaren arabera...".format(FIELD))
    emaitza = disolbatu(gdf, FIELD)

    print("Idazten: {}".format(argumentuak.irteera_gpkg))
    emaitza.to_file(argumentuak.irteera_gpkg, driver="GPKG")

    bukaera = time.time()
    print("Amaituta. Denbora: {:.2f} segundo".format(bukaera - hasiera))


if __name__ == "__main__":
    main()
