import os
import shutil
import sys
from datetime import datetime
import time
import csv
from tabulate import tabulate
import glob

# CSV direktorioa
CSV_DIR = "/home9/web5000/doc/reports/csv"

# Eguneko data
data_str = datetime.now().strftime("%Y%m%d")

def konfiguratu_loga():
    os.makedirs(log_dir, exist_ok=True)

    # Log fitxategiaren izena (script_izena_YYYYMMDD.log)
    script_izena = os.path.splitext(os.path.basename(__file__))[0]
    gaurko_data = datetime.now().strftime("%Y%m%d")
    log_fitxategia = os.path.join(log_dir, f"{script_izena}_{gaurko_data}.log")

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

def sortu_alderaketa_txostena(helburu_direktorioa, log_fitxategia):
    """Sortu alderaketa txostena helburuko direktorioaren eta aurreko bertsioaren artean"""
    # Lortu aurreko bertsioaren direktorioa (YYYYMMDD data kenduta)
    base_izena = os.path.basename(helburu_direktorioa)
    aurreko_izena = base_izena.split('_')[0]
    aurreko_direktorioa = os.path.join(os.path.dirname(helburu_direktorioa), aurreko_izena)

    if not os.path.isdir(aurreko_direktorioa):
        idatzi_logera(f"Oharra: Aurreko bertsiorik ez da aurkitu: {aurreko_direktorioa}", log_fitxategia, 1)
        return

    # Bilatu fitxategi guztiak bi direktorioetan
    helburu_fitxategiak = {}
    for root, _, files in os.walk(helburu_direktorioa):
        for file in files:
            erlatiboa = os.path.relpath(os.path.join(root, file), helburu_direktorioa)
            helburu_fitxategiak[erlatiboa] = os.path.getsize(os.path.join(root, file))

    aurreko_fitxategiak = {}
    for root, _, files in os.walk(aurreko_direktorioa):
        for file in files:
            erlatiboa = os.path.relpath(os.path.join(root, file), aurreko_direktorioa)
            aurreko_fitxategiak[erlatiboa] = os.path.getsize(os.path.join(root, file))

    # Sortu CSV direktorioa existitzen ez bada
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    # Ezabatu aurreko CSV fitxategiak
    txosten_izena = f"{CSV_DIR}/{data_str}_tiles_files.csv"
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
            "Tamaina (KB)",
            os.path.basename(aurreko_direktorioa),
            "Aurreko tamaina (KB)",
            "Aldea (%)"
        ])

        # 1. Taula: Fitxategi komunak
        komunak = set(helburu_fitxategiak.keys()) & set(aurreko_fitxategiak.keys())
        for fitxategia in sorted(komunak):
            tamaina_kb = helburu_fitxategiak[fitxategia] / 1024
            aurreko_tamaina_kb = aurreko_fitxategiak[fitxategia] / 1024
            aldea = ((tamaina_kb - aurreko_tamaina_kb) / aurreko_tamaina_kb) * 100 if aurreko_tamaina_kb != 0 else 0

            csvwriter.writerow([
                fitxategia,
                round(tamaina_kb, 2),
                fitxategia,
                round(aurreko_tamaina_kb, 2),
                round(aldea, 2)
            ])

    # 2. Taula: Fitxategi ezberdinak (logerako)

    # Ezberdinak
    berriak = set(helburu_fitxategiak.keys()) - set(aurreko_fitxategiak.keys())
    ezabatuak = set(aurreko_fitxategiak.keys()) - set(helburu_fitxategiak.keys())

    if berriak or ezabatuak:
        idatzi_logera("\n=== FITXATEGI EZBERDINAK ===", log_fitxategia, 0)

    # Helburuan bakarrik daudenak
    if berriak:
        berriak2 = [(f, round(helburu_fitxategiak[f] / 1024, 2)) for f in sorted(berriak)]
        idatzi_logera(f"\n{os.path.basename(helburu_direktorioa)}:\n", log_fitxategia, 0)
        idatzi_logera(tabulate(
            berriak2,
            headers=['Fitxategia', 'Tamaina (KB)'],
            tablefmt='grid'
        ), log_fitxategia, 0)

        # CSVa
        with open(txosten_izena, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for berriak2_1, berriak2_2 in berriak2:
                csvwriter.writerow([berriak2_1, berriak2_2, "-", "-", 100.0])

    # Aurrekoan bakarrik daudenak
    if ezabatuak:
        ezabatuak2 = [(f, round(aurreko_fitxategiak[f] / 1024, 2)) for f in sorted(ezabatuak)]
        idatzi_logera(f"\n{os.path.basename(aurreko_direktorioa)}:\n", log_fitxategia, 0)
        idatzi_logera(tabulate(
            ezabatuak2,
            headers=['Fitxategia', 'Tamaina (KB)'],
            tablefmt='grid'
        ), log_fitxategia, 0)

        # CSVa
        with open(txosten_izena, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for ezabatuak2_1, ezabatuak2_2 in ezabatuak2:
                csvwriter.writerow(["-", "-", ezabatuak2_1, ezabatuak2_2, 100.0])

    if berriak or ezabatuak:
        idatzi_logera("\n============================\n", log_fitxategia, 0)

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
            f"[{i}/{total}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {os.path.basename(fitxategia)}",
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
        f"Prozesuaren iraupena: {int(orduak)}h {int(minutuak)}m {int(segundoak)}s\n"
        f"{total} fitxategi kopiatu dira {helburu_osoa} helburura.",
        log_fitxategia,
        1
    )

    # Kopiatu ondoren, sortu alderaketa txostena
    sortu_alderaketa_txostena(helburu_osoa, log_fitxategia)

    return True

if __name__ == "__main__":
    # Log direktorioaren bidea
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    log_fitxategia = konfiguratu_loga()

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

    kopiatu_direktorioa(jatorrizkoa, helburua, log_fitxategia)
