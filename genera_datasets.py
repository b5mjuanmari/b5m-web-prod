import os
import cx_Oracle
import subprocess
import zipfile
import csv
from datetime import datetime
import inspect

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

ruta1 = "/home5/SHP"
ruta2 = "/home/data/datos_explotacion/CUR/datasets"
log_file = f"/home/lidar/SCRIPTS/WEB_PROD/log/genera_datasets_{datetime.now().strftime('%Y%m%d')}.log"

def log(message):
    """Idazten du log fitxategian."""
    with open(log_file, "a") as logf:
        logf.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    #print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def format_duration(duration):
    """Denbora iraupena H:MM:SS formatuan itzultzen du."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds:02}"

def execute_sql(query):
    """Exekutatzen du SQL kontsulta bat eta emaitzak itzultzen ditu."""
    try:
        with cx_Oracle.connect(db_user, db_pass, db_dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = []
                for row in cursor:
                    # LOB eremuak irakurri eta string bihurtu
                    new_row = tuple(col.read() if isinstance(col, cx_Oracle.LOB) else col for col in row)
                    results.append(new_row)
                return results
    except cx_Oracle.DatabaseError as e:
        log(f"Errorea SQL exekutzean: {e}")
        return []

def generate_datasets():
    """Dataset-ak sortzen ditu."""
    sql = """
    SELECT a.nombre_es, a.origen, a.destino, b.extension, b.formato, b.namefield
    FROM b5mweb_nombres.datasets_info a
    JOIN b5mweb_nombres.datasets_ficheros b ON a.id_dataset = b.id_dataset
    WHERE a.crear = 1
    ORDER BY a.orden"""

    datasets = execute_sql(sql)

    for i, (nombre, origen, destino, extension, formato, namefield) in enumerate(datasets, start=1):
        log(f"{i}/{len(datasets)} - {nombre} - {formato}")
        f1 = os.path.join(ruta1, f"{origen}.shp")
        if formato == "SHP" or formato == "CSV":
            #f2 = os.path.join(ruta2, f"{destino}_{formato}.zip")
            f2 = os.path.join(ruta2, f"{destino}.zip")
        else:
            f2 = os.path.join(ruta2, f"{destino}{extension}")

        # Helburuko fitxategiak existitzen badira, ezabatu
        if os.path.exists(f2):
            os.remove(f2)

        if formato == "SHP":
            # origen kontsulta SQL bat ez bada, begiratu fitxategia existitzen den (Katastroaren kasua)
            if not origen.strip().lower().startswith("select"):
                d1 = os.path.join(ruta1, f"{origen}")  # Jatorrizko karpeta
                if not os.path.exists(f1):  # Fitxategia existitzen ez bada
                    # ZIP fitxategia sortu jatorrizko karpetako fitxategiekin
                    try:
                        with zipfile.ZipFile(f2, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for root, dirs, files in os.walk(d1):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    zipf.write(file_path, os.path.relpath(file_path, d1))
                    except Exception as e:
                        log(f"Errorea #1 ZIP fitxategia sortzean: {e}")
                    continue  # Hurrengo datu-multzora pasatzen

            shp_files = [f"{ruta2}/{destino}.{ext}" for ext in ["shp", "shx", "dbf", "prj"]]
            for shp_file in shp_files:
                if os.path.exists(shp_file):
                    os.remove(shp_file)

            ogr2ogr_command = [ogr2ogr_bin, "-f", "ESRI Shapefile", "-s_srs", "EPSG:25830", "-t_srs", "EPSG:25830", shp_files[0]]

            # origen aldagaia kontsulta SQL bada, -sql parametroa gehitu
            if origen.strip().lower().startswith("select"):
                ogr2ogr_command.extend(["-sql", origen, f"OCI:{db_user2}/{db_pass}@{db_dsn}:{db_tab}"])
            else:
                ogr2ogr_command.append(f1)

            subprocess.run(ogr2ogr_command, check=True)

            with zipfile.ZipFile(f2, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for shp_file in shp_files:
                    if os.path.exists(shp_file):
                        try:
                            zipf.write(shp_file, os.path.basename(shp_file))
                        except Exception as e:
                            log(f"Errorea #2 ZIP fitxategia sortzean: {e}")
                        os.remove(shp_file)
        elif formato == "KML":
            ogr2ogr_command = [ogr2ogr_bin, "-f", "KML", "-s_srs", "EPSG:25830", "-t_srs", "EPSG:4326", "-nln", destino, "-dsco", f"NameField={namefield}", "-mapFieldType", "Integer64=Real", f2]

            # origen aldagaia kontsulta SQL bada, -sql parametroa gehitu
            if origen.strip().lower().startswith("select"):
                ogr2ogr_command.extend(["-sql", origen, f"OCI:{db_user2}/{db_pass}@{db_dsn}:{db_tab}"])
            else:
                ogr2ogr_command.append(f1)

            subprocess.run(ogr2ogr_command, check=True)
        elif formato == "GeoJSON":
            ogr2ogr_command = [ogr2ogr_bin, "-f", "GeoJSON", "-s_srs", "EPSG:25830", "-t_srs", "EPSG:4326", "-nln", destino, f2]

            # origen aldagaia kontsulta SQL bada, -sql parametroa gehitu
            if origen.strip().lower().startswith("select"):
                ogr2ogr_command.extend(["-sql", origen, f"OCI:{db_user2}/{db_pass}@{db_dsn}:{db_tab}"])
            else:
                ogr2ogr_command.append(f1)

            subprocess.run(ogr2ogr_command, check=True)
        elif formato == "CSV":
            f_csv = os.path.join(ruta2, f"{destino}.csv")

            # Fitxategiak existitzen badira, ezabatu
            if os.path.exists(f_csv):
                os.remove(f_csv)

            # SQL exekutatu eta emaitzak lortu
            if origen.strip().lower().startswith("select"):
                try:
                    with cx_Oracle.connect(db_user, db_pass, db_dsn) as conn:
                        with conn.cursor() as cursor:
                            cursor.execute(origen)
                            columns = [desc[0].lower() for desc in cursor.description]  # Zutabe-izenak
                            csv_data = cursor.fetchall()
                except cx_Oracle.DatabaseError as e:
                    log(f"Errorea SQL exekutzean: {e}")
                    return

                # CSV fitxategia sortu eta datuak idatzi kakotxekin
                try:
                    with open(f_csv, "w", encoding="utf-8", newline="") as f:
                        writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
                        writer.writerow(columns)  # Zutabe-izenak idatzi lehenengo ilaran
                        writer.writerows(csv_data)  # Datu guztiak idatzi
                except Exception as e:
                    log(f"Errorea CSV fitxategia idaztean: {e}")
                    return
            else:
                ogr2ogr_command = [ogr2ogr_bin, "-f", "CSV", "-s_srs", "EPSG:25830", "-t_srs", "EPSG:25830", "-nln", destino, "-lco", "GEOMETRY=AS_XY", f_csv, f1]
                subprocess.run(ogr2ogr_command, check=True)

            # CSV fitxategia ZIP bihurtu
            try:
                with zipfile.ZipFile(f2, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(f_csv, os.path.basename(f_csv))
            except Exception as e:
                log(f"Errorea CSV fitxategia konprimatzean: {e}")
                return

            # CSV fitxategia ezabatu
            try:
                os.remove(f_csv)
            except Exception as e:
                log(f"Errorea CSV fitxategia ezabatzean: {e}")
        else:
            log(f"{formato} ez da onartzen.")

if __name__ == "__main__":
    script_start_time = datetime.now()
    log(f"Script-aren hasiera: {script_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Log fitxategia ezabatu script-a hasi aurretik
    if os.path.exists(log_file):
        os.remove(log_file)

    if not os.path.exists(ruta2):
        os.makedirs(ruta2)

    log(f"Hasiera: {os.path.abspath(__file__)}")
    generate_datasets()
    script_end_time = datetime.now()
    script_duration = script_end_time - script_start_time
    log(f"Bukaera: {os.path.abspath(__file__)}")
    log(f"Denbora: {format_duration(script_duration)}")
