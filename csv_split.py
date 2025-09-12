#!/usr/bin/env python3
"""
Script honek direktorio bateko CSV fitxategi guztiak prozesatzen ditu, hizkuntzaka bananduz.
Jatorrizko CSV fitxategiak field, fieldname_eu, fieldname_es, fieldname_en eremuak izan behar ditu.
Emaitzak 'csv_split' azpikarpeta batean gordetzen ditu.
"""

import csv
import sys
import os
import stat

def sortu_hizkuntzako_fitxategia(data, base_name, lang, fieldnames, output_dir):
    """
    Hizkuntza baterako CSV fitxategia sortzen du output direktorioan.

    Args:
        data: Jatorrizko CSV fitxategiko datuak
        base_name: Jatorrizko fitxategiaren izena luzapenik gabe
        lang: Hizkuntzaren atzizkia (eu, es, en)
        fieldnames: Irteerako fitxategiaren goiburuak
        output_dir: Irteerako direktorioa
    """
    output_file = os.path.join(output_dir, f"{base_name}_{lang}.csv")

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

def process_csv_file(input_file, output_dir):
    """
    CSV fitxategi bat prozesatzen du eta hizkuntzaka banatzen du.

    Args:
        input_file: Prozesatu beharreko CSV fitxategia
        output_dir: Irteerako direktorioa
    """
    try:
        # Jatorrizko fitxategiaren izena luzapenik gabe lortu
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Jatorrizko CSV fitxategia ireki eta datuak memorian gorde
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            # Goiburuak egiaztatu
            expected_headers = ['field', 'fieldname_eu', 'fieldname_es', 'fieldname_en']
            actual_headers = reader.fieldnames

            if not all(header in actual_headers for header in expected_headers):
                print(f"Errorea: '{input_file}' fitxategiak ez ditu beharrezko goiburuak.")
                print(f"Beharrezko goiburuak: {', '.join(expected_headers)}")
                print(f"Fitxategiko goiburuak: {', '.join(actual_headers)}")
                return False

            # Datuak memorian gorde
            data = list(reader)

        # Hizkuntza bakoitzeko fitxategia sortu
        languages = ['eu', 'es', 'en']
        success = True

        for lang in languages:
            if not sortu_hizkuntzako_fitxategia(data, base_name, lang, ['field', f'fieldname_{lang}'], output_dir):
                success = False

        return success

    except Exception as e:
        print(f"Errorea '{input_file}' fitxategia prozesatzean: {e}")
        return False

def main():
    # Scriptaren izena lortu
    script_name = os.path.basename(sys.argv[0])

    # Parametroen kopurua egiaztatu
    if len(sys.argv) != 2:
        print(f"Erabilera: python3 {script_name} <csv_direktorioa>")
        sys.exit(1)

    # Jatorrizko CSV direktorioa lortu
    csv_dir = sys.argv[1]

    # Direktorioa existitzen den egiaztatu
    if not os.path.isdir(csv_dir):
        print(f"Errorea: '{csv_dir}' direktorioa ez da existitzen.")
        sys.exit(1)

    # Irteerako direktorioa sortu (csv_split)
    output_dir = os.path.join(csv_dir, "csv_split")

    try:
        # Direktorioa sortu existitzen ez bada
        os.makedirs(output_dir, exist_ok=True)

        # g+w baimena eman (group write)
        current_permissions = stat.S_IMODE(os.lstat(output_dir).st_mode)
        os.chmod(output_dir, current_permissions | stat.S_IWGRP)

        print(f"Irteerako direktorioa sortu da: {output_dir}")

    except Exception as e:
        print(f"Errorea irteerako direktorioa sortzean: {e}")
        sys.exit(1)

    # Direktorioko fitxategi guztiak lortu
    try:
        files = os.listdir(csv_dir)
    except Exception as e:
        print(f"Errorea direktorioa irakurtzean: {e}")
        sys.exit(1)

    # CSV fitxategiak prozesatu
    csv_files = [f for f in files if f.lower().endswith('.csv')]

    if not csv_files:
        print(f"Abisua: '{csv_dir}' direktorioan ez dago CSV fitxategirik.")
        sys.exit(0)

    print(f"{len(csv_files)} CSV fitxategi prozesatuko dira...")

    success_count = 0
    for filename in csv_files:
        input_file = os.path.join(csv_dir, filename)
        print(f"\nProzesatzen: {input_file}")

        if process_csv_file(input_file, output_dir):
            success_count += 1

    print(f"\nProzesua amaitu da: {success_count}/{len(csv_files)} fitxategi ongi prozesatu dira.")

if __name__ == "__main__":
    main()
