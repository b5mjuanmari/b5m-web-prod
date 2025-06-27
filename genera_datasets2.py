import os
import cx_Oracle
import subprocess
import zipfile
import csv
from datetime import datetime
import time
import math
import shutil
import sys

# NLS_LANG aldagaia konfiguratu Oracle-rentzat
os.environ["NLS_LANG"] = "SPANISH_SPAIN.UTF8"
os.environ["CPL_LOG"] = "/dev/null"

# Konfigurazio aldagaiak
db_user = os.getenv("DB_USER", "b5mweb_nombres")
db_user2 = os.getenv("DB_USER", "b5mweb_25830")
db_pass = os.getenv("DB_PASS", "web+")
db_dsn = os.getenv("DB_DSN", "bdet")
db_tab = os.getenv("DB_TAB", "GIPUTZ")
ogr2ogr_bin = "/usr/local/bin/ogr2ogr"

# SQL kontsulta
sql = """
select
  case
    when a.nombre_eu = a.nombre_es then a.nombre_eu
    else a.nombre_eu || ' / ' || a.nombre_es
  end as name,
  a.origen,
  a.destino,
  b.extension,
  b.formato,
  b.namefield
from
  b5mweb_nombres.datasets2_info a
inner join
  b5mweb_nombres.datasets2_ficheros b on a.id_dataset = b.id_dataset
where
  a.crear = 1
order by
  a.orden"""

ruta1 = "/home5/SHP"
ruta2 = "/home/data/datos_explotacion/CUR/datasets2"
gpkg_dir = f"/tmp/{os.path.splitext(os.path.basename(sys.argv[0]))[0]}"
cur_dir = "/home/lidar/SCRIPTS/WEB_PROD"
log_file = f"{cur_dir}/log/genera_datasets2_{datetime.now().strftime('%Y%m%d')}.log"

def log(message):
    """Idazten du log fitxategian."""
    with open(log_file, "a") as logf:
        logf.write(f"{message}")

