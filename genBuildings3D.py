#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scripta: shapefile_update.py
Deskribapena: Bi fitxategi konbinatu eta eguneratzen ditu:
- Lehenengo Shapefile-tik GPKG-ko idut-ak ezabatu
- GPKG-ko poligonoak txertatu, atributu batzuk eguneratuta
"""

import os
import sys
import time
import geopandas as gpd
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def denbora_neurri(func):
    """Dekoratzailea: funtzioaren exekuzio-denbora neurtzeko"""
    def wrapper(*args, **kwargs):
        hasiera = time.time()
        emaitza = func(*args, **kwargs)
        bukaera = time.time()
        print(f"   ⏱️  {func.__name__}: {(bukaera - hasiera):.2f} segundo")
        return emaitza
    return wrapper

def main():
    # Fitxategien izenak
    shapefile_original = "/home5/SHP/Tiles/t_a_edifind.shp"  # Lehenengo Shapefile-a
    gpkg_fitxategia = "/home9/SHP/Test3D/t_a_edifind_3d_berezi.gpkg"    # GPKG fitxategia
    output_shapefile = "./dat/t_a_edifind_3d.shp"  # Irteerako Shapefile-a

    print("=" * 60)
    print("PROZESUA HASI DA")
    print("=" * 60)
    prozesu_hasiera = time.time()

    # 1. Fitxategiak kargatu
    print("\n1. FITXATEGIAK KARGATZEN...")
    hasiera = time.time()

    # Egiaztatu fitxategiak existitzen diren
    if not os.path.exists(shapefile_original):
        print(f"Errorea: {shapefile_original} ez da existitzen")
        sys.exit(1)

    if not os.path.exists(gpkg_fitxategia):
        print(f"Errorea: {gpkg_fitxategia} ez da existitzen")
        sys.exit(1)

    # Kargatu Shapefile-a
    try:
        gdf_shape = gpd.read_file(shapefile_original)
        print(f"   Shapefile-ak {len(gdf_shape):,} errenkada ditu")
    except Exception as e:
        print(f"Errorea Shapefile-a irakurtzean: {e}")
        sys.exit(1)

    # Kargatu GPKG-a
    try:
        gdf_gpkg = gpd.read_file(gpkg_fitxategia)
        print(f"   GPKG-ak {len(gdf_gpkg):,} errenkada ditu")
    except Exception as e:
        print(f"Errorea GPKG-a irakurtzean: {e}")
        sys.exit(1)

    bukaera = time.time()
    print(f"   ⏱️  Karga denbora: {(bukaera - hasiera):.2f} segundo")

    # 2. Eremuak identifikatu
    print("\n2. EREMUAK IDENTIFIKATZEN...")
    hasiera = time.time()

    # Egiaztatu 'idut' eremua existitzen den (bi kasuak kontuan hartuta: idut eta IDUT)
    idut_eremua_shape = None
    if 'idut' in gdf_shape.columns:
        idut_eremua_shape = 'idut'
    elif 'IDUT' in gdf_shape.columns:
        idut_eremua_shape = 'IDUT'
    else:
        print(f"Errorea: 'idut' edo 'IDUT' eremua ez da existitzen {shapefile_original} fitxategian")
        print(f"   Eremu eskuragarriak: {list(gdf_shape.columns)}")
        sys.exit(1)

    idut_eremua_gpkg = None
    if 'idut' in gdf_gpkg.columns:
        idut_eremua_gpkg = 'idut'
    elif 'IDUT' in gdf_gpkg.columns:
        idut_eremua_gpkg = 'IDUT'
    else:
        print(f"Errorea: 'idut' edo 'IDUT' eremua ez da existitzen {gpkg_fitxategia} fitxategian")
        print(f"   Eremu eskuragarriak: {list(gdf_gpkg.columns)}")
        sys.exit(1)

    print(f"   Shapefile-n '{idut_eremua_shape}' eremua erabiliko da")
    print(f"   GPKG-n '{idut_eremua_gpkg}' eremua erabiliko da")

    # Egiaztatu ALTURA_MED eta ALTURA_MAX eremuak existitzen diren Shapefile-n
    if 'ALTURA_MED' not in gdf_shape.columns:
        print(f"   Abisua: 'ALTURA_MED' eremua ez da existitzen Shapefile-n")

    if 'ALTURA_MAX' not in gdf_shape.columns:
        print(f"   Abisua: 'ALTURA_MAX' eremua ez da existitzen Shapefile-n")

    # Egiaztatu H_MEAN eta H_MAX eremuak existitzen diren GPKG-n
    if 'H_MEAN' not in gdf_gpkg.columns:
        print(f"   Abisua: 'H_MEAN' eremua ez da existitzen GPKG-n")

    if 'H_MAX' not in gdf_gpkg.columns:
        print(f"   Abisua: 'H_MAX' eremua ez da existitzen GPKG-n")

    bukaera = time.time()
    print(f"   ⏱️  Identifikazio denbora: {(bukaera - hasiera):.2f} segundo")

    # 3. GPKG-ko IDUT balioak zerrendatu
    print("\n3. GPKG-KO IDUT BALIOAK ZERRENDATZEN...")
    hasiera = time.time()

    gpkg_idut_balioak = gdf_gpkg[idut_eremua_gpkg].tolist()
    print(f"   GPKG-ko {len(gpkg_idut_balioak)} IDUT balio: {gpkg_idut_balioak}")

    bukaera = time.time()
    print(f"   ⏱️  Zerrendatze denbora: {(bukaera - hasiera):.2f} segundo")

    # 4. Shapefile-tik errenkadak ezabatu
    print("\n4. SHAPEFILE-TIK ERRENKADAK EZABATZEN...")
    hasiera = time.time()

    # Identifikatu ezabatu beharreko errenkadak
    ezabatu_beharrekoak = gdf_shape[gdf_shape[idut_eremua_shape].isin(gpkg_idut_balioak)]
    print(f"   {len(ezabatu_beharrekoak):,} errenkada ezabatuko dira Shapefile-tik")

    # GORDE EZABATUTAKO ERRENKADEN ATRIBUTUAK (ALTURA_MED eta ALTURA_MAX EZIK)
    # Horretarako, ALTURA_MED eta ALTURA_MAX eremuak kendu behar ditugu
    ezabatu_atributuak = ezabatu_beharrekoak.copy()

    # Kendu ALTURA_MED eta ALTURA_MAX ezabatutako datuetatik (gero GPKG-tik hartuko dira)
    if 'ALTURA_MED' in ezabatu_atributuak.columns:
        ezabatu_atributuak = ezabatu_atributuak.drop(columns=['ALTURA_MED'])
        print("   ALTURA_MED kendu da ezabatutako errenkaden atributuetatik")

    if 'ALTURA_MAX' in ezabatu_atributuak.columns:
        ezabatu_atributuak = ezabatu_atributuak.drop(columns=['ALTURA_MAX'])
        print("   ALTURA_MAX kendu da ezabatutako errenkaden atributuetatik")

    # Ezabatu errenkadak Shapefile-tik
    gdf_shape_berria = gdf_shape[~gdf_shape[idut_eremua_shape].isin(gpkg_idut_balioak)]
    print(f"   {len(gdf_shape_berria):,} errenkada geratzen dira Shapefile-n")

    bukaera = time.time()
    print(f"   ⏱️  Ezabaketa denbora: {(bukaera - hasiera):.2f} segundo")

    # 5. GPKG-ko poligonoak prestatu
    print("\n5. GPKG-KO POLIGONOAK PRESTATZEN...")
    hasiera = time.time()

    # GPKG-tik soilik eremu hauek mantenduko ditugu:
    # - idut/IDUT (identifikatzailea)
    # - geometry (geometria)
    # - H_MEAN eta H_MAX (ALTURA_MED eta ALTURA_MAX bihurtuko dira)
    eremuak_mantendu = [idut_eremua_gpkg, 'geometry']

    # Gehitu H_MEAN eta H_MAX existitzen badira
    if 'H_MEAN' in gdf_gpkg.columns:
        eremuak_mantendu.append('H_MEAN')
    if 'H_MAX' in gdf_gpkg.columns:
        eremuak_mantendu.append('H_MAX')

    # Soilik eremu horiek mantendu
    gdf_gpkg_prest = gdf_gpkg[eremuak_mantendu].copy()

    # Berrizendatu eremuak
    if 'H_MEAN' in gdf_gpkg_prest.columns:
        gdf_gpkg_prest = gdf_gpkg_prest.rename(columns={'H_MEAN': 'ALTURA_MED'})
        print("   H_MEAN → ALTURA_MED berrizendatu da")

    if 'H_MAX' in gdf_gpkg_prest.columns:
        gdf_gpkg_prest = gdf_gpkg_prest.rename(columns={'H_MAX': 'ALTURA_MAX'})
        print("   H_MAX → ALTURA_MAX berrizendatu da")

    # Ziurtatu IDUT eremuak izen bera duela Shapefile-koarekin
    if idut_eremua_gpkg != idut_eremua_shape:
        gdf_gpkg_prest = gdf_gpkg_prest.rename(columns={idut_eremua_gpkg: idut_eremua_shape})
        print(f"   '{idut_eremua_gpkg}' → '{idut_eremua_shape}' berrizendatu da")

    print(f"   GPKG-ko {len(gdf_gpkg_prest)} poligono prestatu dira txertatzeko")
    print(f"   GPKG-tik kopiatutako eremuak: {list(gdf_gpkg_prest.columns)}")

    bukaera = time.time()
    print(f"   ⏱️  Prestaketa denbora: {(bukaera - hasiera):.2f} segundo")

    # 6. Shapefile berria sortu
    print("\n6. SHAPEFILE BERRIA SORTZEN...")
    hasiera = time.time()

    # Egiaztatu bi GeoDataFrame-ek eremu berdinak dituztela
    # Shapefile-ko eremu guztiak mantendu (ezabatutako errenkadenak ezik)
    zutabeak_shape = list(gdf_shape_berria.columns)
    zutabeak_gpkg = list(gdf_gpkg_prest.columns)

    # Eremu guztien batura
    zutabe_guztiak = set(zutabeak_shape) | set(zutabeak_gpkg)
    if 'geometry' in zutabe_guztiak:
        zutabe_guztiak.remove('geometry')

    # Gehitu falta diren eremuak
    for zutabe in zutabe_guztiak:
        if zutabe not in gdf_shape_berria.columns:
            gdf_shape_berria[zutabe] = None
        if zutabe not in gdf_gpkg_prest.columns:
            gdf_gpkg_prest[zutabe] = None

    # Konbinatu
    gdf_konbinatua = pd.concat([gdf_shape_berria, gdf_gpkg_prest], ignore_index=True)
    gdf_konbinatua = gpd.GeoDataFrame(gdf_konbinatua, geometry='geometry', crs=gdf_shape.crs)

    print(f"   Shapefile berriak {len(gdf_konbinatua):,} errenkada ditu")

    bukaera = time.time()
    print(f"   ⏱️  Sorkuntza denbora: {(bukaera - hasiera):.2f} segundo")

    # 7. Shapefile berria gorde
    print("\n7. SHAPEFILE BERRIA GORDETZEN...")
    hasiera = time.time()

    # Ezabatu output fitxategia existitzen bada
    if os.path.exists(output_shapefile):
        try:
            os.remove(output_shapefile)
            print(f"   {output_shapefile} ezabatu da")
        except Exception as e:
            print(f"   Errorea {output_shapefile} ezabatzean: {e}")

    # Gorde Shapefile berria
    try:
        gdf_konbinatua.to_file(output_shapefile)
        print(f"   Shapefile berria gorde da: {output_shapefile}")
    except Exception as e:
        print(f"   Errorea Shapefile-a gordetzean: {e}")
        sys.exit(1)

    bukaera = time.time()
    print(f"   ⏱️  Gordetze denbora: {(bukaera - hasiera):.2f} segundo")

    # 8. Laburpena
    print("\n" + "=" * 60)
    print("PROZESUA AMAITU DA")
    print("=" * 60)

    prozesu_bukaera = time.time()
    denbora_totala = prozesu_bukaera - prozesu_hasiera

    print(f"\n📊 LABURPENA:")
    print(f"   Jatorrizko Shapefile: {len(gdf_shape):,} errenkada")
    print(f"   GPKG-ko poligonoak: {len(gdf_gpkg):,} errenkada")
    print(f"   Ezabatutako errenkadak: {len(ezabatu_beharrekoak):,}")
    print(f"   Txertatutako poligonoak: {len(gdf_gpkg_prest):,}")
    print(f"   Emaitzako Shapefile: {len(gdf_konbinatua):,} errenkada")

    # Erakutsi ezabatutako errenkaden informazioa
    if len(ezabatu_atributuak) > 0:
        print(f"\n   Ezabatutako errenkaden IDUT balioak (lehen 5):")
        for idx, row in ezabatu_atributuak.head(5).iterrows():
            idut_val = row.get(idut_eremua_shape, 'N/A')
            print(f"     IDUT: {idut_val}")

    print(f"\n⏱️  DENBORA TOTALA: {denbora_totala:.2f} segundo")
    print("=" * 60)

if __name__ == "__main__":
    main()
