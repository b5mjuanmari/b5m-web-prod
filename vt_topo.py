#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shapefile-en topologia sortu eta orokortze prozesua egin GRASS GIS bidez.

Deskribapena:
    1. Hasierako Shapefile bat irakurri (poligonoak)
    2. GRASS GIS datu-base batean inportatu
    3. Topologia sortu (v.clean)
    4. Orokortze prozesua egin (v.generalize) - zulorik gabe
    5. Emaitza Shapefile gisa exportatu

Python 3.6+ bateragarria.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import time
import datetime
import geopandas as gpd

# =============================================================================
# ALDAGAIAK - Hemen alda ditzakezu parametroak
# =============================================================================

# Sarrerako eta irteerako Shapefile-ak
INPUT_SHAPEFILE  = "/home5/SHP/TilesVT/vt_landcover_4e5.shp"
OUTPUT_SHAPEFILE = "/home/juanmari/SCRIPTS/WEB_PROD/dat/vt_landcover_4e5_50.shp"

# Orokortze parametroak
GENERALIZE_THRESHOLD = 50.0       # Orokortze tolerantzia (metroak)
GENERALIZE_METHOD    = "douglas"  # Metodoa: "douglas", "lang", "snakes", "hermite", "chaiken"

# Topologia garbiketa parametroak
SNAP_THRESHOLD = 0.001  # Snap tolerantzia (metroak) - topologia sortzeko
AREA_THRESHOLD = 1.0    # Azalera minimoa (metro koadroak) - zulo txikiak kentzeko

# GRASS GIS konfigurazioa
GRASS_EXECUTABLE = "grass"  # GRASS exekutagarriaren bidea (PATH-ean badago "grass" nahikoa)
GRASS_EPSG       = None     # None bada, input Shapefile-tik hartuko du automatikoki

# =============================================================================
# LOG SISTEMA - Hasieraketa
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

    # Direktorioa sortu ez bada existitzen
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "{}_{}.log".format(script_izena, data_str))

    # Aurrekoa ezabatu existitzen bada
    if os.path.isfile(log_path):
        os.remove(log_path)

    return log_path


# Log fitxategia global gisa ireki (scriptaren hasieran)
LOG_PATH = log_fitxategia_prestatu()
LOG_FH   = open(LOG_PATH, "w", buffering=1)  # buffering=1: lerro-buffering


def _idatzi(lerro):
    """Lerro bat log fitxategira idatzi (timestamp-arekin)."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FH.write("[{}] {}\n".format(ts, lerro))
    LOG_FH.flush()


def log(mezua):
    """Mezu arrunta log fitxategira."""
    _idatzi("[INFO]    {}".format(mezua))


def log_denbora(etiketa, hasiera):
    """Urrats baten iraupena log fitxategira."""
    iraupena = int(time.time() - hasiera)
    orduak   = iraupena // 3600
    minutuak = (iraupena % 3600) // 60
    seg      = iraupena % 60
    _idatzi("[DENBORA] {} --> {:02d}:{:02d}:{:02d}".format(etiketa, orduak, minutuak, seg))


def errore(mezua):
    """Errore mezua log fitxategira idatzi eta irten."""
    _idatzi("[ERRORE]  {}".format(mezua))
    LOG_FH.close()
    sys.exit(1)


# =============================================================================
# FUNTZIO LAGUNTZAILEAK
# =============================================================================

def subprocess_run_compat(cmd):
    """
    subprocess.run() Python 3.6rekin bateragarria.
    capture_output=True ez dago 3.6an; stdout/stderr=PIPE erabiltzen du.
    """
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def grass_exekutatu_script(grass_bin, gisdb, location, mapset, script_edukia):
    """
    Bash script bat GRASS ingurune batean exekutatu.
    stdout eta stderr log fitxategira bideratzen dira.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False, prefix="grass_script_"
    ) as f:
        f.write("#!/bin/bash\nset -e\n")
        f.write(script_edukia)
        script_path = f.name

    os.chmod(script_path, 0o755)

    cmd = [
        grass_bin,
        os.path.join(gisdb, location, mapset),
        "--exec",
        "bash",
        script_path,
    ]

    # stdout eta stderr log fitxategira bideratu zuzenean
    resultado = subprocess.run(
        cmd,
        stdout=LOG_FH,
        stderr=LOG_FH,
    )
    os.unlink(script_path)
    return resultado.returncode


def epsg_lortu(shp_bidea):
    """Shapefile-aren EPSG kodea lortu GeoPandas bidez."""
    gdf = gpd.read_file(shp_bidea)
    if gdf.crs is None:
        errore("Sarrerako Shapefile-ak ez du proiekziorik (CRS). Mesedez zehaztu EPSG kodea.")
    epsg = gdf.crs.to_epsg()
    if epsg is None:
        log("EPSG kodea ez da aurkitu, proiektua WKT bidez sortuko da.")
        return None, gdf.crs.to_wkt()
    log("CRS detektatua: EPSG:{}".format(epsg))
    return epsg, None


