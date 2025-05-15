#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
import csv
import glob

CSV_DIR = "/home9/web5000/doc/reports/csv"

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
            timeout=10  # Denbora-muga handitu
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
    cmd = f'ssh -o ConnectTimeout=30 {zerbitzaria} "[ -d {direktorioa} ] && echo 1 || echo 0"'
    exists = subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()
    if exists == "1":
        log(f"{direktorioa} direktorioa ezabatzen...")
        subprocess.run(f'ssh -o ConnectTimeout=30 {zerbitzaria} "rm -rf {direktorioa}"', shell=True, check=True)
        return True
    return False

def sortu_alderaketa_txostena(zerbitzaria, helburu_direktorioa):
    import re

    data_str = datetime.now().strftime("%Y%m%d")
    zerbitzari_izena = zerbitzaria.split("@")[1].split(".")[0] if "@" in zerbitzaria else zerbitzaria.split(".")[0]
    base_izena = os.path.basename(helburu_direktorioa)
    aurreko_izena = base_izena.split('_')[0]
    aurreko_direktorioa = os.path.join(os.path.dirname(helburu_direktorioa), aurreko_izena)

    def lortu_elementu_kopuruak(direktorioa):
        """
        Zerbitzariaren direktorio batean dauden .shp eta .gpkg fitxategien elementu-kopurua lortzen du.
        """
        komandoa = f'''
        cd {direktorioa} && \
        find . \\( -name "*.shp" -o -name "*.gpkg" \\) -type f | while read f; do
            if [[ "$f" == *.shp ]]; then
                count=$(ogrinfo -ro -al "$f" 2>/dev/null | grep "Feature Count" | awk -F': ' '{{print $2}}')
            elif [[ "$f" == *.gpkg ]]; then
                count=0
                for layer in $(ogrinfo -so -al "$f" | grep "Layer name" | awk '{{print $3}}'); do
                    lay_count=$(ogrinfo "$f" -sql "SELECT COUNT(*) FROM '$layer'" 2>/dev/null | grep "COUNT_*" | awk '{{print $4}}')
                    count=$((count + lay_count))
                done
            else
                count=0
            fi
            echo "${{f#./}}:$count"
        done
        '''

        try:
            output = subprocess.check_output(
                ["ssh", zerbitzaria, komandoa],
                universal_newlines=True,
                timeout=300
            )
            emaitzak = {}
            for lerroa in output.strip().splitlines():
                if ":" in lerroa:
                    izena, kopurua = lerroa.rsplit(":", 1)
                    emaitzak[izena.strip()] = int(kopurua)
            return emaitzak
        except subprocess.CalledProcessError as e:
            log(f"Errorea: {direktorioa}-n elementu kopuruak lortzean")
            return {}
        except Exception as e:
            log(f"Errore esperogabea: {str(e)}")
            return {}

    helburu_elem = lortu_elementu_kopuruak(helburu_direktorioa)
    if not helburu_elem:
        log("Errorea: helburuko fitxategietatik ez da ezer lortu")
        return

    aurreko_elem = lortu_elementu_kopuruak(aurreko_direktorioa)
    if not aurreko_elem:
        log("Oharra: aurreko bertsiorik ez da aurkitu")
        aurreko_elem = {}

    # CSV fitxategia prestatu
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    txosten_izena = f"{CSV_DIR}/{data_str}_gpkg_{zerbitzari_izena}_features.csv"
    for zaharra in glob.glob(txosten_izena.replace(data_str, "*")):
        try:
            os.remove(zaharra)
        except OSError as e:
            log(f"Errorea '{zaharra}' ezabatzean: {e}")

    with open(txosten_izena, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            os.path.basename(helburu_direktorioa),
            "Features",
            os.path.basename(aurreko_direktorioa),
            "Previous",
            "Diff %"
        ])

        komunak = set(helburu_elem) & set(aurreko_elem)
        for fitx in sorted(komunak):
            h = helburu_elem[fitx]
            a = aurreko_elem[fitx]
            aldea = ((h - a) / a * 100) if a != 0 else 100
            csvwriter.writerow([fitx, h, fitx, a, round(aldea, 2)])

        berriak = set(helburu_elem) - set(aurreko_elem)
        for fitx in sorted(berriak):
            csvwriter.writerow([fitx, helburu_elem[fitx], "-", "-", 100.0])

        ezabatuak = set(aurreko_elem) - set(helburu_elem)
        for fitx in sorted(ezabatuak):
            csvwriter.writerow(["-", "-", fitx, aurreko_elem[fitx], 100.0])

    log(f"Alderaketa-txostena sortu da: {txosten_izena}")

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

    # KOPIA EGITEKO KOMANDO BERRI ZUZENDUA:
    log(f"Fitxategiak kopiatzen: {source_server}:{source_dir} -> {target_server}:{remote_dir_path}")
    hasiera = datetime.now()

    try:
        cmd = (
            f'ssh -o ConnectTimeout=120 {source_server} "cd {source_dir} && tar cf - ." | '
            f'ssh -o ConnectTimeout=120 {target_server} "mkdir -p {remote_dir_path} && cd {remote_dir_path} && tar xf -"'
        )
        subprocess.run(cmd, shell=True, check=True, timeout=600)  # Denbora-muga handitu
    except subprocess.TimeoutExpired:
        log("Errorea: kopiak denbora-muga gainditu du (10 minutuk baino gehiago iraun du)")
        sys.exit(1)
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
