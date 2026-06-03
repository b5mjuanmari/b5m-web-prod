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
import geopandas as gpd

# =============================================================================
# ALDAGAIAK - Hemen alda ditzakezu parametroak
# =============================================================================

# Sarrerako eta irteerako Shapefile-ak
INPUT_SHAPEFILE = "/home5/SHP/TilesVT/MT_landcover_EJ_4E5.shp"
OUTPUT_SHAPEFILE = "./dat/vt_MT_landcover_4e5_5.shp"

# Orokortze parametroak
GENERALIZE_THRESHOLD = 5.0        # Orokortze tolerantzia (metroak)
GENERALIZE_METHOD    = "douglas"  # Metodoa: "douglas", "lang", "snakes", "hermite", "chaiken"

# Topologia garbiketa parametroak
SNAP_THRESHOLD  = 0.001   # Snap tolerantzia (metroak) - topologia sortzeko
AREA_THRESHOLD  = 1.0     # Azalera minimoa (metro koadroak) - zulo txikiak kentzeko

# GRASS GIS konfigurazioa
GRASS_EXECUTABLE = "grass"   # GRASS exekutagarriaren bidea (PATH-ean badago "grass" nahikoa)
GRASS_EPSG       = None      # None bada, input Shapefile-tik hartuko du automatikoki

# =============================================================================
# FUNTZIO LAGUNTZAILEAK
# =============================================================================

def segunduak_formateatu(segunduak):
    """Segunduak HH:MM:SS formatuan itzuli."""
    segunduak = int(segunduak)
    orduak   = segunduak // 3600
    minutuak = (segunduak % 3600) // 60
    seg      = segunduak % 60
    return "{:02d}:{:02d}:{:02d}".format(orduak, minutuak, seg)


def log(mezua):
    """Mezua pantailan erakutsi."""
    print("[INFO] {}".format(mezua), flush=True)


def log_denbora(etiketa, hasiera):
    """Urrats baten iraupena erakutsi."""
    iraupena = time.time() - hasiera
    print("[DENBORA] {} --> {}".format(etiketa, segunduak_formateatu(iraupena)), flush=True)


def errore(mezua):
    """Errore mezua erakutsi eta irten."""
    print("[ERRORE] {}".format(mezua), file=sys.stderr, flush=True)
    sys.exit(1)


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
    Irteera zuzenean pantailara bidalzen du (ez du memorian gordetzen).
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

    # Irteera zuzenean pantailara (ez capture_output)
    resultado = subprocess.run(cmd)
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
    log("=" * 60)

    # --- 1. Sarrerak egiaztatu ---
    t = time.time()
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
        if ret.returncode != 0:
            if ret.stdout:
                print(ret.stdout.decode("utf-8", errors="replace"))
            if ret.stderr:
                print(ret.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
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
MAPA_SARRERA="poligonoak_sarrera"
MAPA_GARBIA="poligonoak_garbia"
MAPA_OROKORTUA="poligonoak_orokortu"
OUTPUT_SHP="{output_path}"
SNAP_THRESHOLD="{snap}"
AREA_THRESHOLD="{area}"
GENERALIZE_THRESHOLD="{gen_thr}"
GENERALIZE_METHOD="{gen_met}"

# --- 1/5: Inportatu ---
echo "[GRASS] 1/5 - Shapefile inportatzen..."
T0=$(date +%s)
v.in.ogr input="$INPUT_SHP" output="$MAPA_SARRERA" --overwrite -o
T1=$(date +%s); echo "[DENBORA] v.in.ogr --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# --- 2/5: Snap ---
echo "[GRASS] 2/5 - Topologia garbitzen (snap)..."
T0=$(date +%s)
v.clean input="$MAPA_SARRERA" output="${{MAPA_SARRERA}}_snap" \\
    tool=snap threshold="$SNAP_THRESHOLD" --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean snap --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# --- 3/5: Topologia garbi ---
echo "[GRASS] 3/5 - Topologia garbitzen (break, rmdupl, rmarea, rmdangle)..."
T0=$(date +%s)
v.clean input="${{MAPA_SARRERA}}_snap" output="$MAPA_GARBIA" \\
    tool=break,rmdupl,rmarea,rmdangle \\
    threshold="0,$SNAP_THRESHOLD,$AREA_THRESHOLD,$SNAP_THRESHOLD" --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean topologia --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# --- 4/5: Orokortze ---
echo "[GRASS] 4/5 - Orokortze prozesua egiten ($GENERALIZE_METHOD, ${{GENERALIZE_THRESHOLD}}m)..."
T0=$(date +%s)
v.generalize input="$MAPA_GARBIA" output="$MAPA_OROKORTUA" \\
    method="$GENERALIZE_METHOD" threshold="$GENERALIZE_THRESHOLD" --overwrite
T1=$(date +%s); echo "[DENBORA] v.generalize --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# --- 5/5: Azken garbiketa ---
echo "[GRASS] 5/5 - Topologia azken garbiketa (zuloak konpondu)..."
T0=$(date +%s)
v.clean input="$MAPA_OROKORTUA" output="${{MAPA_OROKORTUA}}_final" \\
    tool=snap,break,rmdupl,rmarea \\
    threshold="$SNAP_THRESHOLD,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean azken --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# --- Exportatu ---
echo "[GRASS] Shapefile exportatzen..."
T0=$(date +%s)
v.out.ogr input="${{MAPA_OROKORTUA}}_final" output="$OUTPUT_SHP" \\
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
            errore("GRASS script-ean akatsa gertatu da. Ikusi goiko errore mezuak.")

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


# =============================================================================
# SARRERA PUNTUA
# =============================================================================

if __name__ == "__main__":
    main()