def shapefile_ezabatu(output_path):
    """
    Irteera Shapefile eta fitxategi osagarri guztiak ezabatu (existitzen badira).
    Shapefile batek .shp, .dbf, .shx, .prj, .cpg eta beste batzuk izan ditzake.
    """
    oinarri_izena = os.path.splitext(output_path)[0]
    luzapenak = [
        ".shp", ".dbf", ".shx", ".prj", ".cpg",
        ".sbn", ".sbx", ".qix", ".atx",
        ".fbn", ".fbx", ".ain", ".aih",
    ]
    ezabatutakoak = []
    for luzapena in luzapenak:
        fitx = oinarri_izena + luzapena
        if os.path.isfile(fitx):
            os.remove(fitx)
            ezabatutakoak.append(os.path.basename(fitx))

    if ezabatutakoak:
        log("Irteera Shapefile ezabatua (sortu aurretik): {}".format(", ".join(ezabatutakoak)))
    else:
        log("Irteera Shapefile ez zegoen aurretik; ez da ezer ezabatu.")


# =============================================================================
# PROZESU NAGUSIA
# =============================================================================

def main():
    hasiera_osoa = time.time()

    log("=" * 60)
    log("GRASS GIS bidezko topologia eta orokortze prozesua")
    log("Log fitxategia: {}".format(LOG_PATH))
    log("=" * 60)

    # --- 1. Sarrerak egiaztatu ---
    input_path  = os.path.abspath(INPUT_SHAPEFILE)
    output_path = os.path.abspath(OUTPUT_SHAPEFILE)

    if not os.path.isfile(input_path):
        errore("Sarrerako Shapefile ez da aurkitu: {}".format(input_path))

    log("Sarrera:  {}".format(input_path))
    log("Irteera:  {}".format(output_path))
    log("Orokortze tolerantzia: {} m".format(GENERALIZE_THRESHOLD))
    log("Orokortze metodoa:     {}".format(GENERALIZE_METHOD))

    # --- 2. EPSG lortu ---
    log("-" * 60)
    log("CRS irakurtzen...")
    t = time.time()
    if GRASS_EPSG is not None:
        epsg = GRASS_EPSG
        wkt  = None
        log("CRS eskuz zehaztuta: EPSG:{}".format(epsg))
    else:
        epsg, wkt = epsg_lortu(input_path)
    log_denbora("CRS irakurketa", t)

    # --- 3. GRASS datu-base aldi baterako sortu ---
    gisdb    = tempfile.mkdtemp(prefix="grass_db_")
    location = "lan_location"
    mapset   = "PERMANENT"
    log("-" * 60)
    log("GRASS datu-base aldi baterakoa: {}".format(gisdb))

    try:
        # --- 4. Location sortu ---
        log("-" * 60)
        log("GRASS location sortzen...")
        t = time.time()
        if epsg is not None:
            cmd_loc = [
                GRASS_EXECUTABLE, "-c", "EPSG:{}".format(epsg),
                os.path.join(gisdb, location),
                "-e",
            ]
        else:
            wkt_file = os.path.join(gisdb, "crs.wkt")
            with open(wkt_file, "w") as f:
                f.write(wkt)
            cmd_loc = [
                GRASS_EXECUTABLE, "-c", wkt_file,
                os.path.join(gisdb, location),
                "-e",
            ]

        ret = subprocess_run_compat(cmd_loc)
        # Location-en irteera log-era idatzi
        if ret.stdout:
            LOG_FH.write(ret.stdout.decode("utf-8", errors="replace"))
        if ret.stderr:
            LOG_FH.write(ret.stderr.decode("utf-8", errors="replace"))
        LOG_FH.flush()

        if ret.returncode != 0:
            errore("GRASS location sortzean akatsa gertatu da.")
        log("Location sortua.")
        log_denbora("Location sorrera", t)

        # --- 5. Irteera Shapefile ezabatu (v.out.ogr baino LEHEN) ---
        log("-" * 60)
        shapefile_ezabatu(output_path)

        # --- 6. Prozesua GRASS barnean exekutatu ---
        log("-" * 60)
        log("GRASS prozesua abiatzen...")
        t = time.time()

        script = """
# --- Aldagaiak ---
INPUT_SHP="{input_path}"
M0="p_00_sarrera"
M1="p_01_snap1"
M2="p_02_clean1"
M3="p_03_snap2"
M4="p_04_clean2"
M5="p_05_orokortu"
M6="p_06_final"
OUTPUT_SHP="{output_path}"
SNAP_THRESHOLD="{snap}"
AREA_THRESHOLD="{area}"
GENERALIZE_THRESHOLD="{gen_thr}"
GENERALIZE_METHOD="{gen_met}"

# ---------------------------------------------------------------------------
# 1/8 - Inportatu
# ---------------------------------------------------------------------------
echo "[GRASS] 1/8 - Shapefile inportatzen..."
T0=$(date +%s)
v.in.ogr input="$INPUT_SHP" output="$M0" snap=1e-08 --overwrite -o
T1=$(date +%s); echo "[DENBORA] v.in.ogr --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 2/8 - Lehen garbiketa: snap + break + bpol + rmdupl + rmbridge + rmarea
#   snap     : puntu hurbilak batu
#   break    : gurutzaketak apurtu
#   bpol     : boundary poligonoak konpondu (GRASS 7.4.0-rekin bateragarria)
#   rmdupl   : lerro bikoiztuak kendu
#   rmbridge : zubiak kendu (bi poligonoaren arteko lerro meheak)
#   rmarea   : azalera txikiegiko poligonoak kendu
# Oharra: rmcap GRASS 7.8+ baino ez dago; hemen ez da erabiltzen.
# ---------------------------------------------------------------------------
echo "[GRASS] 2/8 - Lehen topologia garbiketa (snap+break+bpol+rmdupl+rmbridge+rmarea)..."
T0=$(date +%s)
v.clean input="$M0" output="$M1" \\
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \\
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \\
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 1. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 3/8 - Bigarren garbiketa iterazioa (lehen pasean agertutako arazo berriak)
# ---------------------------------------------------------------------------
echo "[GRASS] 3/8 - Bigarren topologia garbiketa (iterazioa)..."
T0=$(date +%s)
v.clean input="$M1" output="$M2" \\
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \\
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \\
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 2. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 4/8 - v.dissolve: topologia sendotu eta area "hilak" ezabatu
#   Atributu bereko area guztiak batu — centroide problemak konpontzen ditu.
#   cat zutabea erabiltzen dugu (beti existitzen da).
# ---------------------------------------------------------------------------
echo "[GRASS] 4/8 - Topologia sendotzen (v.dissolve)..."
T0=$(date +%s)
v.dissolve input="$M2" output="$M3" --overwrite
T1=$(date +%s); echo "[DENBORA] v.dissolve --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 5/8 - Hirugarren garbiketa dissolve ondoren sortutako arazoetarako
# ---------------------------------------------------------------------------
echo "[GRASS] 5/8 - Hirugarren topologia garbiketa (dissolve ostean)..."
T0=$(date +%s)
v.clean input="$M3" output="$M4" \\
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \\
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \\
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 3. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 6/8 - Orokortze
# ---------------------------------------------------------------------------
echo "[GRASS] 6/8 - Orokortze prozesua ($GENERALIZE_METHOD, ${{GENERALIZE_THRESHOLD}}m)..."
T0=$(date +%s)
v.generalize input="$M4" output="$M5" \\
    method="$GENERALIZE_METHOD" threshold="$GENERALIZE_THRESHOLD" --overwrite
T1=$(date +%s); echo "[DENBORA] v.generalize --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 7/8 - Azken garbiketa (orokortze ondoren sor daitezkeen arazoak)
# ---------------------------------------------------------------------------
echo "[GRASS] 7/8 - Azken topologia garbiketa (orokortze ostean)..."
T0=$(date +%s)
v.clean input="$M5" output="$M6" \\
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \\
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \\
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean azken --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 8/8 - Exportatu
# ---------------------------------------------------------------------------
echo "[GRASS] 8/8 - Shapefile exportatzen..."
T0=$(date +%s)
v.out.ogr input="$M6" output="$OUTPUT_SHP" \\
    format=ESRI_Shapefile type=area --overwrite
T1=$(date +%s); echo "[DENBORA] v.out.ogr --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

echo "[GRASS] Prozesua amaituta."
""".format(
            input_path=input_path,
            output_path=output_path,
            snap=SNAP_THRESHOLD,
            area=AREA_THRESHOLD,
            gen_thr=GENERALIZE_THRESHOLD,
            gen_met=GENERALIZE_METHOD,
        )

        ret = grass_exekutatu_script(
            GRASS_EXECUTABLE, gisdb, location, mapset, script
        )
        log_denbora("GRASS prozesu osoa", t)

        if ret != 0:
            errore("GRASS script-ean akatsa gertatu da. Ikusi log fitxategia: {}".format(LOG_PATH))

        # --- 7. Emaitza egiaztatu ---
        log("-" * 60)
        if not os.path.isfile(output_path):
            errore("Irteera Shapefile ez da sortu: {}".format(output_path))

        t = time.time()
        gdf_out = gpd.read_file(output_path)
        log_denbora("Emaitza irakurketa", t)

        log("-" * 60)
        log("Emaitza Shapefile: {}".format(output_path))
        log("Poligono kopurua:  {}".format(len(gdf_out)))
        log("CRS:               {}".format(gdf_out.crs))
        log_denbora("PROZESU OSOA", hasiera_osoa)
        log("=" * 60)
        log("Prozesua ONGI amaitu da.")
        log("=" * 60)

    finally:
        # --- 8. Aldi baterako GRASS datu-basea ezabatu ---
        log("GRASS datu-base aldi baterakoa ezabatzen: {}".format(gisdb))
        shutil.rmtree(gisdb, ignore_errors=True)
        LOG_FH.close()


# =============================================================================
# SARRERA PUNTUA
# =============================================================================

if __name__ == "__main__":
    main()
