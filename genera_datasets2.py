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
import sqlite3
import json

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

# SQL kontsulta (ALDATUTA - campos_csv gehitu da)
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
  b.namefield,
  a.campos_csv
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

def kargatu_shapefile_gpkg(sfp, gpkgp, gpkgt, gpkgs):
    """Shapefile bat GPKG fitxategi batean kargatu."""
    #"-sql", "select herria as MUNI from " + sft,
    command = [
        "ogr2ogr",
        "-f", "GPKG",
        "-update",
        "-append",
        "-nlt", "PROMOTE_TO_MULTI",
        "-nln", gpkgt,
        "-sql", gpkgs,
        "-lco", "GEOMETRY_NAME=geom",
        "-lco", "FID=FID",
        gpkgp,
        sfp
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        log(f"Errorea gertatu da {sfp} shapefile-a GPKG fitxategian kargatzean: {e}")

def generate_gpkg_cadastre(origen, gpkg_file, campos_csv):
    """Sortu katastroko GPKG fitxategia"""
    origen_lerroak = origen.splitlines()
    origen_dir = ruta1 + "/" + origen_lerroak[0]
    shapefiles = [f for f in os.listdir(origen_dir) if f.endswith('.shp')]
    for index, fitx_shp in enumerate(shapefiles, start=1):
        shapefile_path = os.path.join(origen_dir, fitx_shp)
        fitx_shp_oin = fitx_shp.split('.')[0]
        # Bilatu katea eta hurrengo lerroaren berri eman
        lerroak = origen.splitlines()
        j = 0
        for i, lerroa in enumerate(lerroak):
            if "-- " + fitx_shp_oin in lerroa:
                if i + 1 < len(lerroak):
                    gpkg_tab = lerroak[i + 1].split('-- ')[1]
                    gpkg_sel = lerroak[i + 2]
                    j = 1

        if j == 0:
            gpkg_tab = fitx_shp_oin

        # Shapefile bat GPKG fitxategi batean kargatu
        kargatu_shapefile_gpkg(shapefile_path, gpkg_file, gpkg_tab, gpkg_sel)

    # GPKG fitxategian eremu deskribapenak gehitu (campos_csv erabiliz)
    if campos_csv:
        conn2 = sqlite3.connect(gpkg_file)
        conn2_c = conn2.cursor()

        # gpkg_data_columns taula sortu (baldin ez badago)
        conn2_c.execute("""
        CREATE TABLE IF NOT EXISTS gpkg_data_columns (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            name TEXT,
            title TEXT,
            description TEXT,
            mime_type TEXT,
            constraint_name TEXT,
            PRIMARY KEY (table_name, column_name)
        )
        """)

        # Eremu bakoitzaren deskribapena sartu comment moduan
        for line in campos_csv.split('\n'):
            line3 = line[:3]
            if line3 == "GFA":
                destino2 = line
                continue
            if line.strip():
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 4:
                    description = f"{parts[1].strip(chr(34))} / {parts[2].strip(chr(34))} / {parts[3].strip(chr(34))}"

                    # gpkg_data_columns sartu / eguneratu
                    conn2_c.execute("""
                    INSERT OR REPLACE INTO gpkg_data_columns (table_name, column_name, description)
                    VALUES (?, ?, ?)
                    """, (destino2, parts[0], description))

        conn2.commit()
        conn2.close()

    return gpkg_file

def generate_gpkg(origen, destino, campos_csv):
    """Sortu GPKG fitxategia jatorrizko datuetatik eremu deskribapenekin"""
    gpkg_file = os.path.join(gpkg_dir, f"{destino}.gpkg")
    if os.path.exists(gpkg_file):
        return gpkg_file

    if origen.split('/')[0].lower() == "catastro":
        # Katastroaren kasu berezia
        generate_gpkg_cadastre(origen, gpkg_file, campos_csv)
    elif origen.strip().lower().startswith("with"):
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

    # GPKG fitxategian eremu deskribapenak gehitu (campos_csv erabiliz)
    if campos_csv:
        conn2 = sqlite3.connect(gpkg_file)
        conn2_c = conn2.cursor()

        # gpkg_data_columns taula sortu (baldin ez badago)
        conn2_c.execute("""
        CREATE TABLE IF NOT EXISTS gpkg_data_columns (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            name TEXT,
            title TEXT,
            description TEXT,
            mime_type TEXT,
            constraint_name TEXT,
            PRIMARY KEY (table_name, column_name)
        )
        """)

        # Eremu bakoitzaren deskribapena sartu comment moduan
        for line in campos_csv.split('\n'):
            if line.strip():
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 4:
                    description = f"{parts[1].strip(chr(34))} / {parts[2].strip(chr(34))} / {parts[3].strip(chr(34))}"

                    # gpkg_data_columns sartu / eguneratu
                    conn2_c.execute("""
                    INSERT OR REPLACE INTO gpkg_data_columns (table_name, column_name, description)
                    VALUES (?, ?, ?)
                    """, (destino, parts[0], description))

        conn2.commit()
        conn2.close()

    return gpkg_file

def generate_shp(gpkg_file, destino, campos_csv):
    """Sortu SHP fitxategia GPKG-tik eremu deskribapenekin"""
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

    # README fitxategia sortu eremu deskribapenekin
    readme_file = os.path.join(gpkg_dir, f"README_{destino}.txt")
    with open(readme_file, 'w') as f:
        f.write("Eremuen deskribapena / Descripción de los campos / Field Description:\n")
        if campos_csv:
            for line in campos_csv.split('\n'):
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 4:
                        f.write(f"{parts[0].upper()}: {parts[1].strip(chr(34))} / {parts[2].strip(chr(34))} / {parts[3].strip(chr(34))}\n")

    zip_file = os.path.join(ruta2, f"{destino}_SHP.zip")
    if os.path.exists(zip_file):
        os.remove(zip_file)
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for shp_file in shp_files:
            if os.path.exists(shp_file):
                zipf.write(shp_file, os.path.basename(shp_file))
                os.remove(shp_file)
        zipf.write(readme_file, os.path.basename(readme_file))
        os.remove(readme_file)

def generate_kml(gpkg_file, destino, namefield, campos_csv):
    """Sortu KML fitxategia GPKG-tik eremu deskribapenekin"""
    kml_file = os.path.join(gpkg_dir, f"{destino}.kml")
    if os.path.exists(kml_file):
        os.remove(kml_file)

    # 1. Lehenik KML fitxategia sortu ogr2ogr-rekin
    kml_command = [
        ogr2ogr_bin,
        "-f", "KML",
        "-dsco", f"NameField={namefield}",
        "-mapFieldType", "Integer64=Real",
        kml_file,
        gpkg_file
    ]
    subprocess.run(kml_command, check=True)

    # 2. Eremu deskribapenak gehitu Document elementuaren barruan
    if campos_csv:
        with open(kml_file, 'r+', encoding='utf-8') as f:
            content = f.read()

            # Bilatu Document etiketa
            doc_start = content.find('<Document id="root_doc">')
            if doc_start == -1:
                doc_start = content.find('<Document>')
                if doc_start == -1:
                    raise ValueError("Ezin da <Document> elementua aurkitu KML fitxategian")

            # Kalkulatu kokalekua (Document etiketaren ondoren)
            insert_pos = content.find('>', doc_start) + 1

            # Sortu deskribapenak KML formatuan
            desc_lines = [
                '<description><![CDATA[',
                'Eremuen deskribapena / Descripción de los campos / Field Description:'
            ]

            for line in campos_csv.split('\n'):
                if line.strip():
                    parts = [part.strip().strip('"') for part in line.split(',')]
                    if len(parts) >= 4:
                        desc_lines.append(
                            f'{parts[0].upper()}: '
                            f'{parts[1]} / {parts[2]} / {parts[3]}'
                        )

            desc_lines.extend([']]></description>'])
            descriptions = '\n    '.join(desc_lines)

            # Sartu deskribapenak kokaleku egokian
            new_content = content[:insert_pos] + '\n    ' + descriptions + content[insert_pos:]

            # Idatzi fitxategia berriro
            f.seek(0)
            f.write(new_content)
            f.truncate()

    # 3. Kopiatu helburuko direktorioa
    kml_file2 = os.path.join(ruta2, f"{destino}.kml")
    if os.path.exists(kml_file2):
        os.remove(kml_file2)
    shutil.copy2(kml_file, kml_file2)

    # 4. Garbitu behin behineko fitxategia
    if os.path.exists(kml_file):
        os.remove(kml_file)

def generate_geojson(gpkg_file, destino, campos_csv):
    """Sortu GeoJSON fitxategia GPKG-tik eremu deskribapenekin"""
    geojson_file = os.path.join(gpkg_dir, f"{destino}.geojson")
    if os.path.exists(geojson_file):
        os.remove(geojson_file)

    # 1. Lehenik GeoJSON fitxategia sortu ogr2ogr-rekin
    geojson_command = [
        ogr2ogr_bin,
        "-f", "GeoJSON",
        geojson_file,
        gpkg_file
    ]
    subprocess.run(geojson_command, check=True)

    # 2. Eremu deskribapenak gehitu JSON-aren egitura egokian
    if campos_csv:
        with open(geojson_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)

            # Sortu eremu deskribapenak (eremu-izenak LARRIZ)
            field_descriptions = {}
            for line in campos_csv.split('\n'):
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 4:
                        eremu_izena = parts[0].upper()  # Eremu-izena LARRIZ bihurtu
                        field_descriptions[eremu_izena] = {
                            "eu": parts[1].strip('"'),
                            "es": parts[2].strip('"'),
                            "en": parts[3].strip('"')
                        }

            # Eguneratu JSON egitura
            updated_data = {
                "type": "FeatureCollection",
                "_fieldDescriptions": field_descriptions,
                **{k: v for k, v in data.items() if k not in ["type"]}
            }

            # Idatzi fitxategia berriro
            f.seek(0)
            json.dump(updated_data, f, ensure_ascii=False, indent=2, sort_keys=False)
            f.truncate()

    # 3. Kopiatu helburuko direktorioa
    geojson_file2 = os.path.join(ruta2, f"{destino}.geojson")
    if os.path.exists(geojson_file2):
        os.remove(geojson_file2)
    shutil.copy2(geojson_file, geojson_file2)

    # 4. Garbitu behin behineko fitxategia
    if os.path.exists(geojson_file):
        os.remove(geojson_file)

def generate_csv(gpkg_file, destino, campos_csv):
    """Sortu CSV fitxategia GPKG-tik eremu deskribapenekin"""
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

    # README fitxategia sortu eremu deskribapenekin
    readme_file = os.path.join(gpkg_dir, f"README_{destino}.txt")
    with open(readme_file, 'w') as f:
        f.write("Eremuen deskribapena / Descripción de los campos / Field Description:\n")
        if campos_csv:
            for line in campos_csv.split('\n'):
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 4:
                        f.write(f"{parts[0].upper()}: {parts[1].strip(chr(34))} / {parts[2].strip(chr(34))} / {parts[3].strip(chr(34))}\n")

    csv_file2 = os.path.join(ruta2, f"{destino}.csv")
    if os.path.exists(csv_file2):
        os.remove(csv_file2)
    shutil.copy2(csv_file, csv_file2)
    if os.path.exists(csv_file):
        os.remove(csv_file)

    zip_file = os.path.join(ruta2, f"{destino}_CSV.zip")
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_file2, os.path.basename(csv_file))
        zipf.write(readme_file, os.path.basename(readme_file))
    os.remove(csv_file2)
    os.remove(readme_file)

