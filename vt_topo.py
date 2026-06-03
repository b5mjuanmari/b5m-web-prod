#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import shutil
import time
import glob
import geopandas as gpd
from datetime import timedelta

# ==================================================
# ALDAGAI KONFIGURAGARRIAK
# ==================================================

# Sarrera eta irteerako fitxategien izenak
INPUT_SHAPEFILE = "/home5/SHP/TilesVT/MT_landcover_EJ_4E5.shp"
OUTPUT_SHAPEFILE = "./dat/vt_MT_landcover_4e5_5.shp"

# Orokortze parametroak (metrotan)
SIMPLIFICATION_TOLERANCE = 5.0  # 5 metroko sinplifikazioa

# GRASS GIS ezarpenak - ZURE INSTALAZIOERAKO EGOKITUTA
GRASS_BASE = "/usr/lib/grass74"  # ZURE GRASS 7.4 BIDEA
GRASS_DATABASE = tempfile.mkdtemp()  # GRASS LOCATION sortzeko direktorioa
GRASS_LOCATION = "proiektua"
GRASS_MAPSET = "permanent"

# ==================================================
# DENBORA KONTAGAILLUAREN FUNTZIOAK
# ==================================================

def format_time(seconds):
    """Segundoak HH:MM:SS formatuan bihurtu"""
    return str(timedelta(seconds=int(seconds)))

