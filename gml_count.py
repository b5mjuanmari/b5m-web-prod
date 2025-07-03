#
# gml_count.py
#
# Direktorio bateko ZIP fitxategietan konprimatuta dauden GMLen elementu kopurua kontatu
#
# Adibidea: python3 gml_count.py /home5/GML
#

import os
import sys
import zipfile
from xml.etree import ElementTree as ET

def kontatu_gml_elementuak(zip_fitxategia):
    """ZIP fitxategi baten barruko GML fitxategietako elementuen kopurua zenbatzen du."""
    elementu_kopurua = {}
    with zipfile.ZipFile(zip_fitxategia, 'r') as zip_ref:
        for fitxategi in zip_ref.namelist():
            if fitxategi.endswith('.gml'):
                with zip_ref.open(fitxategi) as gml_fitxategia:
                    tree = ET.parse(gml_fitxategia)
                    root = tree.getroot()
                    elementu_kopurua[fitxategi] = len(list(root))
    return elementu_kopurua

def main(direktorioa):
    """Direktorio bateko ZIP fitxategietako GML fitxategietako elementuen kopurua zenbatzen du."""
    txostena = {}
    for fitxategi in os.listdir(direktorioa):
        if fitxategi.endswith('.zip'):
            zip_bidea = os.path.join(direktorioa, fitxategi)
            txostena[fitxategi] = kontatu_gml_elementuak(zip_bidea)
    return txostena

if __name__ == "__main__":
    script_izena = sys.argv[0]
    if len(sys.argv) != 2:
        print(f"Erabilera: python3 {script_izena} direktorio_izena")
        sys.exit(1)

    direktorio_izena = sys.argv[1]
    if not os.path.isdir(direktorio_izena):
        print(f"Errorea: '{direktorio_izena}' direktorioa ez da existitzen.")
        sys.exit(1)

    txostena = main(direktorio_izena)
    print("GML fitxategietako elementuen kopurua:")
    for zip_fitxategia, gml_elementuak in txostena.items():
        print(f"{zip_fitxategia}:")
        for gml_fitxategia, kopurua in gml_elementuak.items():
            print(f"  {gml_fitxategia}: {kopurua} elementu")