def generate_datasets(sql):
    datasets = execute_sql(sql)

    # Sortu GPKG karpeta existitzen ez bada
    if not os.path.exists(gpkg_dir):
        os.makedirs(gpkg_dir)

    total_datasets = len(datasets)
    start_time = time.time()
    processed_datasets = 0

    for i, (name, origen, destino, extension, formato, namefield, campos_csv) in enumerate(datasets, start=1):
        iteration_start = time.time()
        log(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {i}/{total_datasets} - {destino} - {name} - {formato} - ")

        try:
            # 1. Lehenik eta behin GPKG fitxategia sortu (campos_csv parametroa gehitu da)
            intermediate_gpkg = generate_gpkg(origen, destino, campos_csv)

            # 2. Formatuaren arabera prozesatu (campos_csv parametroa gehitu da funtzio guztietan)
            if formato == "GPKG":
                target_file = os.path.join(ruta2, f"{destino}.gpkg")
                shutil.copy2(intermediate_gpkg, target_file)
            elif formato == "SHP":
                generate_shp(intermediate_gpkg, destino, campos_csv)
            elif formato == "KML":
                generate_kml(intermediate_gpkg, destino, namefield, campos_csv)
            elif formato == "GeoJSON":
                generate_geojson(intermediate_gpkg, destino, campos_csv)
            elif formato == "CSV":
                generate_csv(intermediate_gpkg, destino, campos_csv)
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
