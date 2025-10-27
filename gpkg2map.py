#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gpkg2map.py

Script honek direktorio bateko GeoPackage (GPKG) fitxategi guztiak aztertu eta
MapServer-en .map fitxategi bat sortzen du, WMS eta WFS zerbitzuekin bateragarria.

EGINKIZUNA:
------------
1. Direktorio bateko GPKG fitxategi guztiak detektatzea
2. GPKG bakoitzaren edukia aztertzea (taulak, geometria motak, metadatuak)
3. .map fitxategi bat sortzea MapServer-erako
4. WMS eta WFS zerbitzuak konfiguratzea

DATU-ITURRIAK:
--------------
- gpkg_contents: fitxategiaren metadatuak (izenburua, deskribapena)
- gpkg_data_columns: eremu-en izenak eta deskribapenak
- SQLite taulak: datu geometrikoen taulak

ERABILERA:
----------
python3 gpkg2map.py /path/to/gpkg/directory irteera.map

Egilea: [Zure izena]
Data: [Data]
"""

import os
import sys
import sqlite3
import argparse
import time
from datetime import datetime

def egiaztatu_parametroak():
    """Scriptaren parametroak egiaztatu eta prozesatzen ditu"""
    parser = argparse.ArgumentParser(
        description='GPKG fitxategietatik MapServer .map fitxategia sortu'
    )
    parser.add_argument('direktorioa', help='GPKG fitxategiak dauden direktorioa')
    parser.add_argument('irteera_map', help='Sortuko den .map fitxategiaren izena')

    return parser.parse_args()

def bilatu_gpkg_fitxategiak(direktorioa):
    """Direktorio bateko GPKG fitxategi guztiak bilatzen ditu"""
    gpkg_fitxategiak = []

    if not os.path.exists(direktorioa):
        print(f"ERROREA: '{direktorioa}' direktorioa ez da existitzen.")
        sys.exit(1)

    for fitxategia in os.listdir(direktorioa):
        if fitxategia.lower().endswith('.gpkg'):
            gpkg_fitxategiak.append(os.path.join(direktorioa, fitxategia))

    if not gpkg_fitxategiak:
        print("ERROREA: Ez da GPKG fitxategirik aurkitu direktorioan.")
        sys.exit(1)

    print(f"{len(gpkg_fitxategiak)} GPKG fitxategi aurkitu dira.")
    return gpkg_fitxategiak

def lortu_gpkg_metadatuak(gpkg_fitxategia, progresua_osoa, progresua_oraingoa, hasiera_denbora):
    """GPKG fitxategiaren metadatuak lortzen ditu"""
    metadatuak = {
        'fitxategia': os.path.basename(gpkg_fitxategia),
        'taulak': [],
        'izenburua': '',
        'deskribapena': ''
    }

    try:
        conn = sqlite3.connect(gpkg_fitxategia)
        cursor = conn.cursor()

        # gpkg_contents taulatik metadatuak lortu
        cursor.execute("""
            SELECT table_name, identifier, description, data_type, srs_id
            FROM gpkg_contents
        """)

        taulak = cursor.fetchall()
        taula_kopurua = len(taulak)

        for i, (taula, identifier, description, data_type, srs_id) in enumerate(taulak):
            # Progresua eguneratu
            progresu_ehunekoa = (progresua_oraingoa + (i / taula_kopurua)) / progresua_osoa * 100
            denbora_pasatua = time.time() - hasiera_denbora
            if progresu_ehunekoa > 0:
                estimatutako_denbora = (denbora_pasatua / progresu_ehunekoa) * 100
                denbora_geratzen = estimatutako_denbora - denbora_pasatua
                print(f"\rProgresua: {progresu_ehunekoa:.1f}% - Denbora geratzen: {denbora_geratzen:.1f}s", end="")

            metadatuak['izenburua'] = identifier or os.path.basename(gpkg_fitxategia)
            metadatuak['deskribapena'] = description or ''

            # Taularen informazio geometrikoa lortu
            cursor.execute(f"PRAGMA table_info({taula})")
            eremuak = [eremua[1] for eremua in cursor.fetchall()]

            # Geometria mota lortu
            geometria_mota = "GEOMETRY"
            cursor.execute(f"""
                SELECT geometry_type_name FROM gpkg_geometry_columns
                WHERE table_name = ?
            """, (taula,))

            geometria_emaitza = cursor.fetchone()
            if geometria_emaitza:
                geometria_mota = geometria_emaitza[0]

            metadatuak['taulak'].append({
                'izena': taula,
                'geometria_mota': geometria_mota,
                'eremuak': eremuak,
                'srs_id': srs_id
            })

        conn.close()

    except sqlite3.Error as e:
        print(f"ERROREA: Ezin izan da {gpkg_fitxategia} aztertu: {e}")

    return metadatuak

def sortu_map_fitxategia(gpkg_metadatuak, irteera_izena, hasiera_denbora):
    """MapServer .map fitxategia sortzen du"""

    # Existitzen bada, ezabatu
    if os.path.exists(irteera_izena):
        os.remove(irteera_izena)

    with open(irteera_izena, 'w', encoding='utf-8') as f:
        # Map fitxategiaren goiburua
        f.write(f"""MAP
    NAME "GPKG_Datuak"
    STATUS ON
    SIZE 800 600
    EXTENT -180 -90 180 90
    UNITS DD
    SHAPEPATH "../data"
    IMAGECOLOR 255 255 255
    FONTSET "../fonts/fonts.list"
    SYMBOLSET "../symbols/symbols.sym"

    # PROJECTION
    PROJECTION
        "init=epsg:4326"
    END

    # WEB METADATAK (WMS/WFS zerbitzuak)
    WEB
        METADATA
            "wms_title" "{gpkg_metadatuak[0]['izenburua'] if gpkg_metadatuak else 'GPKG Datuak'}"
            "wms_onlineresource" "http://localhost/cgi-bin/mapserv?"
            "wms_srs" "EPSG:4326 EPSG:3857"
            "wms_enable_request" "*"
            "wfs_title" "GPKG WFS Zerbitzua"
            "wfs_onlineresource" "http://localhost/cgi-bin/mapserv?"
            "wfs_srs" "EPSG:4326"
            "wfs_enable_request" "*"
            "wfs_encoding" "UTF-8"
            "ows_enable_request" "*"
        END
    END

