#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direktorio bateko «r_» kateaz hasten diren Shapefile guztietatik
zentroideak sortu (poligonoak dituztenak bakarrik).

Erabilera:
    python3 zentroideak.py <direktorioa>

Deskribapena:
    - Direktorioko «r_»-z hasten diren .shp fitxategi guztiak zerrendatzen ditu.
    - Poligonoak dituzten Shapefile-ak prozesatzen ditu.
    - Poligono bakoitzaren zentroidea kalkulatzen du; zentroidea poligonoaren
      barruan ez badago, representative_point() erabiltzen du.
    - Irteerako Shapefile-a sarrerakoaren izen bera du + "_p" atzizkia,
      direktorio berean. Aurretik existitzen bada, ezabatu eta berriro sortzen du.

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
        "Erabilera: python3 {} <direktorioa>\n"
        "\n"
        "  <direktorioa>  «r_»-z hasten diren Shapefile-ak dituen direktorioa\n"
        "\n"
        "Adibidea:\n"
        "  python3 {prog} /home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles".format(
            sys.argv[0], prog=sys.argv[0]
        ),
        file=sys.stderr,
    )
    sys.exit(1)

INPUT_DIR = sys.argv[1]

# =============================================================================
# LOG SISTEMA
# =============================================================================

def log_fitxategia_prestatu():
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
        log("  Aurrekoa ezabatua: {}".format(", ".join(ezabatutakoak)))


def zentroideak_sortu(input_path):
    """
    Shapefile bat prozesatu eta zentroideen Shapefile-a sortu.
    Itzultzen du: True (ongi), False (ez da poligonorik, saltatu).
    """
    oinarria    = os.path.splitext(input_path)[0]
    output_path = oinarria + "_p.shp"

    # Irakurri
    t = time.time()
    gdf = gpd.read_file(input_path, encoding="iso-8859-1")
    log("  Elementu kopurua: {} | CRS: {}".format(len(gdf), gdf.crs))
    log_denbora("  Irakurketa", t)

    # Poligonoak dituela egiaztatu
    geom_motak     = gdf.geometry.geom_type.unique().tolist()
    poligono_motak = {"Polygon", "MultiPolygon"}
    ez_poligonoak  = [m for m in geom_motak if m not in poligono_motak]

    if ez_poligonoak:
        log("  SALTATU: ez ditu poligono geometriak bakarrik "
            "(aurkitutakoak: {}).".format(geom_motak))
        return False

    # Irteera aurrekoa ezabatu
    shapefile_ezabatu(output_path)

    # Zentroideak kalkulatu
    t = time.time()
    zentroideak    = []
    kanpoan_kopuru = 0

    for _, errenkada in gdf.iterrows():
        geom = errenkada.geometry
        if geom is None or geom.is_empty:
            zentroideak.append(None)
            continue

        zentroide = geom.centroid
        if geom.contains(zentroide):
            zentroideak.append(zentroide)
        else:
            zentroideak.append(geom.representative_point())
            kanpoan_kopuru += 1

    log_denbora("  Zentroideak kalkulatu", t)

    if kanpoan_kopuru > 0:
        log("  OHARRA: {} zentroide kanpoan; representative_point() "
            "erabili da.".format(kanpoan_kopuru))

    # GeoDataFrame berria sortu eta gorde
    gdf_zentro             = gdf.copy()
    gdf_zentro["geometry"] = zentroideak
    gdf_zentro             = gdf_zentro[gdf_zentro.geometry.notnull()].reset_index(drop=True)

    t = time.time()
    gdf_zentro.to_file(output_path, encoding="iso-8859-1")

    # .cpg fitxategia ezabatu (ez dugu nahi)
    cpg_path = oinarria + "_p.cpg"
    if os.path.isfile(cpg_path):
        os.remove(cpg_path)

    # DBF fitxategiaren 29. byte-a (LDID) 0x57 jarri -> ISO-8859-1/Windows-1252
    dbf_path = oinarria + "_p.dbf"
    if os.path.isfile(dbf_path):
        with open(dbf_path, "r+b") as _dbf:
            _dbf.seek(29)
            _dbf.write(b"\x57")

    log_denbora("  Gorde", t)
    log("  Irteera: {}".format(output_path))
    return True


# =============================================================================
# PROZESU NAGUSIA
# =============================================================================

def main():
    hasiera_osoa = time.time()

    log("=" * 60)
    log("Zentroideen batch prozesadorea (r_*.shp)")
    log("Log fitxategia: {}".format(LOG_PATH))
    log("=" * 60)

    # --- 1. Direktorioa egiaztatu ---
    input_dir = os.path.abspath(INPUT_DIR)
    if not os.path.isdir(input_dir):
        errore("Direktorioa ez da aurkitu: {}".format(input_dir))

    log("Direktorioa: {}".format(input_dir))

    # --- 2. «r_»-z hasten diren Shapefile-ak zerrendatu ---
    log("-" * 60)
    log("«r_»-z hasten diren Shapefile-ak bilatzen...")

    shp_fitxategiak = sorted([
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.startswith("r_") and f.lower().endswith(".shp")
    ])

    if not shp_fitxategiak:
        errore("Ez da «r_»-z hasten den Shapefile-rik aurkitu: {}".format(input_dir))

    log("Aurkitutako Shapefile-ak: {}".format(len(shp_fitxategiak)))
    for shp in shp_fitxategiak:
        log("  {}".format(os.path.basename(shp)))

    # --- 3. Bakoitza prozesatu ---
    log("-" * 60)
    prozesatutakoak = 0
    saltatutakoak   = 0

    for i, shp_path in enumerate(shp_fitxategiak, start=1):
        log("[{}/{}] Prozesatzen: {}".format(i, len(shp_fitxategiak),
                                              os.path.basename(shp_path)))
        t_shp = time.time()

        ongi = zentroideak_sortu(shp_path)

        if ongi:
            prozesatutakoak += 1
        else:
            saltatutakoak += 1

        log_denbora("  [{}/{}] Denbora".format(i, len(shp_fitxategiak)), t_shp)
        log("-" * 60)

    # --- 4. Laburpena ---
    log("LABURPENA:")
    log("  Aurkitutako Shapefile-ak:  {}".format(len(shp_fitxategiak)))
    log("  Prozesatutakoak:           {}".format(prozesatutakoak))
    log("  Saltatutakoak (ez-polig.): {}".format(saltatutakoak))
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
