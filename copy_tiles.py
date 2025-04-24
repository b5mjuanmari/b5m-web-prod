import os
import shutil
import sys
from datetime import datetime
import time

def kopiatu_direktorioa(jatorrizkoa, helburua):
    # Grabatu hasierako denbora
    hasiera_denbora = time.time()
    hasiera_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\nProzesua hasten: {hasiera_data}")

    # Egiaztatu jatorrizko direktorioa existitzen dela
    if not os.path.isdir(jatorrizkoa):
        print("Errorea: Jatorrizko direktorioa ez da existitzen.")
        return False

    # Sortu helburu direktorioaren izena data erantsiz
    data_str = datetime.now().strftime("%Y%m%d")
    helburu_izena = f"{os.path.basename(jatorrizkoa)}_{data_str}"
    helburu_osoa = os.path.join(helburua, helburu_izena)

    # Egiaztatu helburu direktorioa existitzen bada eta ezabatu
    if os.path.exists(helburu_osoa):
        shutil.rmtree(helburu_osoa)

    # Sortu helburu direktorioa
    os.makedirs(helburu_osoa, exist_ok=True)

    # Kontagailua eta denbora
    fitxategi_zerrenda = []
    for root, _, files in os.walk(jatorrizkoa):
        for file in files:
            fitxategi_zerrenda.append(os.path.join(root, file))

    total = len(fitxategi_zerrenda)
    print(f"Guztira kopiatu beharreko fitxategiak: {total}")

    for i, fitxategia in enumerate(fitxategi_zerrenda, 1):
        data_ordua = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{i}/{total}] {data_ordua} - {os.path.basename(fitxategia)}")

        # Kalkulatu helburuko bidea
        erlatiboa = os.path.relpath(fitxategia, jatorrizkoa)
        helburu_fitxategia = os.path.join(helburu_osoa, erlatiboa)

        # Sortu azpidirektorioak behar badira
        os.makedirs(os.path.dirname(helburu_fitxategia), exist_ok=True)

        # Kopiatu fitxategia
        shutil.copy2(fitxategia, helburu_fitxategia)

    # Kalkulatu iraupena
    bukaera_denbora = time.time()
    iraupena = bukaera_denbora - hasiera_denbora
    orduak, minutuak = divmod(iraupena, 3600)
    minutuak, segundoak = divmod(minutuak, 60)

    print(f"\nProzesua bukatuta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prozesuaren iraupena: {int(orduak)}h {int(minutuak)}m {int(segundoak)}s")
    print(f"{total} fitxategi kopiatu dira {helburu_osoa} helburura.")
    return True

if __name__ == "__main__":
    # Egiaztatu parametro kopurua
    if len(sys.argv) != 3:
        print("Erabilera: python3", os.path.basename(sys.argv[0]), "<jatorrizko_direktorioa> <helburu_direktorioa>")
        print("Adibidea: python3 copy_tiles.py /home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles /home5/SHP")
        sys.exit(1)

    jatorrizkoa = sys.argv[1]
    helburua = sys.argv[2]

    # Egiaztatu helburu direktorioa existitzen den
    if not os.path.isdir(helburua):
        print("Errorea: Helburu direktorioa ez da existitzen.")
        sys.exit(1)

    kopiatu_direktorioa(jatorrizkoa, helburua)