def format_duration(seconds):
    """Denbora iraupena H:MM:SS formatuan itzultzen du."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"

def execute_sql(query):
    """Exekutatzen du SQL kontsulta bat eta emaitzak itzultzen ditu."""
    try:
        with cx_Oracle.connect(db_user, db_pass, db_dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = []
                for row in cursor:
                    new_row = tuple(col.read() if isinstance(col, cx_Oracle.LOB) else col for col in row)
                    results.append(new_row)
                return results
    except cx_Oracle.DatabaseError as e:
        log(f"Errorea SQL exekutzean: {e}\n")
        return []

def generate_gpkg(origen, destino):
    """Sortu GPKG fitxategia jatorrizko datuetatik"""
    gpkg_file = os.path.join(gpkg_dir, f"{destino}.gpkg")
    if os.path.exists(gpkg_file):
        return gpkg_file

    if origen.strip().lower().startswith("with"):
        # SQL sententzia exekutatu eta behin behineko CSV fitxategia sortu
        csv_file = os.path.join(gpkg_dir, f"{destino}.csv")
        if os.path.exists(csv_file):
            os.remove(csv_file)

        # Oracle datu-basearekin konektatu eta SQL sententzia exekutatu
        try:
            with cx_Oracle.connect(db_user, db_pass, db_dsn) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(origen)
                    with open(csv_file, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        # Idatzi goiburukoak
                        columns = [col[0] for col in cursor.description]
                        csv_writer.writerow(columns)
                        # Idatzi datuak
                        for row in cursor:
                            csv_writer.writerow(row)
        except cx_Oracle.DatabaseError as e:
            log(f"Errorea SQL exekutzean: {e}\n")
            return None

        # CSV fitxategia GPKG fitxategira bihurtu
        ogr2ogr_command = [
            ogr2ogr_bin,
            "-f", "GPKG",
            "-s_srs", "EPSG:25830",
            "-t_srs", "EPSG:25830",
            "-nln", destino,
            "-lco", "GEOMETRY_NAME=geom",
            "-lco", "FID=FID",
            gpkg_file,
            csv_file,
            "-oo", "KEEP_GEOM_COLUMNS=NO"
        ]
        subprocess.run(ogr2ogr_command, check=True)

        # Ezabatu behin behineko CSV fitxategia
        if os.path.exists(csv_file):
            os.remove(csv_file)
    else:
        ogr2ogr_command = [
            ogr2ogr_bin,
            "-f", "GPKG",
            "-s_srs", "EPSG:25830",
            "-t_srs", "EPSG:25830",
            "-nln", destino,
            "-lco", "GEOMETRY_NAME=geom",
            "-lco", "FID=FID",
            gpkg_file
        ]
        if origen.strip().lower().startswith("select"):
            ogr2ogr_command.extend(["-sql", origen, f"OCI:{db_user2}/{db_pass}@{db_dsn}:{db_tab}"])
        else:
            ogr2ogr_command.append(os.path.join(ruta1, f"{origen}.shp"))
        subprocess.run(ogr2ogr_command, check=True)

    return gpkg_file

def generate_shp(gpkg_file, destino):
    """Sortu SHP fitxategia GPKG-tik"""
    shp_files = [f"{gpkg_dir}/{destino}.{ext}" for ext in ["shp", "shx", "dbf", "prj"]]
    for shp_file in shp_files:
        if os.path.exists(shp_file):
            os.remove(shp_file)

    shp_command = [
        ogr2ogr_bin,
        "-f", "ESRI Shapefile",
        shp_files[0],
        gpkg_file
    ]
    subprocess.run(shp_command, check=True)

    zip_file = os.path.join(ruta2, f"{gpkg_dir}/{destino}_SHP.zip")
    if os.path.exists(zip_file):
        os.remove(zip_file)
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for shp_file in shp_files:
            if os.path.exists(shp_file):
                zipf.write(shp_file, os.path.basename(shp_file))
                os.remove(shp_file)

    target_file = os.path.join(ruta2, f"{destino}.zip")
    if os.path.exists(target_file):
        os.remove(target_file)
    shutil.copy2(zip_file, target_file)
    if os.path.exists(zip_file):
        os.remove(zip_file)

def generate_kml(gpkg_file, destino, namefield):
    """Sortu KML fitxategia GPKG-tik"""
    kml_file = os.path.join(gpkg_dir, f"{destino}.kml")
    if os.path.exists(kml_file):
        os.remove(kml_file)
    kml_command = [
        ogr2ogr_bin,
        "-f", "KML",
        "-dsco", f"NameField={namefield}",
        "-mapFieldType", "Integer64=Real",
        kml_file,
        gpkg_file
    ]
    subprocess.run(kml_command, check=True)
    kml_file2 = os.path.join(ruta2, f"{destino}.kml")
    if os.path.exists(kml_file2):
        os.remove(kml_file2)
    shutil.copy2(kml_file, kml_file2)
    if os.path.exists(kml_file):
        os.remove(kml_file)

def generate_geojson(gpkg_file, destino):
    """Sortu GeoJSON fitxategia GPKG-tik"""
    geojson_file = os.path.join(gpkg_dir, f"{destino}.geojson")
    if os.path.exists(geojson_file):
        os.remove(geojson_file)
    geojson_command = [
        ogr2ogr_bin,
        "-f", "GeoJSON",
        geojson_file,
        gpkg_file
    ]
    subprocess.run(geojson_command, check=True)
    geojson_file2 = os.path.join(ruta2, f"{destino}.geojson")
    if os.path.exists(geojson_file2):
        os.remove(geojson_file2)
    shutil.copy2(geojson_file, geojson_file2)
    if os.path.exists(geojson_file):
        os.remove(geojson_file)

def generate_csv(gpkg_file, destino):
    """Sortu CSV fitxategia GPKG-tik"""
    csv_file = os.path.join(gpkg_dir, f"{destino}.csv")
    if os.path.exists(csv_file):
        os.remove(csv_file)
    csv_command = [
        ogr2ogr_bin,
        "-f", "CSV",
        "-lco", "GEOMETRY=AS_XY",
        csv_file,
        gpkg_file
    ]
    subprocess.run(csv_command, check=True)
    csv_file2 = os.path.join(ruta2, f"{destino}.csv")
    if os.path.exists(csv_file2):
        os.remove(csv_file2)
    shutil.copy2(csv_file, csv_file2)
    if os.path.exists(csv_file):
        os.remove(csv_file)

    zip_file = os.path.join(ruta2, f"{destino}_CSV.zip")
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_file2, os.path.basename(csv_file))
    os.remove(csv_file2)

def generate_datasets(sql):
    datasets = execute_sql(sql)

    # Sortu GPKG karpeta existitzen ez bada
    if not os.path.exists(gpkg_dir):
        os.makedirs(gpkg_dir)

    total_datasets = len(datasets)
    start_time = time.time()
    processed_datasets = 0

    for i, (name, origen, destino, extension, formato, namefield) in enumerate(datasets, start=1):
        iteration_start = time.time()
        log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {i}/{total_datasets} - {destino} - {name} - {formato} - ")

        try:
            # 1. Lehenik eta behin GPKG fitxategia sortu
            intermediate_gpkg = generate_gpkg(origen, destino)

            # 2. Formatuaren arabera prozesatu
            if formato == "GPKG":
                # GPKG kasuan, jatorrizko fitxategia helburuko kokalekura kopiatu
                target_file = os.path.join(ruta2, f"{destino}.gpkg")
                shutil.copy2(intermediate_gpkg, target_file)

            else:
                # Beste formatuetarako, ohiko prozesua
                if formato == "SHP":
                    generate_shp(intermediate_gpkg, destino)
                elif formato == "KML":
                    generate_kml(intermediate_gpkg, destino, namefield)
                elif formato == "GeoJSON":
                    generate_geojson(intermediate_gpkg, destino)
                elif formato == "CSV":
                    generate_csv(intermediate_gpkg, destino)
                else:
                    log(f"{formato} ez da onartzen.\n")

        except Exception as e:
            log(f"Errorea {destino} prozesatzean: {str(e)}\n")

        # Denbora estimazioa kalkulatu
        processed_datasets += 1
        elapsed_time = time.time() - start_time
        avg_time_per_dataset = elapsed_time / processed_datasets
        remaining_datasets = total_datasets - processed_datasets
        estimated_remaining = avg_time_per_dataset * remaining_datasets

        # Denbora estimatua formatu irakurgarrian
        hours, rem = divmod(estimated_remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        estimated_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

        log(f"{time.time() - iteration_start:.2f}s - geratzen da: {estimated_str}\n")

    # GPKG karpeta ezabatu
    try:
        if os.path.exists(gpkg_dir):
            shutil.rmtree(gpkg_dir)
    except Exception as e:
        log(f"Errorea GPKG direktorioa ezabatzean: {str(e)}\n")

if __name__ == "__main__":
    script_start_time = datetime.now()
    if os.path.exists(log_file):
        os.remove(log_file)

    if os.path.exists(gpkg_dir):
        shutil.rmtree(gpkg_dir)

    if not os.path.exists(ruta2):
        os.makedirs(ruta2)

    log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Hasiera: {os.path.abspath(__file__)}\n")
    generate_datasets(sql)
    script_end_time = datetime.now()
    script_duration = script_end_time - script_start_time
    log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Bukaera: {os.path.abspath(__file__)}\n")
    log(f"Denbora: {format_duration(script_duration.total_seconds())}\n")
