#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

def log(mesedua):
    """Mezuak data eta orduarekin inprimatzen ditu"""
    print(f"{datetime.now().strftime('%Y%m%d %H:%M:%S')} - {mesedua}")

def konexioa_egiaztatu(zerbitzaria):
    """SSH konexioa egiaztatzen du"""
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
    """Urruneko direktorioa ezabatzen du existitzen bada"""
    log(f"{direktorioa} direktorioa existitzen den egiaztatzen {zerbitzaria} zerbitzarian...")
    cmd = f'ssh {zerbitzaria} "[ -d {direktorioa} ] && echo 1 || echo 0"'
    exists = subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()

    if exists == "1":
        log(f"{direktorioa} direktorioa ezabatzen...")
        subprocess.run(f'ssh {zerbitzaria} "rm -rf {direktorioa}"', shell=True, check=True)
        return True
    return False

def main():
    # Parametroak egiaztatu
    if len(sys.argv) != 4:
        log("Erabilera: ./copy_remote.py jatorrizko_direktorioa jatorrizko_zerbitzaria helburuko_zerbitzaria")
        sys.exit(1)

    source_dir = sys.argv[1].rstrip('/')
    source_server = sys.argv[2]
    target_server = sys.argv[3]

    # Konexioak egiaztatu
    if not konexioa_egiaztatu(source_server) or not konexioa_egiaztatu(target_server):
        sys.exit(1)

    # Helburuko direktorioaren izena sortu (jatorrizkoaren parent direktorio berean)
    dir_name = os.path.basename(source_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    remote_dir_name = f"{dir_name}_{timestamp}"
    remote_dir_path = os.path.join(os.path.dirname(source_dir), remote_dir_name)

    # Helburuko direktorioa existitzen bada, ezabatu
    direktorioa_ezabatu(target_server, remote_dir_path)

    # Fitxategiak kopiatu TAR erabiliz
    log(f"Fitxategiak kopiatzen: {source_server}:{source_dir} -> {target_server}:{remote_dir_path}")
    hasiera = datetime.now()

    try:
        # Komandoa: jatorritik TAR sortu eta helburuan deskonprimatu
        cmd = (
            f'ssh {source_server} "tar cf - -C {os.path.dirname(source_dir)} {os.path.basename(source_dir)}" | '
            f'ssh {target_server} "mkdir -p {remote_dir_path} && tar xf - -C {remote_dir_path}"'
        )

        prozesua = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        log(f"Errorea kopiatzean: {e.stderr.decode('utf-8')}")
        sys.exit(1)

    # Denbora kalkulatu
    denbora = (datetime.now() - hasiera).total_seconds()
    log(f"Kopia burututa! {denbora:.2f} segundu")
    log(f"Jatorrizkoa: {source_server}:{source_dir}")
    log(f"Helburua: {target_server}:{remote_dir_path}")

if __name__ == "__main__":
    main()
