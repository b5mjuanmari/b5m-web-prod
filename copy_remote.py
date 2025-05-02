#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
import csv
import glob
import tempfile
import shutil

CSV_DIR = "/home9/web5000/doc/reports/csv"
TEMP_DIR = "/tmp/gpkg_alderaketa"  # Behin-behineko fitxategientzako direktorioa

def log(mezua):
    print(f"{datetime.now().strftime('%Y%m%d %H:%M:%S')} - {mezua}")

def konexioa_egiaztatu(zerbitzaria):
    log(f"{zerbitzaria} zerbitzariarekin konexioa egiaztatzen...")
    try:
        subprocess.run(
            ['ssh', zerbitzaria, 'echo', 'Konexioa ondo dago'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return True
    except subprocess.TimeoutExpired:
        log(f"Errorea: {zerbitzaria}-rekin konexio-denborak iraungi dira")
        return False
    except subprocess.CalledProcessError:
        log(f"Errorea: ezin konektatu {zerbitzaria}-ra")
        return False

def direktorioa_ezabatu(zerbitzaria, direktorioa):
    log(f"{direktorioa} direktorioa existitzen den egiaztatzen {zerbitzaria} zerbitzarian...")
    cmd = f'ssh {zerbitzaria} "[ -d {direktorioa} ] && echo 1 || echo 0"'
    exists = subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()
    if exists == "1":
        log(f"{direktorioa} direktorioa ezabatzen...")
        subprocess.run(f'ssh {zerbitzaria} "rm -rf {direktorioa}"', shell=True, check=True)
        return True
    return False

def kopiatu_zerbitzaritik_lokalera(zerbitzaria, jatorrizko_direktorioa, helburu_direktorioa):
    """Fitxategiak kopiatu zerbitzari urrunetik lokalera"""
    log(f"Kopiatzen {zerbitzaria}:{jatorrizko_direktorioa} -> {helburu_direktorioa}")

    # Helburuko direktorioa sortu
    os.makedirs(helburu_direktorioa, exist_ok=True)

    try:
        # Erabili rsync transferentzia fidagarriagoetarako
        cmd = [
            'rsync', '-az', '--timeout=300',
            f'{zerbitzaria}:{jatorrizko_direktorioa}/',
            helburu_direktorioa + '/'
        ]
        subprocess.run(cmd, check=True, timeout=600)
        return True
    except subprocess.TimeoutExpired:
        log(f"Errorea: denbora-muga gainditu da {zerbitzaria}-tik kopiatzean")
        return False
    except subprocess.CalledProcessError as e:
        log(f"Errorea kopiatzean {zerbitzaria}-tik: {e}")
        return False

def sortu_alderaketa_txostena(zerbitzaria, helburu_direktorioa):
    data_str = datetime.now().strftime("%Y%m%d")
    zerbitzari_izena = zerbitzaria.split("@")[1].split(".")[0] if "@" in zerbitzaria else zerbitzaria.split(".")[0]

    base_izena = os.path.basename(helburu_direktorioa)
    aurreko_izena = base_izena.split('_')[0]
    aurreko_direktorioa = os.path.join(os.path.dirname(helburu_direktorioa), aurreko_izena)

    # Sortu behin-behineko direktorioa kopietarako
    temp_dir = os.path.join(TEMP_DIR, f"konparaketa_{data_str}_{zerbitzari_izena}")
    os.makedirs(temp_dir, exist_ok=True)

    # Alderatzeko direktorioen bide lokalak
    local_helburu = os.path.join(temp_dir, "orain")
    local_aurreko = os.path.join(temp_dir, "aurreko")

    # Kopiatu fitxategiak zerbitzaritik lokalera
    if not kopiatu_zerbitzaritik_lokalera(zerbitzaria, helburu_direktorioa, local_helburu):
        log("Errorea: ezin izan dira uneko fitxategiak kopiatu")
        return

    if not kopiatu_zerbitzaritik_lokalera(zerbitzaria, aurreko_direktorioa, local_aurreko):
        log("Oharra: ezin izan dira aurreko fitxategiak kopiatu")
        # Jarraitu konparazioarekin, baina aurreko fitxategiak hutsik egongo dira

    def lortu_fitxategiak_lokalean(direktorioa):
        """Lortu fitxategi-tamainak direktorio lokaletik"""
        fitxategiak = {}
        if not os.path.exists(direktorioa):
            return fitxategiak

        for root, _, files in os.walk(direktorioa):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    tamaina = os.path.getsize(file_path)
                    erlatiboa = os.path.relpath(file_path, direktorioa)
                    fitxategiak[erlatiboa] = tamaina
                except OSError as e:
                    log(f"Errorea {file_path} fitxategiaren tamaina lortzean: {e}")
        return fitxategiak

    # Lortu fitxategiak lokalean (askoz azkarrago)
    helburu_fitxategiak = lortu_fitxategiak_lokalean(local_helburu)
    aurreko_fitxategiak = lortu_fitxategiak_lokalean(local_aurreko)

    # Sortu CSV fitxategia
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    txosten_izena = f"{CSV_DIR}/{data_str}_gpkg_{zerbitzari_izena}_files.csv"
    for fitx_csv in glob.glob(txosten_izena.replace(data_str, "*")):
        try:
            os.remove(fitx_csv)
        except OSError as e:
            log(f"Errorea '{fitx_csv}' ezabatzean: {e}")

    with open(txosten_izena, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            os.path.basename(helburu_direktorioa),
            "Tamaina (KB)",
            os.path.basename(aurreko_direktorioa),
            "Aurreko tamaina (KB)",
            "Aldea (%)"
        ])

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

        berriak = set(helburu_fitxategiak.keys()) - set(aurreko_fitxategiak.keys())
        for fitxategia in sorted(berriak):
            tamaina_kb = helburu_fitxategiak[fitxategia] / 1024
            csvwriter.writerow([fitxategia, round(tamaina_kb, 2), "-", "-", 100.0])

        ezabatuak = set(aurreko_fitxategiak.keys()) - set(helburu_fitxategiak.keys())
        for fitxategia in sorted(ezabatuak):
            aurreko_tamaina_kb = aurreko_fitxategiak[fitxategia] / 1024
            csvwriter.writerow(["-", "-", fitxategia, round(aurreko_tamaina_kb, 2), 100.0])

    log(f"Alderaketa-txostena sortu da: {txosten_izena}")

    # Garbitu behin-behineko fitxategiak
    try:
        shutil.rmtree(TEMP_DIR)
        log(f"Behin-behineko fitxategiak ezabatu dira: {TEMP_DIR}")
    except OSError as e:
        log(f"Errorea behin-behineko fitxategiak ezabatzean: {e}")

def main():
    if len(sys.argv) != 4:
        log("Erabilera: ./copy_remote.py jatorrizko_direktorioa jatorrizko_zerbitzaria helburuko_zerbitzaria")
        sys.exit(1)

    source_dir = sys.argv[1].rstrip('/')
    source_server = sys.argv[2]
    target_server = sys.argv[3]

    if not konexioa_egiaztatu(source_server) or not konexioa_egiaztatu(target_server):
        sys.exit(1)

    # Helburuko direktorioaren izena (data erantsiz)
    dir_name = os.path.basename(source_dir)
    timestamp = datetime.now().strftime("%Y%m%d")
    remote_dir_name = f"{dir_name}_{timestamp}"
    remote_dir_path = os.path.join(os.path.dirname(source_dir), remote_dir_name)

    # Existitzen bada, ezabatu
    direktorioa_ezabatu(target_server, remote_dir_path)

    # FITXATEGIAK KOPIATU
    log(f"Fitxategiak kopiatzen: {source_server}:{source_dir} -> {target_server}:{remote_dir_path}")
    hasiera = datetime.now()

    try:
        cmd = (
            f'ssh {source_server} "cd {source_dir} && tar cf - ." | '  # Jatorrizko direktorioan sartu eta bertako edukiak hartu
            f'ssh {target_server} "mkdir -p {remote_dir_path} && cd {remote_dir_path} && tar xf -"'  # Helburuan zuzenean deskonprimatu
        )
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        log(f"Errorea kopiatzean: {e.stderr.decode('utf-8') if e.stderr else str(e)}")
        sys.exit(1)

    denbora = (datetime.now() - hasiera).total_seconds()
    log(f"Kopia burututa! {denbora:.2f} segundu")
    log(f"Jatorrizkoa: {source_server}:{source_dir}")
    log(f"Helburua: {target_server}:{remote_dir_path}")

    sortu_alderaketa_txostena(target_server, remote_dir_path)

if __name__ == "__main__":
    main()
