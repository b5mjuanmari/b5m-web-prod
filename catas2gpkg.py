import os
import sys
import subprocess
from datetime import datetime

def ezabatu_gpkg(gpkg_path):
    """GPKG fitxategia existitzen bada, ezabatu."""
    if os.path.exists(gpkg_path):
        os.remove(gpkg_path)
        print(f"GPKG fitxategia {gpkg_path} ezabatu da.")

def kargatu_shapefile_gpkg(sfp, gpkg_path):
    """Shapefile bat GPKG fitxategi batean kargatu."""
    command = [
        "ogr2ogr",
        "-f", "GPKG",
        "-update",
        "-append",
        "-nlt", "PROMOTE_TO_MULTI",
        gpkg_path,
        sfp
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Shapefile {sfp} ondo kargatu da GPKG fitxategian.")
    except subprocess.CalledProcessError as e:
        print(f"Errorea gertatu da shapefile-a GPKG fitxategian kargatzean: {e}")

def main(direktorioa, gpkg_path):
    # Hasiera
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Hasiera")

    # GPKG fitxategia ezabatu existitzen bada
    ezabatu_gpkg(gpkg_path)

    # Prozesatu behar diren fitxategi guztien zerrenda lortu
    shapefiles = [f for f in os.listdir(direktorioa) if f.endswith('.shp')]
    total_shapefiles = len(shapefiles)

    for index, fitxategia in enumerate(shapefiles, start=1):
        shapefile_path = os.path.join(direktorioa, fitxategia)
        uneko_data_ordua = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{uneko_data_ordua} - [{index}/{total_shapefiles}] {fitxategia} fitxategia prozesatzen...")

        # Shapefile bat GPKG fitxategi batean kargatu
        kargatu_shapefile_gpkg(shapefile_path, gpkg_path)

    # Bukaera
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Bukaera")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        script_izena = sys.argv[0]
        print(f"Erabilera: python3 {script_izena} direktorioa gpkg_path")
        sys.exit(1)

    direktorioa = sys.argv[1]
    gpkg_path = sys.argv[2]
    main(direktorioa, gpkg_path)
