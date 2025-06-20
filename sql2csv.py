#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sys
import time
import cx_Oracle

# Oracle konexioa (ALDATU ZURE DATUEKIN)
ORACLE_CONN = "b5mweb_nombres/web+@exploracle:1521/bdet"

def garbitu_sql(sql_query):
    """SQL kontsulta garbitu:
    - ; karakterea kendu
    - Komentarioak kendu (-- eta /* */)
    - Lerro hutsak kendu
    """
    # Komentarioak kendu
    sql = '\n'.join([lerro.split('--')[0] for lerro in sql_query.split('\n')])
    sql = sql.split('/*')[0]  # /* */ komentarioak kentzeko

    # ; eta lerro hutsak kendu
    sql = sql.replace(';', '').strip()

    return sql

def main(sql_file_path, csv_file_path):
    """SQL exekutatu eta CSV-ra esportatu"""
    hasiera = time.time()

    try:
        # 1. Fitxategiak egiaztatu
        if not os.path.isfile(sql_file_path):
            raise FileNotFoundError(f"SQL fitxategia ez da existitzen: {sql_file_path}")

        if os.path.isfile(csv_file_path):
            os.remove(csv_file_path)
            print(f"Oharra: CSV fitxategi zaharra ezabatu da")

        # 2. SQL irakurri eta garbitu
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_query = garbitu_sql(f.read())
            if not sql_query:
                raise ValueError("SQL kontsulta hutsik dago")

        # 3. Oracle exekutatu
        with cx_Oracle.connect(ORACLE_CONN) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)

            # 4. CSV sortu
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([col[0] for col in cursor.description])  # Zutabe izenak
                writer.writerows(cursor)

            print(f"Arrakasta: {cursor.rowcount} errenkada esportatu dira")

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"ORACLE ERROR [{error.code}]: {error.message}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR [{type(e).__name__}]: {str(e)}")
        sys.exit(1)
    finally:
        print(f"Prozesua bukatuta. Iraupena: {round(time.time() - hasiera, 2)}s")

if __name__ == "__main__":
    script_izena = os.path.basename(sys.argv[0])

    if len(sys.argv) != 3:
        print(f"Erabilera: {script_izena} sarrera.sql irteera.csv")
        print(f"Adibidea: {script_izena} kontsulta.sql datuak.csv")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
