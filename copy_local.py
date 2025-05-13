import os
import shutil
import sys
from datetime import datetime
import time
import csv
from tabulate import tabulate
import glob
import geopandas as gpd
import fiona
from fastkml import kml
import zipfile
import tempfile

# CSV direktorioa
CSV_DIR = "/home9/web5000/doc/reports/csv"

# Eguneko data
data_str = datetime.now().strftime("%Y%m%d")

def konfiguratu_loga(jatorrizkoa):
    os.makedirs(log_dir, exist_ok=True)

    # Log fitxategiaren izena (script_izena_YYYYMMDD.log)
    script_izena = os.path.splitext(os.path.basename(__file__))[0]
    gaurko_data = datetime.now().strftime("%Y%m%d")
    jat = jatorrizkoa.split('/')[-1].lower()
    log_fitxategia = os.path.join(log_dir, f"{script_izena}_{gaurko_data}_{jat}.log")

    # Existitzen bada, ezabatu
    if os.path.exists(log_fitxategia):
        os.remove(log_fitxategia)

    return log_fitxategia

def idatzi_logera(mezua, log_fitxategia, dataord):
    with open(log_fitxategia, "a") as f:
        if dataord == 0:
            f.write(f"{mezua}\n")
        else:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mezua}\n")

def lortu_elementu_kopuruak(fitxategi_bidea, log_fitxategia, i, total):
    """Lortu elementu kopuruak (Geo fitxategiak, CSV, edo ZIP barrukoak barne)"""
    try:
        idatzi_logera(f"[{i}/{total}] - {os.path.basename(fitxategi_bidea)}", log_fitxategia, 1)

        # ZIP fitxategientzat: deskonprimitu eta lehenengo onartutako fitxategia prozesatu
        if fitxategi_bidea.endswith('.zip'):
            with zipfile.ZipFile(fitxategi_bidea, 'r') as zip_ref:
                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_ref.extractall(tmpdir)
                    # Onartutako fitxategiak
                    onartuak = ['.gpkg', '.kml', '.shp', '.geojson', '.csv']
                    # Lehenengo egokia aurkitu
                    aurkitua = False
                    for root, _, files in os.walk(tmpdir):
                        for file in files:
                            if any(file.endswith(ext) for ext in onartuak):
                                full_path = os.path.join(root, file)
                                aurkitua = True
                                return lortu_elementu_kopuruak(full_path, log_fitxategia, i, total)
                    if not aurkitua:
                        print(f"Ez da onartutako fitxategirik aurkitu ZIP honetan: {fitxategi_bidea}")
            return None

        # GPKG fitxategientzat
        elif fitxategi_bidea.endswith('.gpkg'):
            total_elements = 0
            layers = fiona.listlayers(fitxategi_bidea)
            for layer in layers:
                try:
                    layer_gdf = gpd.read_file(fitxategi_bidea, layer=layer)
                    total_elements += len(layer_gdf)
                except Exception as e:
                    print(f"Errorea {fitxategi_bidea} (layer: {layer}) irakurtzean: {e}")
            return total_elements

        # KML fitxategientzat
        elif fitxategi_bidea.endswith('.kml'):
            from fastkml import kml
            with open(fitxategi_bidea, 'rb') as f:
                k = kml.KML()
                k.from_string(f.read())
                count = 0
                for d in k.features():
                    for fld in d.features():
                        count += len(list(fld.features()))
                return count

        # CSV fitxategientzat
        elif fitxategi_bidea.endswith('.csv'):
            with open(fitxategi_bidea, 'r', encoding='utf-8') as f:
                next(f)  # Goiburukoa saltatu nahi bada
                count = sum(1 for _ in f)
            return count

        # Beste formatuak (GeoJSON, SHP, ...)
        else:
            gdf = gpd.read_file(fitxategi_bidea)
            return len(gdf)

    except Exception as e:
        print(f"Errorea {fitxategi_bidea} irakurtzean: {e}")
        return None

