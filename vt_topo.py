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
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon

# =============================================================================
# ALDAGAIAK - Hemen alda ditzakezu parametroak
# =============================================================================

# Sarrerako eta irteerako Shapefile-ak — komando-lerroko parametroetatik hartu
if len(sys.argv) != 5:
    print(
        "Erabilera: python3 {} <sarrera.shp> <irteera.shp> <tolerantzia_m> <area_min_m2>\n"
        "\n"
        "  <sarrera.shp>     Hasierako Shapefile-aren bide osoa (poligonoak)\n"
        "  <irteera.shp>     Bukaerako Shapefile-aren bide osoa\n"
        "  <tolerantzia_m>   Orokortze tolerantzia metroak (adib. 5, 50); 0 = orokortzerik ez\n"
        "  <area_min_m2>    Azalera minimoa m2 (adib. 1000); txikiagoak ezabatu eta ondokoarekin batu; 0 = ez ezabatu\n"
        "\n"
        "Adibidea:\n"
        "  python3 {prog} /home/juanmari/SCRIPTS/WEB_PROD/dat/vt_landcover_4e5.shp"
        " /home/juanmari/SCRIPTS/WEB_PROD/dat/vt_landcover_4e5_50.shp 50 1000".format(sys.argv[0], prog=sys.argv[0]),
        file=sys.stderr,
    )
    sys.exit(1)

INPUT_SHAPEFILE  = sys.argv[1]
OUTPUT_SHAPEFILE = sys.argv[2]

try:
    _thr = float(sys.argv[3])
    if _thr < 0:
        raise ValueError
