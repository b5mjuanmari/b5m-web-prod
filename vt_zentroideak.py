#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poligono Shapefile batetik zentroideak sortu.

Erabilera:
    python3 zentroideak.py <sarrera.shp>

Deskribapena:
    - Sarrerako Shapefile-ak poligonoak dituela egiaztatzen du.
    - Poligono bakoitzaren zentroidea kalkulatzen du.
    - Zentroidea poligonoaren barruan ez badago, representative_point()
      erabiltzen du (beti barnean kokatzen den puntua).
    - Irteerako Shapefile-a sarrerakoaren izen bera du + "_p" atzizkia.
    - Aurretik existitzen bada, ezabatu eta berriro sortzen du.

Python 3.6+ bateragarria.
"""

import os
import sys
import time
import datetime
import geopandas as gpd

# =============================================================================
# PARAMETROAK
# =============================================================================

if len(sys.argv) != 2:
    print(
        "Erabilera: python3 {} <sarrera.shp>\n"
        "\n"
        "  <sarrera.shp>  Poligono Shapefile-aren bide osoa\n"
        "\n"
        "Adibidea:\n"
        "  python3 {prog} /home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles/r_oronimia.shp".format(
            sys.argv[0], prog=sys.argv[0]
        ),
        file=sys.stderr,
    )
    sys.exit(1)

INPUT_SHAPEFILE = sys.argv[1]

# =============================================================================
# LOG SISTEMA
# =============================================================================

def log_fitxategia_prestatu():
    """
    Log direktorioa eta fitxategia prestatu.
    - Direktorioa: scriptaren ondoan dagoen 'log/' karpeta.
    - Izena: <script_izena>_YYYYMMDD.log
    - Aurrekoa ezabatu existitzen bada.
    """
    script_izena = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    data_str     = datetime.datetime.now().strftime("%Y%m%d")
    log_dir      = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "log")

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "{}_{}.log".format(script_izena, data_str))

    if os.path.isfile(log_path):
        os.remove(log_path)

    return log_path


LOG_PATH = log_fitxategia_prestatu()
LOG_FH   = open(LOG_PATH, "w", buffering=1)


def _idatzi(lerro):
    """Lerro bat log fitxategira idatzi (timestamp-arekin)."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FH.write("[{}] {}\n".format(ts, lerro))
    LOG_FH.flush()


def log(mezua):
    _idatzi("[INFO]    {}".format(mezua))


def log_denbora(etiketa, hasiera):
    iraupena = int(time.time() - hasiera)
    orduak   = iraupena // 3600
    minutuak = (iraupena % 3600) // 60
    seg      = iraupena % 60
    _idatzi("[DENBORA] {} --> {:02d}:{:02d}:{:02d}".format(etiketa, orduak, minutuak, seg))


def errore(mezua):
    _idatzi("[ERRORE]  {}".format(mezua))
    LOG_FH.close()
    sys.exit(1)


# =============================================================================
# FUNTZIO LAGUNTZAILEAK
# =============================================================================

def shapefile_ezabatu(path):
    """Shapefile eta fitxategi osagarri guztiak ezabatu."""
    oinarria  = os.path.splitext(path)[0]
    luzapenak = [
        ".shp", ".dbf", ".shx", ".prj", ".cpg",
        ".sbn", ".sbx", ".qix", ".atx",
        ".fbn", ".fbx", ".ain", ".aih",
    ]
    ezabatutakoak = []
    for luz in luzapenak:
        fitx = oinarria + luz
        if os.path.isfile(fitx):
            os.remove(fitx)
            ezabatutakoak.append(os.path.basename(fitx))
    if ezabatutakoak:
        log("Aurrekoa ezabatua: {}".format(", ".join(ezabatutakoak)))


# =============================================================================
# PROZESU NAGUSIA
# =============================================================================