def sortu_alderaketa_txostena(helburu_direktorioa, log_fitxategia):
    """Sortu alderaketa txostena helburuko direktorioaren eta aurreko bertsioaren artean"""
    alderaketa_hasiera = time.time()
    idatzi_logera("Alderaketa prozesua hasten...", log_fitxategia, 1)

    # Lortu aurreko bertsioaren direktorioa (YYYYMMDD data kenduta)
    base_izena = os.path.basename(helburu_direktorioa)
    aurreko_izena = base_izena.split('_')[0]
    aurreko_direktorioa = os.path.join(os.path.dirname(helburu_direktorioa), aurreko_izena)

    if not os.path.isdir(aurreko_direktorioa):
        aurreko_direktorioa2 = '/'.join(aurreko_direktorioa.split('/')[:-1] + [aurreko_direktorioa.split('/')[-1].upper()])
        if not os.path.isdir(aurreko_direktorioa2):
           idatzi_logera(f"Oharra: Aurreko bertsiorik ez da aurkitu: {aurreko_direktorioa}", log_fitxategia, 1)
           return
        else:
           aurreko_direktorioa = aurreko_direktorioa2
           helburu_direktorioa2 = '/'.join(helburu_direktorioa.split('/')[:-1] + [helburu_direktorioa.split('/')[-1].upper()])
           if os.path.exists(helburu_direktorioa2):
               shutil.rmtree(helburu_direktorioa2)
           os.rename(helburu_direktorioa, helburu_direktorioa2)
           helburu_direktorioa = helburu_direktorioa2

    # 1. Fasea: Fitxategi zerrendak bildu
    idatzi_logera("Fitxategi zerrendak bildu...", log_fitxategia, 1)

    # Bilatu fitxategi guztiak bi direktorioetan
    helburu_fitxategiak = {}
    helburu_fitxategi_zerrenda = []
    for root, _, files in os.walk(helburu_direktorioa):
        for file in files:
            if file.endswith(('.shp', '.gpkg', '.geojson', '.kml', '.csv', '.zip')):
                bide_osoa = os.path.join(root, file)
                erlatiboa = os.path.relpath(bide_osoa, helburu_direktorioa)
                helburu_fitxategi_zerrenda.append((erlatiboa, bide_osoa))

    aurreko_fitxategiak = {}
    aurreko_fitxategi_zerrenda = []
    for root, _, files in os.walk(aurreko_direktorioa):
        for file in files:
            if file.endswith(('.shp', '.gpkg', '.geojson', '.kml', '.csv', '.zip')):
                bide_osoa = os.path.join(root, file)
                erlatiboa = os.path.relpath(bide_osoa, aurreko_direktorioa)
                aurreko_fitxategi_zerrenda.append((erlatiboa, bide_osoa))

    # 2. Fasea: Elementu kopuruak kalkulatu (helburu direktorioa)
    idatzi_logera(f"Helburuko direktorioko {len(helburu_fitxategi_zerrenda)} fitxategi prozesatzen...", log_fitxategia, 1)
    for i, (erlatiboa, bide_osoa) in enumerate(helburu_fitxategi_zerrenda, 1):
        kopurua = lortu_elementu_kopuruak(bide_osoa, log_fitxategia, i, len(helburu_fitxategi_zerrenda))
        if kopurua is not None:
            helburu_fitxategiak[erlatiboa] = kopurua

    # 3. Fasea: Elementu kopuruak kalkulatu (aurreko direktorioa)
    idatzi_logera(f"Aurreko direktorioko {len(aurreko_fitxategi_zerrenda)} fitxategi prozesatzen...", log_fitxategia, 1)
    for i, (erlatiboa, bide_osoa) in enumerate(aurreko_fitxategi_zerrenda, 1):
        kopurua = lortu_elementu_kopuruak(bide_osoa, log_fitxategia, i, len(aurreko_fitxategi_zerrenda))
        if kopurua is not None:
            aurreko_fitxategiak[erlatiboa] = kopurua

    # Sortu CSV direktorioa existitzen ez bada
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    # Ezabatu aurreko CSV fitxategiak
    mota = helburu_direktorioa.split('/')[-1].split('_')[0].lower()
    txosten_izena = f"{CSV_DIR}/{data_str}_{mota}_features.csv"
    ezab_csv = glob.glob(txosten_izena.replace(data_str, "*"))
    for fitx_csv in ezab_csv:
        try:
            os.remove(fitx_csv)
        except OSError as e:
            print(f"Errorea '{fitx_csv}' ezabatzean: {e}")

    # Sortu CSV fitxategia
    with open(txosten_izena, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            os.path.basename(helburu_direktorioa),
            "Features",
            os.path.basename(aurreko_direktorioa),
            "Features (aurrekoa)",
            "Aldea (%)"
        ])

        # 1. Taula: Fitxategi komunak
        komunak = set(helburu_fitxategiak.keys()) & set(aurreko_fitxategiak.keys())
        for fitxategia in sorted(komunak):
            oraingoa = helburu_fitxategiak[fitxategia]
            aurrekoa = aurreko_fitxategiak[fitxategia]

            # Kalkulatu aldea
            if aurrekoa == 0:
                aldea = 0 if oraingoa == 0 else 100.0
            else:
                aldea = ((oraingoa - aurrekoa) / aurrekoa) * 100

            csvwriter.writerow([
                fitxategia,
                oraingoa,
                fitxategia,
                aurrekoa,
                round(aldea, 2)
            ])

    # 2. Taula: Fitxategi ezberdinak (logerako)
    berriak = set(helburu_fitxategiak.keys()) - set(aurreko_fitxategiak.keys())
    ezabatuak = set(aurreko_fitxategiak.keys()) - set(helburu_fitxategiak.keys())

    if berriak or ezabatuak:
        idatzi_logera("\n=== FITXATEGI EZBERDINAK ===", log_fitxategia, 0)

    # Helburuan bakarrik daudenak
    if berriak:
        berriak2 = [(f, helburu_fitxategiak[f]) for f in sorted(berriak)]
        idatzi_logera(f"\n{os.path.basename(helburu_direktorioa)}:\n", log_fitxategia, 0)
        idatzi_logera(tabulate(
            berriak2,
            headers=['Fitxategia', 'Features'],
            tablefmt='grid'
        ), log_fitxategia, 0)

        # CSVa
        with open(txosten_izena, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for fitx, kop in berriak2:
                csvwriter.writerow([fitx, kop, "-", "-", 100.0])

    # Aurrekoan bakarrik daudenak
    if ezabatuak:
        ezabatuak2 = [(f, aurreko_fitxategiak[f]) for f in sorted(ezabatuak)]
        idatzi_logera(f"\n{os.path.basename(aurreko_direktorioa)}:\n", log_fitxategia, 0)
        idatzi_logera(tabulate(
            ezabatuak2,
            headers=['Fitxategia', 'Features'],
            tablefmt='grid'
        ), log_fitxategia, 0)

        # CSVa
        with open(txosten_izena, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for fitx, kop in ezabatuak2:
                csvwriter.writerow(["-", "-", fitx, kop, 100.0])

    if berriak or ezabatuak:
        idatzi_logera("\n============================\n", log_fitxategia, 0)

    # Denbora-kontagailua bukatu
    iraupena = time.time() - alderaketa_hasiera
    orduak, resto = divmod(iraupena, 3600)
    minutuak, segundoak = divmod(resto, 60)
    denbora_mezua = (
        f"Alderaketa prozesuaren iraupena: "
        f"{int(orduak)}h {int(minutuak)}m {int(segundoak)}s\n"
        f"Guztira {len(helburu_fitxategiak)} fitxategi berri eta "
        f"{len(aurreko_fitxategiak)} fitxategi zahar alderatu dira"
    )
    idatzi_logera(denbora_mezua, log_fitxategia, 1)
    idatzi_logera(f"Alderaketa txostena sortu da: {txosten_izena}", log_fitxategia, 1)

def kopiatu_direktorioa(jatorrizkoa, helburua, log_fitxategia):
    hasiera_denbora = time.time()
    idatzi_logera(f"Prozesua hasten.", log_fitxategia, 1)

    if not os.path.isdir(jatorrizkoa):
        idatzi_logera("Errorea: Jatorrizko direktorioa ez da existitzen.", log_fitxategia, 1)
        return False

    helburu_izena = f"{os.path.basename(jatorrizkoa)}_{data_str}"
    helburu_osoa = os.path.join(helburua, helburu_izena)

    if os.path.exists(helburu_osoa):
        shutil.rmtree(helburu_osoa)

    os.makedirs(helburu_osoa, exist_ok=True)

    fitxategi_zerrenda = []
    for root, _, files in os.walk(jatorrizkoa):
        for file in files:
            fitxategi_zerrenda.append(os.path.join(root, file))

    total = len(fitxategi_zerrenda)
    idatzi_logera(f"Guztira kopiatu beharreko fitxategiak: {total}", log_fitxategia, 1)

    for i, fitxategia in enumerate(fitxategi_zerrenda, 1):
        idatzi_logera(
            f"[{i}/{total}] - {os.path.basename(fitxategia)}",
            log_fitxategia,
            1
        )
        erlatiboa = os.path.relpath(fitxategia, jatorrizkoa)
        helburu_fitxategia = os.path.join(helburu_osoa, erlatiboa)
        os.makedirs(os.path.dirname(helburu_fitxategia), exist_ok=True)
        shutil.copy2(fitxategia, helburu_fitxategia)

    iraupena = time.time() - hasiera_denbora
    orduak, resto = divmod(iraupena, 3600)
    minutuak, segundoak = divmod(resto, 60)
    idatzi_logera(
        f"Prozesua bukatuta."
        f" Prozesuaren iraupena: {int(orduak)}h {int(minutuak)}m {int(segundoak)}s\n"
        f"{total} fitxategi kopiatu dira {helburu_osoa} helburura.",
        log_fitxategia,
        1
    )

    # Kopiatu ondoren, sortu alderaketa txostena
    sortu_alderaketa_txostena(helburu_osoa, log_fitxategia)

    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        errorea = (
            f"Erabilera: python3 {os.path.basename(sys.argv[0])} "
            "<jatorrizko_direktorioa> <helburu_direktorioa>\n"
            f"Adibidea: python3 {os.path.basename(sys.argv[0])} "
            "/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles /home5/SHP"
        )
        print(errorea)
        sys.exit(1)

    jatorrizkoa = sys.argv[1]
    helburua = sys.argv[2]

    if not os.path.isdir(helburua):
        idatzi_logera("Errorea: Helburu direktorioa ez da existitzen.", log_fitxategia, 1)
        sys.exit(1)

    # Log direktorioaren bidea
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    log_fitxategia = konfiguratu_loga(jatorrizkoa)

    hasiera = time.time()
    kopiatu_direktorioa(jatorrizkoa, helburua, log_fitxategia)
    iraupena = time.time() - hasiera
    orduak, resto = divmod(iraupena, 3600)
    minutuak, segundoak = divmod(resto, 60)
    idatzi_logera(
        f"Prozesu osoaren iraupena: {int(orduak)}h {int(minutuak)}m {int(segundoak)}s.",
        log_fitxategia,
        1
    )
