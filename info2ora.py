#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
info2ora.py

Fitxategiak Oracle 11g-ra eguneratzeko script-a:
- CSV fitxategiak → campos_csv eremua (jatorrizko formatua mantenduz)
- SQL fitxategiak → origen eremua (kontsultako ';' amaiera kenduz)
"""

import os
import sys

def kendu_azken_puntukoma(sql_edukia):
    """SQL sententziaren azkeneko ';' kentzen du baldin badago"""
    return sql_edukia.rstrip().rstrip(';')

def egiaztatu_parametroak():
    if len(sys.argv) != 3:
        print(f"Erabilera: python3 {sys.argv[0]} <sarrera> <irteera.sql>")
        sys.exit(1)

    sarrera = sys.argv[1]
    if not os.path.exists(sarrera):
        print("Errorea: Sarrerako fitxategia/direktorioa ez da existitzen")
        sys.exit(1)

    return sarrera, sys.argv[2]

def bilatu_fitxategiak(sarrera):
    if os.path.isfile(sarrera):
        if not sarrera.lower().endswith(('.csv','.sql')):
            print("Errorea: Fitxategiak CSV edo SQL luzapena izan behar du")
            sys.exit(1)
        return [sarrera]

    fitxategiak = [os.path.join(sarrera, f) for f in os.listdir(sarrera)
                 if f.lower().endswith(('.csv','.sql'))]

    if not fitxategiak:
        print("Errorea: Ez da CSV edo SQL fitxategirik aurkitu")
        sys.exit(1)

    return fitxategiak

def sortu_update(fitxategia):
    izena = os.path.splitext(os.path.basename(fitxategia))[0]

    try:
        with open(fitxategia, 'r', encoding='utf-8') as f:
            edukia = f.read().strip()

        if fitxategia.lower().endswith('.csv'):
            return f"""UPDATE datasets2_info
SET campos_csv = TO_CLOB(q'[{edukia.replace("'","''")}]')
WHERE destino = '{izena}';\n"""

        elif fitxategia.lower().endswith('.sql'):
            garbitua = kendu_azken_puntukoma(edukia)
            return f"""UPDATE datasets2_info
SET origen = '{garbitua.replace("'","''")}'
WHERE destino = '{izena}';\n"""

    except Exception as e:
        print(f"Errorea {fitxategia} irakurtzean: {str(e)}")
        return None

def main():
    sarrera, irteera = egiaztatu_parametroak()
    fitxategiak = bilatu_fitxategiak(sarrera)

    if os.path.exists(irteera):
        os.remove(irteera)

    with open(irteera, 'w', encoding='utf-8') as out:
        for i, fitx in enumerate(fitxategiak, 1):
            update = sortu_update(fitx)
            if update:
                out.write(update)
                print(f"[{i}/{len(fitxategiak)}] {os.path.basename(fitx)}")

    print(f"\nEginda! {len(fitxategiak)} fitxategi prozesatu dira.")

if __name__ == "__main__":
    main()