except ValueError:
    print(
        "ERRORE: <tolerantzia_m> zenbaki positibo bat edo 0 izan behar da (0 = orokortzerik ez).",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    _area_min = float(sys.argv[4])
    if _area_min < 0:
        raise ValueError
except ValueError:
    print(
        "ERRORE: <area_min_m2> zenbaki positibo bat edo 0 izan behar da (0 = ez ezabatu).",
        file=sys.stderr,
    )
    sys.exit(1)

# Orokortze parametroak
GENERALIZE_THRESHOLD = _thr              # Orokortze tolerantzia (metroak) — argv[3]
AREA_MIN_M2          = _area_min         # Poligono txikienen azalera minimoa (m2) — argv[4]
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
    if GENERALIZE_THRESHOLD == 0:
        log("Orokortze tolerantzia: DESGAITUTA (0)")
    else:
        log("Orokortze tolerantzia: {} m".format(GENERALIZE_THRESHOLD))
    log("Orokortze metodoa:     {}".format(GENERALIZE_METHOD))
    if AREA_MIN_M2 > 0:
        log("Poligono min. azalera: {} m2 (txikiagoak ezabatu eta ondokoarekin batu)".format(AREA_MIN_M2))
    else:
        log("Poligono min. azalera: DESGAITUTA (0)")

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

        # Orokortze aktibo dagoen ala ez erabaki
        do_generalize = (GENERALIZE_THRESHOLD > 0)

        # Mapa izenak urrats bakoitzeko
        # Orokortzerik ez bada, M4 zuzenean M6 bihurtzen da
        script = """
# --- Aldagaiak ---
INPUT_SHP="{input_path}"
M0="p_00_sarrera"
M1="p_01_clean1"
M2="p_02_clean2"
M3="p_03_reklasif"
M4="p_04_dissolve"
M5="p_05_clean3"
M6="p_06_orokortu"
M7="p_07_final"
OUTPUT_SHP="{output_path}"
SNAP_THRESHOLD="{snap}"
AREA_THRESHOLD="{area}"
GENERALIZE_THRESHOLD="{gen_thr}"
GENERALIZE_METHOD="{gen_met}"
DO_GENERALIZE="{do_gen}"

# ---------------------------------------------------------------------------
# 1/N - Inportatu
# ---------------------------------------------------------------------------
echo "[GRASS] 1 - Shapefile inportatzen..."
T0=$(date +%s)
v.in.ogr input="$INPUT_SHP" output="$M0" snap=1e-08 --overwrite -o
T1=$(date +%s); echo "[DENBORA] v.in.ogr --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 2 - Lehen topologia garbiketa
# ---------------------------------------------------------------------------
echo "[GRASS] 2 - Lehen topologia garbiketa..."
T0=$(date +%s)
v.clean input="$M0" output="$M1" \
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 1. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 3 - Bigarren topologia garbiketa (iterazioa)
# ---------------------------------------------------------------------------
echo "[GRASS] 3 - Bigarren topologia garbiketa..."
T0=$(date +%s)
v.clean input="$M1" output="$M2" \
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 2. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 4 - LEGENDA_1 birsailkapena: type eremu berria sortu
#   v.db.addcolumn: type zutabea gehitu
#   v.db.update:    LEGENDA_1 balioaren arabera type bete
# ---------------------------------------------------------------------------
echo "[GRASS] 4 - LEGENDA_1 birsailkapena (type eremua sortzen)..."
T0=$(date +%s)
v.db.addcolumn map="$M2" columns="type varchar(20)"
v.db.update map="$M2" column="type" value="Urban"      where="LEGENDA_1 = 'Artifiziala'"
v.db.update map="$M2" column="type" value="Forestal"   where="LEGENDA_1 = 'Baso zuhaiztia'"
v.db.update map="$M2" column="type" value="Water"      where="LEGENDA_1 = 'Ingurune hezeak eta urazalak'"
v.db.update map="$M2" column="type" value="Meadow"     where="LEGENDA_1 = 'Laborantzak eta belardiak'"
v.db.update map="$M2" column="type" value="Rock" where="LEGENDA_1 = 'Landaretzagabeko edo urriko teselak'"
v.db.update map="$M2" column="type" value="Meadow"     where="LEGENDA_1 = 'Larrea'"
v.db.update map="$M2" column="type" value="Scrub"      where="LEGENDA_1 = 'Sastraka'"
# Egiaztatu: type NULL gelditu den erregistrorik ba ote dagoen
NULL_COUNT=$(db.select sql="SELECT COUNT(*) FROM $M2 WHERE type IS NULL" | tail -1)
echo "[GRASS] type=NULL duten erregistroak: $NULL_COUNT"
T1=$(date +%s); echo "[DENBORA] Birsailkapena --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 5 - Dissolve type eremuan oinarrituta
# ---------------------------------------------------------------------------
echo "[GRASS] 5 - Dissolve type eremuan..."
T0=$(date +%s)
v.dissolve input="$M2" column="type" output="$M3" --overwrite
T1=$(date +%s); echo "[DENBORA] v.dissolve --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 6 - Hirugarren topologia garbiketa (dissolve ostean)
# ---------------------------------------------------------------------------
echo "[GRASS] 6 - Topologia garbiketa dissolve ostean..."
T0=$(date +%s)
v.clean input="$M3" output="$M4" \
    tool=snap,break,bpol,rmdupl,rmbridge,rmarea \
    threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \
    --overwrite
T1=$(date +%s); echo "[DENBORA] v.clean 3. garbiketa --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

# ---------------------------------------------------------------------------
# 7 - Orokortze (DO_GENERALIZE=1 bada bakarrik)
# ---------------------------------------------------------------------------
if [ "$DO_GENERALIZE" = "1" ]; then
    echo "[GRASS] 7 - Orokortze ($GENERALIZE_METHOD, ${{GENERALIZE_THRESHOLD}}m)..."
    T0=$(date +%s)
    v.generalize input="$M4" output="$M5" \
        method="$GENERALIZE_METHOD" threshold="$GENERALIZE_THRESHOLD" --overwrite
    T1=$(date +%s); echo "[DENBORA] v.generalize --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"

    echo "[GRASS] 8 - Azken topologia garbiketa (orokortze ostean)..."
    T0=$(date +%s)
    v.clean input="$M5" output="$M6" \
        tool=snap,break,bpol,rmdupl,rmbridge,rmarea \
        threshold="$SNAP_THRESHOLD,0,0,$SNAP_THRESHOLD,$SNAP_THRESHOLD,$AREA_THRESHOLD" \
        --overwrite
    T1=$(date +%s); echo "[DENBORA] v.clean azken --> $(date -u -d @$(( T1 - T0 )) +%H:%M:%S)"
    MAPA_AZKEN="$M6"
else
    echo "[GRASS] 7 - Orokortze desgaituta (tolerantzia=0); urratsa saltatu."
    MAPA_AZKEN="$M4"
fi

# ---------------------------------------------------------------------------
# Exportatu (GeoPandas-ek egingo du eremu garbiketa ondoren)
# ---------------------------------------------------------------------------
echo "[GRASS] Exportatzen (aldi baterako fitxategia)..."
T0=$(date +%s)
v.out.ogr input="$MAPA_AZKEN" output="$OUTPUT_SHP" \
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
            do_gen="1" if do_generalize else "0",
        )

        ret = grass_exekutatu_script(
            GRASS_EXECUTABLE, gisdb, location, mapset, script
        )
        log_denbora("GRASS prozesu osoa", t)

        if ret != 0:
            errore("GRASS script-ean akatsa gertatu da. Ikusi log fitxategia: {}".format(LOG_PATH))

        # --- 7. Eremu garbiketa eta poligono txikiak ezabatu (GeoPandas) ---
        log("-" * 60)
        if not os.path.isfile(output_path):
            errore("Irteera Shapefile ez da sortu: {}".format(output_path))

        log("Eremu garbiketa GeoPandas bidez (fid, type)...")
        t = time.time()
        gdf_out = gpd.read_file(output_path)

        # type eremua egiaztatu
        if "type" not in gdf_out.columns:
            errore("'type' eremua ez da aurkitu irteerako Shapefile-an.")

        # --- 7a. Poligono txikiak ezabatu eta hutsuneak ondokoarekin bete ---
        if AREA_MIN_M2 > 0:
            log("Poligono txikiak ezabatzen ({} m2 baino txikiagoak)...".format(AREA_MIN_M2))
            t2 = time.time()
            gdf_out = gdf_out.reset_index(drop=True)
            gdf_out["_area"] = gdf_out.geometry.area

            txiki_mask = gdf_out["_area"] < AREA_MIN_M2
            n_txiki = txiki_mask.sum()
            log("  Ezabatzeko poligonoak: {}".format(n_txiki))

            if n_txiki > 0:
                # Sindex erabiliz ondoko poligono handiena aurkitu eta type hartu
                # Iterazio bat baino gehiago behar da poligono txikien kate-efektua
                # konpontzeko (txiki bat ezabatu -> ondokoa txiki bihurtu)
                aldaketa = True
                while aldaketa:
                    aldaketa = False
                    gdf_out = gdf_out.reset_index(drop=True)
                    gdf_out["_area"] = gdf_out.geometry.area
                    txiki_idx = gdf_out.index[gdf_out["_area"] < AREA_MIN_M2].tolist()
                    if not txiki_idx:
                        break

                    # Spatial index eraiki
                    sindex = gdf_out.sindex

                    ezabatu_idx = []
                    for idx in txiki_idx:
                        geom = gdf_out.at[idx, "geometry"]
                        if geom is None or geom.is_empty:
                            ezabatu_idx.append(idx)
                            continue

                        # Kandidatoak: geometriarekin ukitzen duten poligonoak
                        kandidatuak = list(sindex.intersection(geom.bounds))
                        kandidatuak = [
                            i for i in kandidatuak
                            if i != idx
                            and gdf_out.at[i, "geometry"] is not None
                            and not gdf_out.at[i, "geometry"].is_empty
                            and gdf_out.at[i, "geometry"].touches(geom)
                        ]

                        if not kandidatuak:
                            # Ukitzerik ez bada, intersects probatu
                            kandidatuak = [
                                i for i in list(sindex.intersection(geom.bounds))
                                if i != idx
                                and gdf_out.at[i, "geometry"] is not None
                                and not gdf_out.at[i, "geometry"].is_empty
                                and gdf_out.at[i, "geometry"].intersects(geom)
                                and gdf_out.at[i, "_area"] >= AREA_MIN_M2
                            ]

                        if not kandidatuak:
                            # Ezin da ondokorik aurkitu; ezabatu hutsik
                            ezabatu_idx.append(idx)
                            continue

                        # Azaleraren arabera kandidatu handiena aukeratu
                        ondokoa = max(kandidatuak, key=lambda i: gdf_out.at[i, "_area"])

                        # type hartu ondokotik eta geometria batu
                        tipo_berria = gdf_out.at[ondokoa, "type"]
                        geom_berria = gdf_out.at[ondokoa, "geometry"].union(geom)
                        gdf_out.at[ondokoa, "geometry"] = geom_berria
                        gdf_out.at[ondokoa, "type"]     = tipo_berria
                        ezabatu_idx.append(idx)
                        aldaketa = True

                    if ezabatu_idx:
                        gdf_out = gdf_out.drop(index=ezabatu_idx).reset_index(drop=True)
                        gdf_out["_area"] = gdf_out.geometry.area

            gdf_out = gdf_out.drop(columns=["_area"])
            log("  Poligono kopurua ezabatu ostean: {}".format(len(gdf_out)))
            log_denbora("Poligono txikiak ezabatu", t2)

        # --- 7b. Hutsune egiaztapena eta konponketa (interior rings) ---
        # Interior ring bat poligono baten barruan dagoen zulo geometrikoa da.
        # Aurkitzen badira: zuloa betetzen duen ondoko poligonora gehitu (union),
        # eta poligono berria ring-rik gabe gorde.
        log("Hutsune egiaztapena egiten (interior rings)...")
        t_huts = time.time()

        gdf_out = gdf_out.reset_index(drop=True)
        sindex  = gdf_out.sindex
        zulo_total    = 0
        zulo_konpondu = 0

        for i in range(len(gdf_out)):
            geom = gdf_out.at[i, "geometry"]
            if geom is None or geom.is_empty:
                continue

            # Poligono guztiak lortu (Polygon edo MultiPolygon)
            poli_lista = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
            zulo_kopuru_i = sum(len(p.interiors) for p in poli_lista)
            if zulo_kopuru_i == 0:
                continue

            zulo_total += zulo_kopuru_i
            geom_berri_lista = []

            for poly in poli_lista:
                if len(poly.interiors) == 0:
                    geom_berri_lista.append(poly)
                    continue

                # Interior ring bakoitza ondoko poligonorik handiena aurkitu eta eman
                for ring in poly.interiors:
                    zulo_geom = Polygon(ring)
                    kandidatuak = [
                        j for j in sindex.intersection(zulo_geom.bounds)
                        if j != i
                        and gdf_out.at[j, "geometry"] is not None
                        and not gdf_out.at[j, "geometry"].is_empty
                        and gdf_out.at[j, "geometry"].intersects(zulo_geom)
                    ]
                    if kandidatuak:
                        ondokoa = max(
                            kandidatuak,
                            key=lambda j: gdf_out.at[j, "geometry"].intersection(zulo_geom).area
                        )
                        gdf_out.at[ondokoa, "geometry"] = (
                            gdf_out.at[ondokoa, "geometry"].union(zulo_geom)
                        )
                        zulo_konpondu += 1

                # Poligono berria exterior bakarrik (interior ring-rik gabe)
                geom_berri_lista.append(Polygon(poly.exterior))

            # Geometria eguneratu
            if len(geom_berri_lista) == 1:
                gdf_out.at[i, "geometry"] = geom_berri_lista[0]
            else:
                gdf_out.at[i, "geometry"] = MultiPolygon(geom_berri_lista)

        if zulo_total == 0:
            log("  Interior ring-rik ez da aurkitu.")
        else:
            log("  {} interior ring aurkitu, {} konponduta.".format(zulo_total, zulo_konpondu))
            if zulo_total != zulo_konpondu:
                log("  ABISUA: {} interior ring ezin izan da konpondu "
                    "(ondoko poligonorik gabe).".format(zulo_total - zulo_konpondu))

        log_denbora("Hutsune egiaztapena", t_huts)

        # --- 7c. fid sortu eta eremu ordena ezarri ---
        gdf_out["fid"] = range(1, len(gdf_out) + 1)
        gdf_out = gdf_out[["fid", "type", "geometry"]]

        # Berriro gorde (cat eta beste eremu guztiak kenduta)
        gdf_out.to_file(output_path, encoding="utf-8")
        log_denbora("Eremu garbiketa osoa", t)

        log("-" * 60)
        log("Emaitza Shapefile: {}".format(output_path))
        log("Poligono kopurua:  {}".format(len(gdf_out)))
        log("Eremua:            fid, type")
        log("CRS:               {}".format(gdf_out.crs))
        log("=" * 60)
        log("Prozesua ONGI amaitu da.")
        log("=" * 60)

    finally:
        # --- 8. Aldi baterako GRASS datu-basea ezabatu ---
        log("GRASS datu-base aldi baterakoa ezabatzen: {}".format(gisdb))
        shutil.rmtree(gisdb, ignore_errors=True)
        log("=" * 60)
        log_denbora("PROZESU OSOA", hasiera_osoa)
        log("=" * 60)
        LOG_FH.close()


# =============================================================================
# SARRERA PUNTUA
# =============================================================================

if __name__ == "__main__":
    main()
