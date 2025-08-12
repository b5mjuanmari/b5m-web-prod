#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
csv_to_oracle_update.py

CSV fitxategiak Oracle 11g-ko UPDATE sententzietara bihurtzen ditu, eremuetan
dauden kakotxak ("...") mantenduz eta lerroak jatorrizko formatuan gordez.
"""

import os
import sys
import csv

def egiaztatu_parametroak():
    if len(sys.argv) != 3:
        print(f"Errorea: Erabilera: python3 {sys.argv[0]} <csv_direktorioa> <irteerako_sql_fitxategia>")
        sys.exit(1)

    csv_dir = sys.argv[1]
    if not os.path.isdir(csv_dir):
        print(f"Errorea: '{csv_dir}' direktorioa ez da existitzen")
        sys.exit(1)

    csv_fitxategiak = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if not csv_fitxategiak:
        print(f"Errorea: '{csv_dir}' direktorioan ez da CSV fitxategirik aurkitu")
        sys.exit(1)

    return csv_dir, sys.argv[2], csv_fitxategiak

def csv_to_oracle_clob(csv_path):
    """CSV fitxategiaren edukia jatorrizko formatuan irakurtzen du"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        return f.read()

def sortu_update_sententzia(destino, clob_edukia):
    """UPDATE sententzia sortzen du, jatorrizko CSV formatua mantenduz"""
    clob_safe = clob_edukia.replace("'", "''")
    return f"""UPDATE datasets2_info
SET campos_csv = TO_CLOB(q'[{clob_safe}]')
WHERE destino = '{destino}';\n\n"""

def main():
    csv_dir, sql_irteera, csv_fitxategiak = egiaztatu_parametroak()
    total_fitxategiak = len(csv_fitxategiak)

    if os.path.exists(sql_irteera):
        os.remove(sql_irteera)

    with open(sql_irteera, 'w', encoding='utf-8') as sql_file:
        for idx, csv_fitx in enumerate(csv_fitxategiak, 1):
            csv_path = os.path.join(csv_dir, csv_fitx)
            destino = os.path.splitext(csv_fitx)[0]
            clob_edukia = csv_to_oracle_clob(csv_path)

            sql_file.write(sortu_update_sententzia(destino, clob_edukia))
            print(f"[{idx}/{total_fitxategiak}] {csv_fitx}")

if __name__ == "__main__":
    main()
