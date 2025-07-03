import os
import sys
import subprocess
import cx_Oracle
from datetime import datetime

# Oracle konexio parametroak
user = "mapas_otros"
password = "web+"
host = "exploracle"
port = "1521"
service = "bdet"
geom_table = "euskalerri"

def ezabatu_taula_eta_metadatuak(oracle_conn, taula_izena):
    cursor = oracle_conn.cursor()

    # Taula existitzen bada, ezabatu
    try:
        cursor.execute(f"DROP TABLE {taula_izena}")
        #print(f"Taula {taula_izena} ezabatu da.")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        #if error.code == 942:
        #    print(f"Taula {taula_izena} ez zegoen, ez da ezabatu.")
        #else:
        #    raise

    # Metadatuak ezabatu
    try:
        cursor.execute(f"DELETE FROM user_sdo_geom_metadata WHERE table_name = '{taula_izena.upper()}'")
        cursor.execute("commit")
        #print(f"Metadatuak {taula_izena} taularentzat ezabatu dira.")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Errorea metadatuak ezabatzean: {error.message}")

    cursor.close()

def kargatu_shapefile_oracle(sfp, oci_connection_string, taula_izena):
    # ogr2ogr komandoa exekutatu Shapefile bat Oracle datu-base batera kargatzeko
    command = [
        "ogr2ogr",
        "-f", "OCI",
        f"OCI:{oci_connection_string}",
        "-nln", taula_izena,
        "-lco", "DIM=2",
        "-lco", "SRID=25830",
        "-lco", "GEOMETRY_NAME=GEOM",
        "-nlt", "PROMOTE_TO_MULTI",
        sfp
    ]

    try:
        subprocess.run(command, check=True)
        #print(f"Shapefile {sfp} ondo kargatu da Oracle datu-basean {taula_izena} taula gisa.")
    except subprocess.CalledProcessError as e:
        print(f"Errorea gertatu da shapefile-a Oracle datu-basean kargatzean: {e}")

def main(direktorioa):
    # Hasiera
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Hasiera")

    # Oracle konexioa
    oracle_conn = cx_Oracle.connect(user=user, password=password, dsn=f"{host}:{port}/{service}")

    # OCI konexio katea sortu
    oci_connection_string = f"{user}/{password}@{service}:{geom_table}"

    # Prozesatu behar diren fitxategi guztien zerrenda lortu
    shapefiles = [f for f in os.listdir(direktorioa) if f.endswith('.shp')]
    total_shapefiles = len(shapefiles)

    for index, fitxategia in enumerate(shapefiles, start=1):
        shapefile_path = os.path.join(direktorioa, fitxategia)
        taula_izena = f"catas_{os.path.splitext(fitxategia)[0]}"
        taula_izena = taula_izena.lower()  # Letra xehez
        taula_izena = '_'.join(taula_izena.split('_')[:-1])
        uneko_data_ordua = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{uneko_data_ordua} - [{index}/{total_shapefiles}] {taula_izena} taula prozesatzen...")

        # Taula eta metadatuak ezabatu
        ezabatu_taula_eta_metadatuak(oracle_conn, taula_izena)

        # Shapefile bat Oracle datu-base batera kargatu
        kargatu_shapefile_oracle(shapefile_path, oci_connection_string, taula_izena)

    # Itxi Oracle konexioa
    oracle_conn.close()

    # Bukaera
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Bukaera")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        script_izena = sys.argv[0]
        print(f"Erabilera: python3 {script_izena} direktorioa")
        sys.exit(1)

    direktorioa = sys.argv[1]
    main(direktorioa)
