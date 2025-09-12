#!/usr/bin/env python3
"""
Script honek CSV fitxategi batetik hiru CSV fitxategi sortzen ditu, hizkuntza bakoitzeko bat (eu, es, en).
Jatorrizko CSV fitxategiak field, fieldname_eu, fieldname_es, fieldname_en eremuak izan behar ditu.
"""

import csv
import sys
import os

def sortu_hizkuntzako_fitxategia(data, base_name, lang, fieldnames):
    """
    Hizkuntza baterako CSV fitxategia sortzen du.

    Args:
        data: Jatorrizko CSV fitxategiko datuak
        base_name: Jatorrizko fitxategiaren izena luzapenik gabe
        lang: Hizkuntzaren atzizkia (eu, es, en)
        fieldnames: Irteerako fitxategiaren goiburuak
    """
    output_file = f"{base_name}_{lang}.csv"

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in data:
                writer.writerow({
                    'field': row['field'],
                    f'fieldname_{lang}': row[f'fieldname_{lang}']
                })

        print(f"{output_file} fitxategia sortu da.")
        return True

    except Exception as e:
        print(f"Errorea {output_file} fitxategia sortzean: {e}")
        return False

def main():
    # Scriptaren izena lortu
    script_name = os.path.basename(sys.argv[0])

    # Parametroen kopurua egiaztatu
    if len(sys.argv) != 2:
        print(f"Erabilera: python3 {script_name} <csv_fitxategia>")
        sys.exit(1)

    # Jatorrizko CSV fitxategiaren izena lortu
    csv_file = sys.argv[1]

    # Fitxategia existitzen den egiaztatu
    if not os.path.isfile(csv_file):
        print(f"Errorea: '{csv_file}' fitxategia ez da existitzen.")
        sys.exit(1)

    # Jatorrizko fitxategiaren izena luzapenik gabe lortu
    base_name = os.path.splitext(csv_file)[0]

    try:
        # Jatorrizko CSV fitxategia ireki eta datuak memorian gorde
        with open(csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            # Goiburuak egiaztatu
            expected_headers = ['field', 'fieldname_eu', 'fieldname_es', 'fieldname_en']
            actual_headers = reader.fieldnames

            if not all(header in actual_headers for header in expected_headers):
                print("Errorea: Jatorrizko CSV fitxategiak ez ditu beharrezko goiburuak.")
                print(f"Beharrezko goiburuak: {', '.join(expected_headers)}")
                print(f"Fitxategiko goiburuak: {', '.join(actual_headers)}")
                sys.exit(1)

            # Datuak memorian gorde
            data = list(reader)

        # Hizkuntza bakoitzeko fitxategia sortu
        languages = ['eu', 'es', 'en']
        success = True

        for lang in languages:
            if not sortu_hizkuntzako_fitxategia(data, base_name, lang, ['field', f'fieldname_{lang}']):
                success = False

        if success:
            print("Prozesua ongi burutu da.")
        else:
            print("Erroreak gertatu dira prozesuan.")
            sys.exit(1)

    except Exception as e:
        print(f"Errorea fitxategia prozesatzean: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
