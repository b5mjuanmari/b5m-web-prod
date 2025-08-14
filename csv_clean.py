#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV fitxategietako kakotxak kentzen ditu komarik ez duten eremuetan.
Garbitutako CSV fitxategiak jatorrizko direktorioan gordetzen dira '_2' atzizkia duen direktorio berrian.
"""

import os
import sys
import csv

def garbitu_eremua(eremua):
    """Kendu kakotxak eremutik komarik ez badu"""
    if eremua.startswith('"') and eremua.endswith('"'):
        garbitua = eremua[1:-1]
        if ',' not in garbitua:
            return garbitua
    return eremua

def prozesatu_csv(sarrera_bidea, irteera_bidea):
    """CSV fitxategi bat prozesatu eta garbitu"""
    with open(sarrera_bidea, 'r', encoding='utf-8') as sarrera_fitx:
        irakurlea = csv.reader(sarrera_fitx)
        errenkadak = [errenkada for errenkada in irakurlea]

    with open(irteera_bidea, 'w', encoding='utf-8', newline='') as irteera_fitx:
        idazlea = csv.writer(irteera_fitx)
        for errenkada in errenkadak:
            garbitua = [garbitu_eremua(eremua) for eremua in errenkada]
            idazlea.writerow(garbitua)

def main():
    script_izena = os.path.basename(sys.argv[0])  # Script-aren izena lortu

    if len(sys.argv) != 2:
        print(f"Erabilera: python3 {script_izena} <csv_direktorioa>")  # Script-aren izena erabilera-mezuan
        sys.exit(1)

    sarrera_direktorioa = sys.argv[1]

    # Egiaztatu sarrera direktorioa existitzen dela
    if not os.path.isdir(sarrera_direktorioa):
        print(f"ERROREA: Direktorioa ez da existitzen: {sarrera_direktorioa}")
        sys.exit(1)

    # Bilatu CSV fitxategiak
    csv_fitxategiak = [f for f in os.listdir(sarrera_direktorioa)
                      if f.endswith('.csv')]

    if not csv_fitxategiak:
        print(f"ABISUA: Ez da CSV fitxategirik aurkitu {sarrera_direktorioa} direktorioan")
        return

    # Sortu irteera direktorioa (_2 atzizkia gehituta)
    irteera_direktorioa = f"{sarrera_direktorioa}_2"
    if not os.path.exists(irteera_direktorioa):
        os.makedirs(irteera_direktorioa)

    # Prozesatu CSV fitxategi bakoitza
    for csv_fitx in csv_fitxategiak:
        sarrera_bidea = os.path.join(sarrera_direktorioa, csv_fitx)
        irteera_bidea = os.path.join(irteera_direktorioa, csv_fitx)
        prozesatu_csv(sarrera_bidea, irteera_bidea)
        print(f"{csv_fitx} -> {irteera_direktorioa}/{csv_fitx}")

if __name__ == "__main__":
    main()
