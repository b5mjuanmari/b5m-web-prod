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

def sortu_alderaketa_txostena(zerbitzaria, helburu_direktorioa):
    data_str = datetime.now().strftime("%Y%m%d")
    zerbitzari_izena = zerbitzaria.split("@")[1].split(".")[0] if "@" in zerbitzaria else zerbitzaria.split(".")[0]

    base_izena = os.path.basename(helburu_direktorioa)
    aurreko_izena = base_izena.split('_')[0]
    aurreko_direktorioa = os.path.join(os.path.dirname(helburu_direktorioa), aurreko_izena)

    def lortu_fitxategiak(zerbitzaria, direktorioa):
        try:
            # SSH komandoa hobetu (erroreak eta timeout-ak kudeatzeko)
            cmd = (
                f'ssh -o ConnectTimeout=15 '          # 15 segundoko timeout
                f'-o BatchMode=yes '                 # Ez eskatu pasahitzarik
                f'-o StrictHostKeyChecking=no '      # Host key egiaztapena saltatu
                f'-o LogLevel=ERROR '                # Log erreferentziak murriztu
                f'{zerbitzaria} '
                f'"test -d {direktorioa} && find {direktorioa} -type f 2>/dev/null || echo \'ERROR_DIR\'"'
            )

            # Komandoa exekutatu timeout-ekin
            output = subprocess.check_output(
                cmd,
                shell=True,
                timeout=20,
                universal_newlines=True,
                stderr=subprocess.PIPE
            )

            if "ERROR_DIR" in output:
                log(f"Errorea: direktorioa ez da existitzen {zerbitzaria}:{direktorioa}")
                return {}

            fitxategiak = {}
            for line in output.splitlines():
                if not line.strip() or line == "ERROR_DIR":
                    continue

                # Fitxategiaren tamaina lortu (errore-kudeaketa gehiagorekin)
                tamaina_cmd = (
                    f'ssh -o ConnectTimeout=10 {zerbitzaria} '
                    f'"stat -c %s \'{line}\' 2>/dev/null || echo 0"'
                )
                tamaina = subprocess.check_output(
                    tamaina_cmd,
                    shell=True,
                    timeout=10,
                    universal_newlines=True
                ).strip()

                if tamaina.isdigit():
                    erlatiboa = os.path.relpath(line, direktorioa)
                    fitxategiak[erlatiboa] = int(tamaina)

            return fitxategiak

        except subprocess.TimeoutExpired:
            log(f"SSH timeout {zerbitzaria}-rekin direktorioa irakurtzean: {direktorioa}")
            return {}
        except subprocess.CalledProcessError as e:
            log(f"SSH errorea {zerbitzaria}-rekin. Stderr: {e.stderr}")
            return {}
        except Exception as e:
            log(f"Errore esperogabea {zerbitzaria}-rekin: {str(e)}")
            return {}

    # Fitxategiak lortu (errore-kudeaketa gehiagorekin)
    helburu_fitxategiak = lortu_fitxategiak(zerbitzaria, helburu_direktorioa)
    if not helburu_fitxategiak:
        log(f"Errorea: ezin izan dira fitxategiak lortu {helburu_direktorioa}-n")
        return

    aurreko_fitxategiak = lortu_fitxategiak(zerbitzaria, aurreko_direktorioa)
    if not aurreko_fitxategiak:
        log(f"Oharra: aurreko bertsiorik ez da aurkitu {aurreko_direktorioa}-n")

    # CSV fitxategia sortu
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
    # Jatorrizko direktorioaren edukia zuzenean helburuko direktorioan kopiatu (azpidirektoriorik gabe)
    log(f"Fitxategiak kopiatzen: {source_server}:{source_dir} -> {target_server}:{remote_dir_path}")
    hasiera = datetime.now()

    try:
        cmd = (
            f'ssh {source_server} "cd {source_dir} && tar cf - ." | '  # Jatorrizko direktorioan sartu eta bertako edukiak hartu
            f'ssh {target_server} "mkdir -p {remote_dir_path} && cd {remote_dir_path} && tar xf -"'  # Helburuan zuzenean deskonprimatu
        )
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        log(f"Errorea kopiatzean: {e.stderr.decode('utf-8')}")
        sys.exit(1)

    denbora = (datetime.now() - hasiera).total_seconds()
    log(f"Kopia burututa! {denbora:.2f} segundu")
    log(f"Jatorrizkoa: {source_server}:{source_dir}")
    log(f"Helburua: {target_server}:{remote_dir_path}")

    sortu_alderaketa_txostena(target_server, remote_dir_path)

if __name__ == "__main__":
    main()
