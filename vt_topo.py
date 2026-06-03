#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import shutil
import subprocess
import geopandas as gpd
from datetime import timedelta
from shapely.geometry import Polygon, MultiPolygon

# ==================================================
# ALDAGAI KONFIGURAGARRIAK
# ==================================================

INPUT_SHAPEFILE = "/home5/SHP/TilesVT/MT_landcover_EJ_4E5.shp"
OUTPUT_SHAPEFILE = "./dat/vt_MT_landcover_4e5_5.shp"
SIMPLIFICATION_TOLERANCE = 5.0
GRASS_BASE = "/usr/lib/grass74"

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
# ZULOAK KENTZEKO FUNTZIOA (BEHAR BEZALA)
# ==================================================

def remove_all_holes(geometry):
    """Poligono baten zulo guztiak kendu (barneko eremu guztiak ezabatu)"""

    if geometry is None or geometry.is_empty:
        return geometry

    def process_polygon(poly):
        if poly.is_empty:
            return poly
        # Zuloak kendu: kanpoko perimetroa bakarrik mantendu
        if poly.exterior:
            return Polygon(poly.exterior)
        return poly

    def process_geometry(geom):
        if geom.geom_type == 'Polygon':
            return process_polygon(geom)
        elif geom.geom_type == 'MultiPolygon':
            # MultiPoligonoaren poligono bakoitzaren zuloak kendu
            new_polygons = []
            for poly in geom.geoms:
                if isinstance(poly, Polygon):
                    cleaned = process_polygon(poly)
                    if not cleaned.is_empty and cleaned.is_valid:
                        new_polygons.append(cleaned)
            if new_polygons:
                return MultiPolygon(new_polygons)
            else:
                return None
        return geom

    try:
        result = process_geometry(geometry)
        # Gehiegizko sinplifikazioa? (aukerakoa)
        if result and hasattr(result, 'simplify'):
            result = result.simplify(0.1, preserve_topology=True)
        return result
    except Exception as e:
        print(f"    Zuloak kentzean errorea: {e}")
        return geometry

def fill_holes(geometry, max_hole_area=1000):
    """Zulo txikiak bete (tolerantzia baino txikiagoak direnak)"""

    if geometry is None or geometry.is_empty:
        return geometry

    def process_polygon(poly):
        if not poly.interiors:
            return poly

        new_interiors = []
        for interior in poly.interiors:
            interior_poly = Polygon(interior)
            # Zuloaren azalera kalkulatu
            if interior_poly.area > max_hole_area:
                # Zulo handia mantendu
                new_interiors.append(interior)
            # Zulo txikiak baztertu (ez dira mantenduko)

        return Polygon(poly.exterior, new_interiors)

    def process_geometry(geom):
        if geom.geom_type == 'Polygon':
            return process_polygon(geom)
        elif geom.geom_type == 'MultiPolygon':
            polygons = [process_polygon(p) for p in geom.geoms]
            return MultiPolygon(polygons)
        return geom

    return process_geometry(geometry)

# ==================================================
# GRASS PROZESUA
# ==================================================