""")

        # Layer bakoitza sortu
        layer_kopurua = sum(len(gpkg['taulak']) for gpkg in gpkg_metadatuak)
        layer_oraingoa = 0

        for gpkg in gpkg_metadatuak:
            for taula in gpkg['taulak']:
                layer_izena = f"{os.path.splitext(gpkg['fitxategia'])[0]}_{taula['izena']}"

                # Progresua eguneratu
                layer_oraingoa += 1
                progresu_ehunekoa = layer_oraingoa / layer_kopurua * 100
                denbora_pasatua = time.time() - hasiera_denbora
                print(f"\rMap fitxategia sortzen: {progresu_ehunekoa:.1f}% - Layer {layer_oraingoa}/{layer_kopurua}", end="")

                f.write(f"""
    # LAYER: {layer_izena}
    LAYER
        NAME "{layer_izena}"
        TYPE {geometria_mota_aldaketa(taula['geometria_mota'])}
        STATUS ON
        CONNECTIONTYPE OGR
        CONNECTION "{gpkg['fitxategia']}"
        DATA "{taula['izena']}"
        METADATA
            "wms_title" "{taula['izena']}"
            "wms_srs" "EPSG:4326 EPSG:3857"
            "gml_include_items" "all"
            "wfs_typename" "{taula['izena']}"
        END
        PROJECTION
            "init=epsg:{taula['srs_id'] or 4326}"
        END
""")

                # Klase sinple bat gehitu
                f.write(f"""
        CLASS
            NAME "{taula['izena']}"
            STYLE
                COLOR 200 100 100
                OUTLINECOLOR 0 0 0
            END
        END
    END
""")

        f.write("END\n")

    print(f"\nMap fitxategia sortu da: {irteera_izena}")

def geometria_mota_aldaketa(geometria_mota):
    """Geometria mota MapServer formatura aldatu"""
    mota_aldaketak = {
        'POINT': 'POINT',
        'LINESTRING': 'LINE',
        'POLYGON': 'POLYGON',
        'MULTIPOINT': 'POINT',
        'MULTILINESTRING': 'LINE',
        'MULTIPOLYGON': 'POLYGON'
    }
    return mota_aldaketak.get(geometria_mota.upper(), 'POLYGON')

def main():
    """Programa nagusia"""
    print("GPKG to MapServer Script-a abiarazten...")
    hasiera_denbora = time.time()

    # Parametroak lortu
    args = egiaztatu_parametroak()

    # GPKG fitxategiak bilatu
    print("1. GPKG fitxategiak bilatzen...")
    gpkg_fitxategiak = bilatu_gpkg_fitxategiak(args.direktorioa)

    # Metadatuak bildu
    print("2. GPKG fitxategiak aztertzen...")
    gpkg_metadatuak = []
    gpkg_kopurua = len(gpkg_fitxategiak)

    for i, gpkg in enumerate(gpkg_fitxategiak):
        print(f"\nAztertzen: {os.path.basename(gpkg)} ({i+1}/{gpkg_kopurua})")
        metadatuak = lortu_gpkg_metadatuak(gpkg, gpkg_kopurua, i, hasiera_denbora)
        if metadatuak['taulak']:
            gpkg_metadatuak.append(metadatuak)

    # Map fitxategia sortu
    print("\n3. Map fitxategia sortzen...")
    sortu_map_fitxategia(gpkg_metadatuak, args.irteera_map, hasiera_denbora)

    # Denbora totala kalkulatu
    denbora_totala = time.time() - hasiera_denbora
    print(f"\nProzesua amaitu da!")
    print(f"Denbora totala: {denbora_totala:.2f} segundo")
    print(f"Prozesatutako GPKG fitxategiak: {len(gpkg_metadatuak)}")
    print(f"Sortutako layer kopurua: {sum(len(gpkg['taulak']) for gpkg in gpkg_metadatuak)}")

if __name__ == "__main__":
    main()
