#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gpkg2map.py

Script honek direktorio bateko GeoPackage (GPKG) fitxategi guztiak aztertu eta
MapServer-en .map fitxategi bat sortzen du, WMS eta WFS zerbitzuekin bateragarria.

EGINKIZUNA:
-----------
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

ADIBIDEA:
---------
python3 gpkg2map.py /home/data/datos_explotacion/CUR/datasets2 ./dat/gipuzkoa_map_wms3.map

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

def lortu_gpkg_metadatuak(gpkg_fitxategia):
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

        for taula, identifier, description, data_type, srs_id in taulak:
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

def sortu_map_fitxategia(gpkg_metadatuak, irteera_izena):
    """MapServer .map fitxategia sortzen du"""

    # Existitzen bada, ezabatu
    if os.path.exists(irteera_izena):
        os.remove(irteera_izena)

    with open(irteera_izena, 'w', encoding='utf-8') as f:
        # Map fitxategiaren goiburua
        f.write(f"""map
  config proj_lib /usr/local/share/proj
  name gipuzkoa_map_wms2
  status on
  size 600 600
  extent 530000 4740000 610000 4820000
  units meters
  shapepath "/home/data/datasets"
  imagecolor 255 255 255
  resolution 96
  maxsize 4096
  symbolset "wms.sim"
  projection
    "init=epsg:25830"
  end
  outputformat
      name png
      mimetype "image/png"
      driver "agg/png"
      extension "png"
      imagemode rgba
      transparent on
      formatoption "COMPRESSION=9"
      formatoption "QUANTIZE_FORCE=on"
      formatoption "QUANTIZE_COLORS=256"
  end
  web
    metadata
      "ows_enable_request" "*"
      "wms_enable_request" "*"
      "wms_title" "Gipuzkoa Web Map Service: Maps"
      "wms_abstract" "This is an OGC compliant Map Service served by the Provincial Council of Gipuzkoa. The engine used to server this Map Service is MapServer"
      "wms_keywordlist" "Gipuzkoa WMS Maps"
      "wms_onlineresource" "https://b5mdev/ogc/wms/gipuzkoa_map_wms2?"
      "wms_contactperson" ""
      "wms_contactorganization" "Provincial Council of Gipuzkoa/Gipuzkoako Foru Aldundia/Diputación Foral de Gipuzkoa"
      "wms_addresstype" "postal address"
      "wms_address" "Julio Caro Baroja 2-3º"
      "wms_city" "Donostia / San Sebastián"
      "wms_stateorprovince" "Gipuzkoa"
      "wms_postcode" "20018"
      "wms_country" "Spain"
      "wms_contactvoicetelephone" ""
      "wms_contactfacsimiletelephone" ""
      "wms_contactelectronicmailaddress" "liz@gipuzkoa.eus"
      "wms_fees" "none"
      "wms_accessconstraints" "https://b5mdev/web5000/en/legal-information"
      "wms_attribution_title" "Provincial Council of Gipuzkoa/Gipuzkoako Foru Aldundia/Diputacion Foral de Gipuzkoa"
      "wms_srs" "EPSG:25830 EPSG:23030 EPSG:4326 EPSG:32630 EPSG:4230 EPSG:900913 EPSG:3857 EPSG:3042"
      "wms_feature_info_mime_type" "text/html"
      "wfs_title" "Gipuzkoa Web Map Service: Maps"
      "wfs_onlineresource" "https://b5mdev/ogc/wms/gipuzkoa_map_wms2?"
      "wfs_srs" "EPSG:25830 EPSG:23030 EPSG:4326 EPSG:32630 EPSG:4230 EPSG:900913 EPSG:3857 EPSG:3042"
      "wfs_enable_request" "*"
      "wfs_encoding" "UTF-8"
    end
    header "info/gipuzkoa_map_wms_bur.html"
    footer "info/gipuzkoa_map_wms_oin.html"
    empty "info/gipuzkoa_map_wms_huts.html"
    temppath "/tmp/"
    imagepath "/tmp/"
    imageurl "/tmp/"
  end
""")

        # Layer bakoitza sortu
        layer_kopurua = sum(len(gpkg['taulak']) for gpkg in gpkg_metadatuak)
        layer_oraingoa = 0

        for gpkg in gpkg_metadatuak:
            for taula in gpkg['taulak']:
                layer_oraingoa += 1
                layer_izena = f"{os.path.splitext(gpkg['fitxategia'])[0]}_{taula['izena']}"

                print(f"\rLayer-ak sortzen: {layer_oraingoa}/{layer_kopurua}", end="")

                f.write(f"""
  # layer: {layer_izena}
  layer
    name "{layer_izena}"
    type {geometria_mota_aldaketa(taula['geometria_mota'])}
    status on
    connectiontype ogr
    connection "{gpkg['fitxategia']}"
    data "{taula['izena']}"
    metadata
      "wms_title" "{taula['izena']}"
      "wms_srs" "EPSG:4326 EPSG:3857"
      "gml_include_items" "all"
      "wfs_typename" "{taula['izena']}"
    end
    projection
      "init=epsg:{taula['srs_id'] or 4326}"
    end
""")

                # Klase sinple bat gehitu
                f.write(f"""
    class
      name "{taula['izena']}"
      style
        color 200 100 100
        outlinecolor 0 0 0
      end
    end
  end
""")

        f.write("end\n")

    print(f"\nMap fitxategia sortu da: {irteera_izena}")

def geometria_mota_aldaketa(geometria_mota):
    """Geometria mota MapServer formatura aldatu"""
    mota_aldaketak = {
        'POINT': 'point',
        'LINESTRING': 'line',
        'POLYGON': 'polygon',
        'MULTIPOINT': 'point',
        'MULTILINESTRING': 'line',
        'MULTIPOLYGON': 'polygon'
    }
    return mota_aldaketak.get(geometria_mota.upper(), 'polygon')

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
    print("\n2. GPKG fitxategiak aztertzen...")
    gpkg_metadatuak = []
    gpkg_kopurua = len(gpkg_fitxategiak)

    for i, gpkg in enumerate(gpkg_fitxategiak):
        prg_ehun = ((i + 1) / gpkg_kopurua) * 100
        print(f"[{i+1}/{gpkg_kopurua}] {os.path.basename(gpkg)} - %{prg_ehun:.0f}")
        metadatuak = lortu_gpkg_metadatuak(gpkg)
        if metadatuak['taulak']:
            gpkg_metadatuak.append(metadatuak)

    # Map fitxategia sortu
    print("\n3. Map fitxategia sortzen...")
    sortu_map_fitxategia(gpkg_metadatuak, args.irteera_map)

    # Denbora totala kalkulatu
    denbora_totala = time.time() - hasiera_denbora
    print(f"\nProzesatutako GPKG fitxategiak: {len(gpkg_metadatuak)}")
    print(f"Sortutako layer kopurua: {sum(len(gpkg['taulak']) for gpkg in gpkg_metadatuak)}")
    print(f"Denbora: {denbora_totala:.2f} segundo")

if __name__ == "__main__":
    main()