def main():
    hasiera_osoa = time.time()

    log("=" * 60)
    log("Zentroideen Shapefile sortzailea")
    log("Log fitxategia: {}".format(LOG_PATH))
    log("=" * 60)

    # --- 1. Sarrera egiaztatu ---
    input_path = os.path.abspath(INPUT_SHAPEFILE)

    if not os.path.isfile(input_path):
        errore("Sarrerako Shapefile ez da aurkitu: {}".format(input_path))

    log("Sarrera: {}".format(input_path))

    # --- 2. Irakurri ---
    log("-" * 60)
    log("Shapefile irakurtzen...")
    t = time.time()
    gdf = gpd.read_file(input_path)
    log_denbora("Shapefile irakurketa", t)
    log("Elementu kopurua: {}".format(len(gdf)))
    log("CRS: {}".format(gdf.crs))

    # --- 3. Poligonoak direla egiaztatu ---
    geom_motak = gdf.geometry.geom_type.unique().tolist()
    log("Geometria motak: {}".format(geom_motak))

    poligono_motak = {"Polygon", "MultiPolygon"}
    ez_poligonoak  = [m for m in geom_motak if m not in poligono_motak]
    if ez_poligonoak:
        errore(
            "Shapefile-ak ez ditu poligono geometriak bakarrik. "
            "Aurkitutako mota ez-onartuak: {}".format(ez_poligonoak)
        )
    log("Geometria egiaztapena ONGI: poligonoak dira.")

    # --- 4. Irteera bidea sortu (<izena>_p.shp) ---
    oinarria    = os.path.splitext(input_path)[0]
    output_path = oinarria + "_p.shp"
    log("Irteera: {}".format(output_path))

    # --- 5. Aurrekoa ezabatu existitzen bada ---
    shapefile_ezabatu(output_path)

    # --- 6. Zentroideak kalkulatu ---
    log("-" * 60)
    log("Zentroideak kalkulatzen...")
    t = time.time()
    zentroideak    = []
    kanpoan_kopuru = 0

    for idx, errenkada in gdf.iterrows():
        geom = errenkada.geometry
        if geom is None or geom.is_empty:
            zentroideak.append(None)
            continue

        zentroide = geom.centroid

        if geom.contains(zentroide):
            zentroideak.append(zentroide)
        else:
            # representative_point(): beti poligonoaren barruan kokatzen den puntua
            zentroideak.append(geom.representative_point())
            kanpoan_kopuru += 1

    log_denbora("Zentroideak kalkulatu", t)

    if kanpoan_kopuru > 0:
        log("OHARRA: {} zentroide poligonotik kanpo zeuden; "
            "representative_point() erabili da.".format(kanpoan_kopuru))
    else:
        log("Zentroide guztiak poligonoaren barruan daude.")

    # --- 7. GeoDataFrame berria sortu ---
    gdf_zentro = gdf.copy()
    gdf_zentro["geometry"] = zentroideak
    gdf_zentro = gdf_zentro[gdf_zentro.geometry.notnull()].reset_index(drop=True)

    # --- 8. Gorde ---
    log("-" * 60)
    log("Shapefile gordetzen...")
    t = time.time()
    gdf_zentro.to_file(output_path, encoding="utf-8")

    # .cpg fitxategia ezabatu (GeoPandas-ek sortzen du baina ez da beharrezkoa)
    cpg_path = os.path.splitext(output_path)[0] + ".cpg"
    if os.path.isfile(cpg_path):
        os.remove(cpg_path)
        log(".cpg fitxategia ezabatua.")

    log_denbora("Shapefile gorde", t)

    log("-" * 60)
    log("Irteerako Shapefile: {}".format(output_path))
    log("Zentroide kopurua:   {}".format(len(gdf_zentro)))
    log_denbora("PROZESU OSOA", hasiera_osoa)
    log("=" * 60)
    log("Prozesua ONGI amaitu da.")
    log("=" * 60)

    LOG_FH.close()


# =============================================================================
# SARRERA PUNTUA
# =============================================================================

if __name__ == "__main__":
    main()