def generalize_polygons_grass(input_shp, output_shp, tolerance):
    """GRASS erabiliz poligonoak orokortu, gero zulo guztiak kendu"""

    denbora_kont = DenboraKontagailua("Poligonoen Orokortzea (GRASS)")
    denbora_kont.hasi_prozesu_osoa()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    grass_db = os.path.join(script_dir, "grassdata_temp")
    temp_shp = os.path.join(script_dir, "temp_generalized.shp")

    try:
        # 1. Irteera Shapefile zaharra ezabatu
        denbora_kont.urratsa_hasi("Irteera Shapefile zaharra ezabatzen")
        for f in [output_shp, temp_shp]:
            if os.path.exists(f):
                base_path = os.path.splitext(f)[0]
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj']:
                    file_path = base_path + ext
                    if os.path.exists(file_path):
                        os.remove(file_path)
        denbora_kont.urratsa_amaitu()

        # 2. Irteera direktorioa sortu
        denbora_kont.urratsa_hasi("Irteera direktorioa sortzen")
        output_dir = os.path.dirname(output_shp)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        denbora_kont.urratsa_amaitu()

        # 3. CRS lortu
        denbora_kont.urratsa_hasi("CRS detektatzen")
        original_gdf = gpd.read_file(input_shp)
        crs = original_gdf.crs
        epsg_code = crs.to_epsg() if crs and crs.to_epsg() else 25830
        print(f"    EPSG: {epsg_code}")
        print(f"    Jatorrizko poligono kopurua: {len(original_gdf)}")
        denbora_kont.urratsa_amaitu()

        # 4. GRASS Location sortu
        denbora_kont.urratsa_hasi("GRASS Location sortzen")
        location_path = os.path.join(grass_db, "proiektua")

        if os.path.exists(grass_db):
            shutil.rmtree(grass_db)
        os.makedirs(grass_db)

        subprocess.run(
            ["grass", "-c", f"EPSG:{epsg_code}", "-e", location_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        mapset_path = os.path.join(location_path, "PERMANENT")
        if not os.path.exists(mapset_path):
            os.makedirs(mapset_path)
        denbora_kont.urratsa_amaitu()

        # 5. Shapefile inportatu
        denbora_kont.urratsa_hasi("Shapefile inportatzen GRASS-era")
        subprocess.run([
            "grass", mapset_path, "--exec",
            "v.in.ogr", f"input={input_shp}", "output=landcover", "--overwrite"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        denbora_kont.urratsa_amaitu()

        # 6. Topologia eraiki
        denbora_kont.urratsa_hasi("Topologia eraikitzen")
        subprocess.run([
            "grass", mapset_path, "--exec",
            "v.build", "map=landcover", "option=build"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        denbora_kont.urratsa_amaitu()

        # 7. Poligonoak orokortu
        denbora_kont.urratsa_hasi(f"Poligonoak orokortzen ({tolerance}m)")

        methods = ["boyle", "reduction", "snake"]
        success = False

        for method in methods:
            print(f"    Saiatzen: {method} metodoa...")
            result = subprocess.run([
                "grass", mapset_path, "--exec",
                "v.generalize", "input=landcover", "output=landcover_gen",
                f"method={method}", f"threshold={tolerance}", "--overwrite"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                print(f"    {method} metodoak ondo funtzionatu du")
                success = True
                break

        if not success:
            raise RuntimeError("Ez da orokortze metodoa aurkitu")

        denbora_kont.urratsa_amaitu()

        # 8. Emaitza esportatu
        denbora_kont.urratsa_hasi("Emaitza esportatzen")
        subprocess.run([
            "grass", mapset_path, "--exec",
            "v.out.ogr", "input=landcover_gen", f"output={temp_shp}",
            "format=ESRI_Shapefile", "--overwrite"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        denbora_kont.urratsa_amaitu()

        # 9. Zulo guztiak kendu GeoPandas-ekin
        denbora_kont.urratsa_hasi("Zulo guztiak kentzen")
        gdf_gen = gpd.read_file(temp_shp)
        print(f"    Orokortu ondorengo poligonoak: {len(gdf_gen)}")

        # Lehenengo: geometria bakoitza baliozkoa dela ziurtatu
        gdf_gen['geometry'] = gdf_gen.geometry.buffer(0)

        # Zulo guztiak kendu (zulo txiki eta handi guztiak)
        gdf_clean = gdf_gen.copy()
        gdf_clean['geometry'] = gdf_clean.geometry.apply(remove_all_holes)

        # Baliozkotasuna ziurtatu
        gdf_clean['geometry'] = gdf_clean.geometry.buffer(0)

        # Poligono hutsak ezabatu
        gdf_clean = gdf_clean[~gdf_clean.geometry.is_empty]
        gdf_clean = gdf_clean[gdf_clean.geometry.is_valid]

        print(f"    Zuloak kendu ondorengo poligonoak: {len(gdf_clean)}")
        denbora_kont.urratsa_amaitu()

        # 10. Azken emaitza gorde
        denbora_kont.urratsa_hasi("Azken emaitza gordetzen")
        gdf_clean.to_file(output_shp)
        denbora_kont.urratsa_amaitu()

        print(f"\nProzesua amaituta. Emaitza: {output_shp}")

    except subprocess.CalledProcessError as e:
        print(f"\nErrorea GRASS komandoan: {e}")
        raise
    except Exception as e:
        print(f"\nErrorea: {e}")
        raise
    finally:
        denbora_kont.urratsa_hasi("Behin-behineko fitxategiak garbitzen")
        if os.path.exists(grass_db):
            shutil.rmtree(grass_db)
        if os.path.exists(temp_shp):
            base_path = os.path.splitext(temp_shp)[0]
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg', '.qpj']:
                f = base_path + ext
                if os.path.exists(f):
                    os.remove(f)
        denbora_kont.urratsa_amaitu()
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
    print(f"GRASS + GeoPandas (zulo guztiak kenduz)")

    try:
        generalize_polygons_grass(
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
