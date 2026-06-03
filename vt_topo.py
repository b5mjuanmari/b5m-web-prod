#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import geopandas as gpd
from datetime import timedelta

# ==================================================
# ALDAGAI KONFIGURAGARRIAK
# ==================================================

INPUT_SHAPEFILE = "/home5/SHP/TilesVT/BTA_CUBIERT_TERRESTRE_A_4E5_ETRS89.shp"
OUTPUT_SHAPEFILE = "./dat/vt_landcover_4e5_5.shp"
SIMPLIFICATION_TOLERANCE = 5.0

# ==================================================
# DENBORA KONTAGAILLUA
# ==================================================

def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

class DenboraKontagailua:
    def __init__(self, izena="Prozesua"):
        self.izena = izena
        self.hasiera_globala = None
        self.bukaera_globala = None
        self.urratsak = []

    def hasi_prozesu_osoa(self):
        self.hasiera_globala = time.time()
        print(f"\n{'='*60}")
        print(f">>> {self.izena} HASIERA - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

    def amaitu_prozesu_osoa(self):
        self.bukaera_globala = time.time()
        denbora_totala = self.bukaera_globala - self.hasiera_globala
        print(f"\n{'='*60}")
        print(f">>> {self.izena} AMAITU")
        print(f"    Denbora totala: {format_time(denbora_totala)}")
        print(f"{'='*60}\n")
        self.erakutsi_laburpena()

    def urratsa_hasi(self, urrats_izena):
        hasiera = time.time()
        self.urratsak.append({
            'izena': urrats_izena,
            'hasiera': hasiera,
            'bukaera': None
        })
        print(f"    [*] {urrats_izena}...", end=' ', flush=True)
        return hasiera

    def urratsa_amaitu(self):
        if self.urratsak and self.urratsak[-1]['bukaera'] is None:
            bukaera = time.time()
            self.urratsak[-1]['bukaera'] = bukaera
            iraupena = bukaera - self.urratsak[-1]['hasiera']
            print(f"[DONE - {format_time(iraupena)}]")

    def erakutsi_laburpena(self):
        print("\nDENBORA LABURPENA:")
        print("-" * 50)
        for urratsa in self.urratsak:
            if urratsa['bukaera']:
                iraupena = urratsa['bukaera'] - urratsa['hasiera']
                print(f"    - {urratsa['izena']:30} {format_time(iraupena)}")
        print("-" * 50)

# ==================================================
# PROZESU NAGUSIA (GRASS gabe, GeoPandas + Shapely erabiliz)
# ==================================================

def generalize_polygons_geopandas(input_shp, output_shp, tolerance):
    """GeoPandas eta Shapely erabiliz poligonoak orokortu (GRASS gabe)"""

    denbora_kont = DenboraKontagailua("Poligonoen Orokortzea")
    denbora_kont.hasi_prozesu_osoa()

    try:
        # 1. Irteera Shapefile zaharra ezabatu
        denbora_kont.urratsa_hasi("Irteera Shapefile zaharra ezabatzen")
        if os.path.exists(output_shp):
            base_path = os.path.splitext(output_shp)[0]
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj']:
                f = base_path + ext
                if os.path.exists(f):
                    os.remove(f)
        denbora_kont.urratsa_amaitu()

        # 2. Shapefile irakurri
        denbora_kont.urratsa_hasi("Sarrera Shapefile irakurtzen")
        gdf = gpd.read_file(input_shp)
        print(f"    Poligono kopurua: {len(gdf)}")
        denbora_kont.urratsa_amaitu()

        # 3. Poligonoak orokortu (Douglas-Peucker)
        denbora_kont.urratsa_hasi(f"Poligonoak orokortzen ({tolerance} metro)")

        from shapely.geometry import Polygon, MultiPolygon
        from shapely.ops import transform

        def simplify_polygon(geom):
            if geom.is_empty:
                return geom
            if geom.geom_type == 'Polygon':
                # Poligonoa sinplifikatu
                simplified = geom.simplify(tolerance, preserve_topology=True)
                # Poligonoa baliozkoa dela ziurtatu
                if not simplified.is_valid:
                    simplified = simplified.buffer(0)
                return simplified
            elif geom.geom_type == 'MultiPolygon':
                # MultiPoligonoa sinplifikatu
                polygons = [simplify_polygon(p) for p in geom.geoms]
                return MultiPolygon([p for p in polygons if not p.is_empty])
            else:
                return geom

        # Sinplifikazioa aplikatu
        gdf['geometry'] = gdf.geometry.apply(simplify_polygon)

        # Poligono hutsak ezabatu
        gdf = gdf[~gdf.geometry.is_empty]
        print(f"    Orokortu ondorengo poligono kopurua: {len(gdf)}")
        denbora_kont.urratsa_amaitu()

        # 4. Emaitza gorde
        denbora_kont.urratsa_hasi("Emaitza Shapefile gisa gordetzen")
        output_dir = os.path.dirname(output_shp)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        gdf.to_file(output_shp)
        denbora_kont.urratsa_amaitu()

        print(f"\nProzesua amaituta. Emaitza: {output_shp}")

    except Exception as e:
        print(f"\nErrorea: {e}")
        raise
    finally:
        denbora_kont.amaitu_prozesu_osoa()

# ==================================================
# MAIN
# ==================================================

def main():
    if not os.path.exists(INPUT_SHAPEFILE):
        print(f"Errorea: {INPUT_SHAPEFILE} ez da existitzen.")
        return 1

    print(f"\nSarrera Shapefile: {INPUT_SHAPEFILE}")
    print(f"Irteera Shapefile: {OUTPUT_SHAPEFILE}")
    print(f"Orokortze tolerantzia: {SIMPLIFICATION_TOLERANCE} metro")
    print(f"\n[NOTA] GRASS-en ordez, GeoPandas + Shapely erabiliz prozesatuko da.")

    try:
        generalize_polygons_geopandas(
            INPUT_SHAPEFILE,
            OUTPUT_SHAPEFILE,
            SIMPLIFICATION_TOLERANCE
        )
    except Exception as e:
        print(f"\nProzesuak huts egin du: {e}")
        return 1

    if os.path.exists(OUTPUT_SHAPEFILE):
        gdf_out = gpd.read_file(OUTPUT_SHAPEFILE)
        print(f"\nEmaitzaren estatistikak:")
        print(f"  Poligono kopurua: {len(gdf_out)}")
        print("\nProzesua ARRAKASTATSUA izan da!")
        return 0
    else:
        print("\nErrorea: Irteera Shapefile-a ez da sortu.")
        return 1

if __name__ == "__main__":
    exit(main())