class DenboraKontagailua:
    """Denbora neurtzeko klasea HH:MM:SS formatuan emaitza erakusteko"""

    def __init__(self, izena="Prozesua"):
        self.izena = izena
        self.hasiera_globala = None
        self.bukaera_globala = None
        self.urratsak = []

    def hasi_prozesu_osoa(self):
        """Prozesu osoaren hasiera markatu"""
        self.hasiera_globala = time.time()
        print(f"\n{'='*60}")
        print(f">>> {self.izena} HASIERA - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

    def amaitu_prozesu_osoa(self):
        """Prozesu osoaren bukaera markatu eta denbora totala erakutsi"""
        self.bukaera_globala = time.time()
        denbora_totala = self.bukaera_globala - self.hasiera_globala
        denbora_formateatua = format_time(denbora_totala)

        print(f"\n{'='*60}")
        print(f">>> {self.izena} AMAITU")
        print(f"    Denbora totala: {denbora_formateatua}")
        print(f"    Bukaera: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Urratsen laburpena erakutsi
        self.erakutsi_laburpena()

    def urratsa_hasi(self, urrats_izena):
        """Urrats baten hasiera markatu"""
        hasiera = time.time()
        self.urratsak.append({
            'izena': urrats_izena,
            'hasiera': hasiera,
            'bukaera': None
        })
        print(f"    [*] {urrats_izena}...", end=' ', flush=True)
        return hasiera

    def urratsa_amaitu(self):
        """Azken urratsa amaitu eta denbora erakutsi"""
        if self.urratsak and self.urratsak[-1]['bukaera'] is None:
            bukaera = time.time()
            self.urratsak[-1]['bukaera'] = bukaera
            hasiera = self.urratsak[-1]['hasiera']
            iraupena = bukaera - hasiera
            denbora_formateatua = format_time(iraupena)
            print(f"[DONE - {denbora_formateatua}]")

    def erakutsi_laburpena(self):
        """Urrats guztien denbora laburpena erakutsi"""
        print("\nDENBORA LABURPENA:")
        print("-" * 50)
        for urratsa in self.urratsak:
            if urratsa['bukaera']:
                iraupena = urratsa['bukaera'] - urratsa['hasiera']
                denbora_formateatua = format_time(iraupena)
                print(f"    - {urratsa['izena']:30} {denbora_formateatua}")
        print("-" * 50)

# ==================================================
# FITXATEGIAK KUDEATZEKO FUNTZIOAK
# ==================================================

def delete_shapefile_if_exists(shapefile_path):
    """Shapefile bat existitzen bada ezabatu (shp, shx, dbf, prj, cpg, qpj)"""

    if not os.path.exists(shapefile_path):
        return False

    base_path = os.path.splitext(shapefile_path)[0]
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj', '.shp.xml']

    deleted_files = []
    for ext in extensions:
        file_path = base_path + ext
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_files.append(os.path.basename(file_path))

    if deleted_files:
        print(f"    Ezabatutako fitxategiak: {', '.join(deleted_files)}")

    return True

def delete_grass_output_if_exists(shapefile_path):
    """GRASSek sortutako irteera fitxategiak ezabatu (izen bereko beste formatuak)"""

    if not os.path.exists(shapefile_path):
        return False

    # Shapefile ezabatu
    delete_shapefile_if_exists(shapefile_path)

    # GRASSek sortutako beste fitxategi batzuk
    base_path = os.path.splitext(shapefile_path)[0]
    additional_files = [
        f"{base_path}.shp.xml",
        f"{base_path}.qix",
        f"{base_path}.fix",
    ]

    for file_path in additional_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"    Ezabatutako fitxategia: {os.path.basename(file_path)}")

    return True

# ==================================================
# GRASS INGURUNEA KONFIGURATU
# ==================================================

def setup_grass_environment():
    """GRASS ingurunearen aldagaiak konfiguratu zure instalaziorako"""

    # GRASS base bidea ezarri
    os.environ["GISBASE"] = GRASS_BASE

    # PATH-a eguneratu GRASS bin eta script direktorioekin
    grass_bin = os.path.join(GRASS_BASE, "bin")
    grass_scripts = os.path.join(GRASS_BASE, "scripts")

    current_path = os.environ.get('PATH', '')
    if os.path.exists(grass_bin):
        os.environ["PATH"] = f"{grass_bin}:{current_path}"
        print(f"    GRASS bin bidea gehitu da: {grass_bin}")
    if os.path.exists(grass_scripts):
        os.environ["PATH"] = f"{grass_scripts}:{os.environ['PATH']}"
        print(f"    GRASS scripts bidea gehitu da: {grass_scripts}")

    # GRASS lib bidea ezarri
    grass_lib = os.path.join(GRASS_BASE, "lib")
    if os.path.exists(grass_lib):
        os.environ["LD_LIBRARY_PATH"] = f"{grass_lib}:{os.environ.get('LD_LIBRARY_PATH', '')}"

    print(f"    GRASS ingurunea konfiguratuta: {GRASS_BASE}")

def create_grass_location(shapefile_path, grass_db, grass_location, grass_mapset, denbora_kont):
    """Shapefile batetik abiatuta GRASS LOCATION bat sortu"""

    denbora_kont.urratsa_hasi("GRASS LOCATION sortzen")

    # Behin-behineko datuak irakurri proiekzioa lortzeko
    gdf = gpd.read_file(shapefile_path)
    crs = gdf.crs

    if crs is None:
        raise ValueError("Shapefile-ak ez du CRS definiturik. EPSG kodea eman behar duzu.")

    # EPSG kodea atera
    epsg_code = crs.to_epsg()
    if epsg_code is None:
        raise ValueError("Ezin izan da EPSG kodea atera. CRS-a ondo definituta dagoela ziurtatu.")

    print(f"    EPSG kodea detektatuta: {epsg_code}")

    # LOCATION sortu
    grass_location_path = os.path.join(grass_db, grass_location, grass_mapset)
    subprocess.run([
        "grass", "-c", f"EPSG:{epsg_code}",
        grass_location_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    denbora_kont.urratsa_amaitu()
    return epsg_code

def run_grass_command(command, grass_db, grass_location, grass_mapset, denbora_kont):
    """GRASS komando bat exekutatu"""

    grass_location_path = os.path.join(grass_db, grass_location, grass_mapset)
    full_cmd = [
        "grass",
        grass_location_path,
        "--exec"
    ] + command.split()

    result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        print(f"Errorea GRASS komandoan: {command}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"GRASS komandoak huts egin du: {command}")

    return result.stdout

def generalize_polygons_grass(input_shp, output_shp, tolerance):
    """GRASS erabiliz poligonoak orokortu"""

    denbora_kont = DenboraKontagailua("Poligonoen Orokortzea")
    denbora_kont.hasi_prozesu_osoa()

    try:
        # 1. GRASS ingurunea konfiguratu
        denbora_kont.urratsa_hasi("GRASS ingurunea konfiguratzen")
        setup_grass_environment()
        denbora_kont.urratsa_amaitu()

        # 2. GRASS LOCATION sortu
        epsg = create_grass_location(
            input_shp, GRASS_DATABASE, GRASS_LOCATION, GRASS_MAPSET, denbora_kont
        )

        # 3. Shapefile inportatu GRASS-era
        denbora_kont.urratsa_hasi("Shapefile inportatzen GRASS-era")
        base_name = os.path.splitext(os.path.basename(input_shp))[0]
        # Izena laburtu behar bada (GRASS-ek 10 karaktere baino gehiago ez ditu onartzen batzuetan)
        if len(base_name) > 10:
            base_name = base_name[:10]
        run_grass_command(
            f"v.in.ogr input={input_shp} output={base_name} --overwrite",
            GRASS_DATABASE, GRASS_LOCATION, GRASS_MAPSET, denbora_kont
        )
        denbora_kont.urratsa_amaitu()

        # 4. Topologia sortu
        denbora_kont.urratsa_hasi("Topologia eraikitzen")
        run_grass_command(
            f"v.build map={base_name} option=build",
            GRASS_DATABASE, GRASS_LOCATION, GRASS_MAPSET, denbora_kont
        )
        denbora_kont.urratsa_amaitu()

        # 5. Poligonoak orokortu (Douglas-Peucker algoritmoa)
        denbora_kont.urratsa_hasi(f"Poligonoak orokortzen ({tolerance}m tolerantziarekin)")
        generalized_name = f"{base_name}_gen"

        run_grass_command(
            f"v.generalize input={base_name} output={generalized_name} "
            f"method=douglas threshold={tolerance} --overwrite",
            GRASS_DATABASE, GRASS_LOCATION, GRASS_MAPSET, denbora_kont
        )
        denbora_kont.urratsa_amaitu()

        # 6. Irteera Shapefile zaharra ezabatu (berria sortu baino lehen)
        denbora_kont.urratsa_hasi("Irteera Shapefile zaharra ezabatzen")
        if os.path.exists(output_shp):
            print(f"    {output_shp} existitzen da, ezabatzen...")
            delete_grass_output_if_exists(output_shp)
        else:
            print(f"    {output_shp} ez da existitzen, ez da ezabatu behar.")
        denbora_kont.urratsa_amaitu()

        # 7. Emaitza Shapefile gisa esportatu
        denbora_kont.urratsa_hasi("Emaitza Shapefile gisa esportatzen")
        run_grass_command(
            f"v.out.ogr input={generalized_name} output={output_shp} format=ESRI_Shapefile --overwrite",
            GRASS_DATABASE, GRASS_LOCATION, GRASS_MAPSET, denbora_kont
        )
        denbora_kont.urratsa_amaitu()

        print(f"\nProzesua amaituta. Emaitza: {output_shp}")

    except Exception as e:
        print(f"\nErrorea: {e}")
        raise
    finally:
        # 8. Garbitu behin-behineko fitxategiak
        denbora_kont.urratsa_hasi("Behin-behineko fitxategiak garbitzen")
        if os.path.exists(GRASS_DATABASE):
            shutil.rmtree(GRASS_DATABASE)
        denbora_kont.urratsa_amaitu()

        denbora_kont.amaitu_prozesu_osoa()

# ==================================================
# PROGRAMA NAGUSIA
# ==================================================

def main():
    """Programa nagusia"""

    # Sarrera fitxategia existitzen dela egiaztatu
    if not os.path.exists(INPUT_SHAPEFILE):
        print(f"Errorea: {INPUT_SHAPEFILE} ez da existitzen.")
        return 1

    # 'grass' komandoa existitzen dela egiaztatu (Python 3.6-rako egokituta)
    try:
        subprocess.run(["which", "grass"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Errorea: 'grass' komandoa ez da aurkitu. GRASS GIS instalatuta dagoela ziurtatu.")
        return 1

    print(f"\nSarrera Shapefile: {INPUT_SHAPEFILE}")
    print(f"Irteera Shapefile: {OUTPUT_SHAPEFILE}")
    print(f"Orokortze tolerantzia: {SIMPLIFICATION_TOLERANCE} metro")
    print(f"GRASS instalazioa: {GRASS_BASE}")
    print(f"GRASS datu-basea: {GRASS_DATABASE}")

    # Orokortzea aplikatu
    try:
        generalize_polygons_grass(
            INPUT_SHAPEFILE,
            OUTPUT_SHAPEFILE,
            SIMPLIFICATION_TOLERANCE
        )
    except Exception as e:
        print(f"\nProzesuak huts egin du: {e}")
        return 1

    # Emaitza egiaztatu (GeoPandas-ekin irakurri)
    if os.path.exists(OUTPUT_SHAPEFILE):
        gdf_out = gpd.read_file(OUTPUT_SHAPEFILE)
        print(f"\nEmaitzaren estatistikak:")
        print(f"  Poligono kopurua: {len(gdf_out)}")
        print(f"  Fitxategia: {OUTPUT_SHAPEFILE}")
        print("\nProzesua ARRAKASTATSUA izan da!")
        return 0
    else:
        print("\nErrorea: Irteera Shapefile-a ez da sortu.")
        return 1

if __name__ == "__main__":
    import sys
    exit(main())
