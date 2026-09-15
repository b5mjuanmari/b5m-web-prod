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

import fiona
import geopandas as gpd
from shapely.geometry import MultiPolygon, shape
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


def garbitu_geometria(geom_diktategia):
    """
    Geometria-diktategi bat (GeoJSON motakoa) jaso eta baliogabeak diren
    eraztunak kentzen ditu (4 koordenatu-bikote baino gutxiago dituztenak,
    hau da, itxitako eraztun izan ez daitezkeenak).

    Kanpoko eraztuna baliogabea bada, poligono/azpi-poligono osoa baztertzen
    da. Emaitzarik ez badago, None itzultzen da.
    """
    mota = geom_diktategia.get("type")
    koordenatuak = geom_diktategia.get("coordinates")

    if mota == "Polygon":
        eraztunak = [e for e in koordenatuak if len(e) >= 4]
        if not eraztunak or len(eraztunak[0]) < 4:
            return None
        return {"type": "Polygon", "coordinates": eraztunak}

    if mota == "MultiPolygon":
        poligonoak = []
        for poligonoa in koordenatuak:
            eraztunak = [e for e in poligonoa if len(e) >= 4]
            if eraztunak and len(eraztunak[0]) >= 4:
                poligonoak.append(eraztunak)
        if not poligonoak:
            return None
        return {"type": "MultiPolygon", "coordinates": poligonoak}

    return geom_diktategia


def irakurri_gpkg(bidea):
    """
    GPKG fitxategia fiona bidez erregistroz erregistro irakurri, geometria
    bakoitza garbitu eta baliogabeak (konponezinak) diren erregistroak
    baztertu, gpd.read_file()-k egingo lukeen bezala guztiz huts egin
    beharrean.
    """
    erregistroak = []
    baztertuak = 0

    with fiona.open(bidea) as jatorria:
        crs = jatorria.crs
        for erregistroa in jatorria:
            geom_diktategia = erregistroa["geometry"]
            if geom_diktategia is None:
                baztertuak += 1
                continue

            geom_garbia = garbitu_geometria(geom_diktategia)
            if geom_garbia is None:
                baztertuak += 1
                continue

            try:
                geometria = shape(geom_garbia)
            except Exception:
                baztertuak += 1
                continue

            erregistro_berria = dict(erregistroa["properties"])
            erregistro_berria["geometry"] = geometria
            erregistroak.append(erregistro_berria)

    if baztertuak:
        print(
            "OHARRA: {} erregistro baztertu dira geometria baliogabea "
            "zutelako".format(baztertuak)
        )

    return gpd.GeoDataFrame(erregistroak, crs=crs)


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

    Emaitzak MultiPolygon bat izan badezake ere (adib. talde bereko bi
    poligono elkarrengandik bereizita geratzen badira), funtzio honek
    poligono bakunetan zatitzen du emaitza, eremuaren balioa poligono
    bakoitzari errepikatuz — horrela, irteerako geometriak beti Polygon
    dira, ez MultiPolygon.
    """
    disolbatuak = []
    balioak = []

    for balioa, taldea in gdf.groupby(eremua):
        handituak = [geom.buffer(EPS) for geom in taldea.geometry.values]
        geometria_batua = unary_union(handituak)
        geometria_garbia = geometria_batua.buffer(-EPS)

        if isinstance(geometria_garbia, MultiPolygon):
            for poligonoa in geometria_garbia.geoms:
                disolbatuak.append(poligonoa)
                balioak.append(balioa)
        else:
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
    gdf = irakurri_gpkg(argumentuak.sarrera_gpkg)

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
