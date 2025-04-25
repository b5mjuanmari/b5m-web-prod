import os
import shutil
import sys
from datetime import datetime
import time

def konfiguratu_loga():
    # Log direktorioaren bidea
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    os.makedirs(log_dir, exist_ok=True)

    # Log fitxategiaren izena (script_izena_YYYYMMDD.log)
    script_izena = os.path.splitext(os.path.basename(__file__))[0]
    gaurko_data = datetime.now().strftime("%Y%m%d")
    log_fitxategia = os.path.join(log_dir, f"{script_izena}_{gaurko_data}.log")

    # Existitzen bada, ezabatu
    if os.path.exists(log_fitxategia):
        os.remove(log_fitxategia)

    return log_fitxategia

def idatzi_logera(mesedua, log_fitxategia):
    with open(log_fitxategia, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {mesedua}\n")

def kopiatu_direktorioa(jatorrizkoa, helburua, log_fitxategia):
    hasiera_denbora = time.time()
    idatzi_logera(f"Prozesua hasten.", log_fitxategia)

    if not os.path.isdir(jatorrizkoa):
        idatzi_logera("Errorea: Jatorrizko direktorioa ez da existitzen.", log_fitxategia)
        return False

    data_str = datetime.now().strftime("%Y%m%d")
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
    idatzi_logera(f"Guztira kopiatu beharreko fitxategiak: {total}", log_fitxategia)

    for i, fitxategia in enumerate(fitxategi_zerrenda, 1):
        idatzi_logera(
            f"[{i}/{total}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {os.path.basename(fitxategia)}",
            log_fitxategia
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
        log_fitxategia
    )
    return True

if __name__ == "__main__":
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
        idatzi_logera("Errorea: Helburu direktorioa ez da existitzen.", log_fitxategia)
        sys.exit(1)

    kopiatu_direktorioa(jatorrizkoa, helburua, log_fitxategia)
