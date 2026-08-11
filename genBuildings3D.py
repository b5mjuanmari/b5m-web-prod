#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scripta: genBuildings3D.py
Deskribapena: Bi fitxategi konbinatu eta eguneratzen ditu:
- Lehenengo Shapefile-tik GPKG-ko idut-ak ezabatu
- GPKG-ko poligonoak txertatu, atributu batzuk eguneratuta
- Ezabatutako errenkaden atributuak (ALTURA_MED eta ALTURA_MAX ezik) GPKG-ko poligonoetan txertatu
"""

import os
import sys
import time
import datetime
import geopandas as gpd
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Aldagai globalak definitzen ditugu
HOME = "/home/lidar/SCRIPTS/WEB_PROD"
BASE_PATH = "/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles"
TEST_PATH = "/home9/SHP/Test3D"

# Log fitxategiaren konfigurazioa
SCRIPT_IZENA = os.path.splitext(os.path.basename(__file__))[0]
DATA_STR = datetime.datetime.now().strftime("%Y%m%d")
LOG_DIR = f"{HOME}/log"
LOG_FILE = f"{LOG_DIR}/{SCRIPT_IZENA}_{DATA_STR}.log"

class Logger:
    """Log fitxategira soilik idazteko klasea"""
    def __init__(self, log_file):
        self.log_file = log_file
        # Ziurtatu log direktorioa existitzen dela
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Ezabatu log fitxategia existitzen bada
        if os.path.exists(log_file):
            os.remove(log_file)

    def log(self, mezua):
        """Mezua log fitxategira idatzi (pantailara ez)"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(mezua + '\n')

    def log_bukaera(self):
        """Log bukaerako lerroa idatzi"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("=" * 60 + '\n')

def main():
    # Fitxategien izenak
    shapefile_original = f"{BASE_PATH}/t_a_edifind.shp"
    gpkg_fitxategia = f"{TEST_PATH}/t_a_edifind_3d_berezi.gpkg"
    output_shapefile = f"{BASE_PATH}/t_a_edifind_3d.shp"

    # Log sistema hasieratu
    logger = Logger(LOG_FILE)

    logger.log("=" * 60)
    logger.log(f"PROZESUA HASI DA - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log("=" * 60)
    prozesu_hasiera = time.time()

    # 1. Fitxategiak kargatu
    logger.log("\n1. FITXATEGIAK KARGATZEN...")
    hasiera = time.time()

    # Egiaztatu fitxategiak existitzen diren
    if not os.path.exists(shapefile_original):
        logger.log(f"Errorea: {shapefile_original} ez da existitzen")
        sys.exit(1)

    if not os.path.exists(gpkg_fitxategia):
        logger.log(f"Errorea: {gpkg_fitxategia} ez da existitzen")
        sys.exit(1)

    # Kargatu Shapefile-a
    try:
        gdf_shape = gpd.read_file(shapefile_original)
        logger.log(f"   Shapefile-ak {len(gdf_shape):,} errenkada ditu")
    except Exception as e:
        logger.log(f"Errorea Shapefile-a irakurtzean: {e}")
        sys.exit(1)

    # Kargatu GPKG-a
    try:
        gdf_gpkg = gpd.read_file(gpkg_fitxategia)
        logger.log(f"   GPKG-ak {len(gdf_gpkg):,} errenkada ditu")
    except Exception as e:
        logger.log(f"Errorea GPKG-a irakurtzean: {e}")
        sys.exit(1)

    bukaera = time.time()
    logger.log(f"   Karga denbora: {(bukaera - hasiera):.2f} segundo")

    # 2. Eremuak identifikatu
    logger.log("\n2. EREMUAK IDENTIFIKATZEN...")
    hasiera = time.time()

    # Egiaztatu 'idut' eremua existitzen den (bi kasuak kontuan hartuta: idut eta IDUT)
    idut_eremua_shape = None
    if 'idut' in gdf_shape.columns:
        idut_eremua_shape = 'idut'
    elif 'IDUT' in gdf_shape.columns:
        idut_eremua_shape = 'IDUT'
    else:
        logger.log(f"Errorea: 'idut' edo 'IDUT' eremua ez da existitzen {shapefile_original} fitxategian")
        logger.log(f"   Eremu eskuragarriak: {list(gdf_shape.columns)}")
        sys.exit(1)

    idut_eremua_gpkg = None
    if 'idut' in gdf_gpkg.columns:
        idut_eremua_gpkg = 'idut'
    elif 'IDUT' in gdf_gpkg.columns:
        idut_eremua_gpkg = 'IDUT'
    else:
        logger.log(f"Errorea: 'idut' edo 'IDUT' eremua ez da existitzen {gpkg_fitxategia} fitxategian")
        logger.log(f"   Eremu eskuragarriak: {list(gdf_gpkg.columns)}")
        sys.exit(1)

    logger.log(f"   Shapefile-n '{idut_eremua_shape}' eremua erabiliko da")
    logger.log(f"   GPKG-n '{idut_eremua_gpkg}' eremua erabiliko da")

    # Egiaztatu ALTURA_MED eta ALTURA_MAX eremuak existitzen diren Shapefile-n
    if 'ALTURA_MED' not in gdf_shape.columns:
        logger.log(f"   Abisua: 'ALTURA_MED' eremua ez da existitzen Shapefile-n")

    if 'ALTURA_MAX' not in gdf_shape.columns:
        logger.log(f"   Abisua: 'ALTURA_MAX' eremua ez da existitzen Shapefile-n")

    # Egiaztatu H_MEAN eta H_MAX eremuak existitzen diren GPKG-n
    if 'H_MEAN' not in gdf_gpkg.columns:
        logger.log(f"   Abisua: 'H_MEAN' eremua ez da existitzen GPKG-n")

    if 'H_MAX' not in gdf_gpkg.columns:
        logger.log(f"   Abisua: 'H_MAX' eremua ez da existitzen GPKG-n")

    bukaera = time.time()
    logger.log(f"   Identifikazio denbora: {(bukaera - hasiera):.2f} segundo")

    # 3. GPKG-ko IDUT balioak zerrendatu
    logger.log("\n3. GPKG-KO IDUT BALIOAK ZERRENDATZEN...")
    hasiera = time.time()

    gpkg_idut_balioak = gdf_gpkg[idut_eremua_gpkg].tolist()
    logger.log(f"   GPKG-ko {len(gpkg_idut_balioak)} IDUT balio: {gpkg_idut_balioak}")

    bukaera = time.time()
    logger.log(f"   Zerrendatze denbora: {(bukaera - hasiera):.2f} segundo")

    # 4. Shapefile-tik errenkadak ezabatu eta atributuak gorde
    logger.log("\n4. SHAPEFILE-TIK ERRENKADAK EZABATZEN ETA ATRIBUTUAK GORDETZEN...")
    hasiera = time.time()

    # Identifikatu ezabatu beharreko errenkadak
    ezabatu_beharrekoak = gdf_shape[gdf_shape[idut_eremua_shape].isin(gpkg_idut_balioak)]
    logger.log(f"   {len(ezabatu_beharrekoak):,} errenkada ezabatuko dira Shapefile-tik")

    # GORDE EZABATUTAKO ERRENKADEN ATRIBUTUAK (ALTURA_MED eta ALTURA_MAX EZIK)
    # Horretarako, ALTURA_MED eta ALTURA_MAX eremuak kendu behar ditugu
    ezabatu_atributuak = ezabatu_beharrekoak.copy()

    # Kendu ALTURA_MED eta ALTURA_MAX ezabatutako datuetatik (gero GPKG-tik hartuko dira)
    if 'ALTURA_MED' in ezabatu_atributuak.columns:
        ezabatu_atributuak = ezabatu_atributuak.drop(columns=['ALTURA_MED'])
        logger.log("   ALTURA_MED kendu da ezabatutako errenkaden atributuetatik")

    if 'ALTURA_MAX' in ezabatu_atributuak.columns:
        ezabatu_atributuak = ezabatu_atributuak.drop(columns=['ALTURA_MAX'])
        logger.log("   ALTURA_MAX kendu da ezabatutako errenkaden atributuetatik")

    # EZABATU errenkadak Shapefile-tik
    gdf_shape_berria = gdf_shape[~gdf_shape[idut_eremua_shape].isin(gpkg_idut_balioak)]
    logger.log(f"   {len(gdf_shape_berria):,} errenkada geratzen dira Shapefile-n")

    bukaera = time.time()
    logger.log(f"   Ezabaketa denbora: {(bukaera - hasiera):.2f} segundo")

    # 5. GPKG-ko poligonoak prestatu eta atributuak txertatu
    logger.log("\n5. GPKG-KO POLIGONOAK PRESTATZEN ETA ATRIBUTUAK TXERTATZEN...")
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
        logger.log("   H_MEAN -> ALTURA_MED berrizendatu da")

    if 'H_MAX' in gdf_gpkg_prest.columns:
        gdf_gpkg_prest = gdf_gpkg_prest.rename(columns={'H_MAX': 'ALTURA_MAX'})
        logger.log("   H_MAX -> ALTURA_MAX berrizendatu da")

    # Ziurtatu IDUT eremuak izen bera duela Shapefile-koarekin
    if idut_eremua_gpkg != idut_eremua_shape:
        gdf_gpkg_prest = gdf_gpkg_prest.rename(columns={idut_eremua_gpkg: idut_eremua_shape})
        logger.log(f"   '{idut_eremua_gpkg}' -> '{idut_eremua_shape}' berrizendatu da")

    # TXERTATU ezabatutako errenkaden atributuak GPKG-ko poligonoetan (IDUT-aren arabera)
    if len(ezabatu_atributuak) > 0:
        logger.log(f"\n   Ezabatutako {len(ezabatu_atributuak):,} errenkaden atributuak txertatzen...")

        # Egin merge-a IDUT-aren arabera
        # GPKG-ko poligonoetan ezabatutako atributuak txertatu
        gdf_gpkg_prest = gdf_gpkg_prest.merge(
            ezabatu_atributuak[[idut_eremua_shape] + [col for col in ezabatu_atributuak.columns if col != idut_eremua_shape and col != 'geometry']],
            on=idut_eremua_shape,
            how='left',
            suffixes=('', '_ezabatua')
        )

        # Eguneratu eremuak: lehenetsi GPKG-tik datozenak, ez badago, ezabatutakoak
        for col in ezabatu_atributuak.columns:
            if col != idut_eremua_shape and col != 'geometry' and col != 'ALTURA_MED' and col != 'ALTURA_MAX':
                if col in gdf_gpkg_prest.columns and f'{col}_ezabatua' in gdf_gpkg_prest.columns:
                    # GPKG-n badago eremua, mantendu; bestela ezabatutakoa hartu
                    gdf_gpkg_prest[col] = gdf_gpkg_prest[col].fillna(gdf_gpkg_prest[f'{col}_ezabatua'])
                    # Kendu aldi baterako zutabea
                    gdf_gpkg_prest = gdf_gpkg_prest.drop(columns=[f'{col}_ezabatua'])
                elif f'{col}_ezabatua' in gdf_gpkg_prest.columns:
                    # GPKG-n ez badago, zuzenean ezabatutakoa hartu
                    gdf_gpkg_prest[col] = gdf_gpkg_prest[f'{col}_ezabatua']
                    gdf_gpkg_prest = gdf_gpkg_prest.drop(columns=[f'{col}_ezabatua'])

        logger.log(f"   {len(gdf_gpkg_prest):,} poligono eguneratu dira ezabatutako atributuekin")
    else:
        logger.log("   Ez dago ezabatutako errenkadarik atributuak txertatzeko")

    logger.log(f"\n   GPKG-ko {len(gdf_gpkg_prest):,} poligono prestatu dira txertatzeko")
    logger.log(f"   GPKG-tik kopiatutako eremuak: {list(gdf_gpkg_prest.columns)}")

    bukaera = time.time()
    logger.log(f"   Prestaketa denbora: {(bukaera - hasiera):.2f} segundo")

    # 6. Shapefile berria sortu
    logger.log("\n6. SHAPEFILE BERRIA SORTZEN...")
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

    logger.log(f"   Shapefile berriak {len(gdf_konbinatua):,} errenkada ditu")

    bukaera = time.time()
    logger.log(f"   Sorkuntza denbora: {(bukaera - hasiera):.2f} segundo")

    # 7. Shapefile berria gorde
    logger.log("\n7. SHAPEFILE BERRIA GORDETZEN...")
    hasiera = time.time()

    # Ezabatu output fitxategia existitzen bada
    if os.path.exists(output_shapefile):
        try:
            os.remove(output_shapefile)
            logger.log(f"   {output_shapefile} ezabatu da")
        except Exception as e:
            logger.log(f"   Errorea {output_shapefile} ezabatzean: {e}")

    # Gorde Shapefile berria
    try:
        gdf_konbinatua.to_file(output_shapefile)
        logger.log(f"   Shapefile berria gorde da: {output_shapefile}")
    except Exception as e:
        logger.log(f"   Errorea Shapefile-a gordetzean: {e}")
        sys.exit(1)

    # Ezabatu .cpg fitxategia
    cpg_file = output_shapefile.replace('.shp', '.cpg')
    if os.path.exists(cpg_file):
        try:
            os.remove(cpg_file)
            logger.log(f"   {cpg_file} ezabatu da")
        except Exception as e:
            logger.log(f"   Errorea {cpg_file} ezabatzean: {e}")

    bukaera = time.time()
    logger.log(f"   Gordetze denbora: {(bukaera - hasiera):.2f} segundo")

    # 8. Laburpena
    logger.log("\n" + "=" * 60)
    logger.log("PROZESUA AMAITU DA")
    logger.log("=" * 60)

    prozesu_bukaera = time.time()
    denbora_totala = prozesu_bukaera - prozesu_hasiera

    logger.log(f"\nLABURPENA:")
    logger.log(f"   Jatorrizko Shapefile: {len(gdf_shape):,} errenkada")
    logger.log(f"   GPKG-ko poligonoak: {len(gdf_gpkg):,} errenkada")
    logger.log(f"   Ezabatutako errenkadak: {len(ezabatu_beharrekoak):,}")
    logger.log(f"   Txertatutako poligonoak: {len(gdf_gpkg_prest):,}")
    logger.log(f"   Emaitzako Shapefile: {len(gdf_konbinatua):,} errenkada")

    # Erakutsi ezabatutako errenkaden informazioa
    if len(ezabatu_atributuak) > 0:
        logger.log(f"\n   Ezabatutako errenkaden IDUT balioak (lehen 5):")
        for idx, row in ezabatu_atributuak.head(5).iterrows():
            idut_val = row.get(idut_eremua_shape, 'N/A')
            logger.log(f"     IDUT: {idut_val}")

        logger.log(f"\n   Txertatutako atributuak (ezabatutako errenkadenak):")
        for col in ezabatu_atributuak.columns:
            if col != idut_eremua_shape and col != 'geometry':
                logger.log(f"     - {col}")

    logger.log(f"\nDENBORA TOTALA: {denbora_totala:.2f} segundo")
    logger.log("=" * 60)
    logger.log_bukaera()

if __name__ == "__main__":
    main()
