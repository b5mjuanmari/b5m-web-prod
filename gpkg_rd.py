#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import cx_Oracle
from osgeo import ogr
import time
from datetime import datetime

def ora_data():
    """Uneko data eta ordua itzultzen du formatu egokian"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def konexioa_egin():
    """Oracle datu-basearekin konexioa egiteko funtzioa"""
    print(f"[{ora_data()}] Oracle-ra konektatzen...")
    hasiera = time.time()

    # Aldatu konexio parametroak zure ingurunearen arabera
    konexioa = cx_Oracle.connect(
        user="b5mweb_nombres",
        password="web+",
        dsn="exploracle:1521/bdet"
    )

    denbora = time.time() - hasiera
    print(f"[{ora_data()}] Konexioa eginda ({denbora:.2f} segundo)")
    return konexioa

def gpkg_sortu(gpkg_izena):
    """GPKG fitxategia sortu edo existitzen bada ezabatu"""
    print(f"[{ora_data()}] GPKG fitxategia prestatzen...")
    hasiera = time.time()

    if os.path.exists(gpkg_izena):
        os.remove(gpkg_izena)
        print(f"[{ora_data()}] Oharra: {gpkg_izena} existitzen zen eta ezabatu da.")

    driver = ogr.GetDriverByName("GPKG")
    datuak = driver.CreateDataSource(gpkg_izena)
    datuak.Destroy()

    denbora = time.time() - hasiera
    print(f"[{ora_data()}] {gpkg_izena} fitxategia sortu da ({denbora:.2f} segundo)")

def datuak_esportatu(gpkg_izena):
    """Datuak Oracle-tik esportatu eta GPKG fitxategian gorde"""
    print(f"\n[{ora_data()}] Datuak esportatzen hasi...")
    prozesu_hasiera = time.time()

    # 1. Konexioak sortu
    konexioa = konexioa_egin()
    cursor = konexioa.cursor()
    driver = ogr.GetDriverByName("GPKG")
    datuak = driver.Open(gpkg_izena, 1)

    # Oinarrizko izena lortu
    oinarrizko_izena = os.path.splitext(os.path.basename(gpkg_izena))[0]

    # ==============================================
    # 1. Taula geografikoa sortu
    # ==============================================
    geom_taula_izena = f"{oinarrizko_izena}_geom"
    print(f"\n[{ora_data()}] {geom_taula_izena} taula geografikoa sortzen...")
    geom_hasiera = time.time()

    # SQL kontsulta, geometria WKT formatura bihurtzeko
    sql_geom = """
    select
      a.idut as b5midut,
      b.bridge_tunnel,
      sdo_util.to_wktgeometry(a.polyline) as geom_wkt
    from
      b5mweb_25830.vialesind a
    join
      (
        select idut,
        max(puente_tunel) as bridge_tunnel
        from b5mweb_nombres.v_vialtramo
        where nomtipo_e = 'errepidea'
        group by idut
      ) b on b.idut = a.idut
    order by
      a.idut
    """

    try:
        cursor.execute(sql_geom)

        # Taula geografikoa sortu
        srs = ogr.osr.SpatialReference()
        srs.ImportFromEPSG(25830)

        layer = datuak.CreateLayer(
            geom_taula_izena,
            srs,
            ogr.wkbLineString,
            ["OVERWRITE=YES"]
        )

        # Eremuak gehitu
        layer.CreateField(ogr.FieldDefn("b5midut", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("bridge_tunnel", ogr.OFTString))

        # Datu geometrikoak gehitu
        kont = 0
        for erregistroa in cursor:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("b5midut", str(erregistroa[0]))
            feature.SetField("bridge_tunnel", str(erregistroa[1]))

            if erregistroa[2] is not None:
                try:
                    geometria = ogr.CreateGeometryFromWkt(str(erregistroa[2]))
                    feature.SetGeometry(geometria)
                except Exception as e:
                    print(f"[{ora_data()}] Oharra: geometria ezin izan da gehitu - {str(e)}")

            layer.CreateFeature(feature)
            feature = None
            kont += 1

            # Progresua erakutsi 1000 erregistroko
            if kont % 1000 == 0:
                print(f"[{ora_data()}] {kont} erregistro prozesatu dira...")

        denbora_geom = time.time() - geom_hasiera
        print(f"[{ora_data()}] {geom_taula_izena} taula geografikoa sortu da ({kont} erregistro, {denbora_geom:.2f} segundo)")

    except Exception as e:
        print(f"[{ora_data()}] ERROREA: {geom_taula_izena} taula sortzean - {str(e)}")
        raise

    # ==============================================
    # 2. Atributuen taula alfanumerikoa sortu
    # ==============================================
    att_taula_izena = f"{oinarrizko_izena}_att"
    print(f"\n[{ora_data()}] {att_taula_izena} taula alfanumerikoa sortzen...")
    att_hasiera = time.time()

    sql_att = """
    select distinct
      a.url_2d as b5mcode,
      case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
      a.nombre_e as name_eu,
      a.nombre_c as name_es,
      e.description_eu as type_eu,
      e.description_es as type_es,
      b.descripcion_e description_eu,
      b.descripcion_c description_es,
      b.observacion_e observation_eu,
      b.observacion_c observation_es,
      a.idnombre b5midname
    from
      b5mweb_nombres.solr_gen_toponimia_2d a
    join
      b5mweb_nombres.v_vialtramo b on b.idnombre = a.idnombre
    join
      b5mweb_nombres.vv_color d on to_char(d.codigo) = a.id_nombre1
    join
      b5mweb_nombres.vv_color_desc e on e.color = d.color
    where
      a.id_nombre2 = '9000'
      and b.nomtipo_e = 'errepidea'
    order by
      a.url_2d
    """

    try:
        cursor.execute(sql_att)

        # Atributuen taula alfanumerikoa sortu
        layer = datuak.CreateLayer(
            att_taula_izena,
            None,
            ogr.wkbNone,
            ["OVERWRITE=YES"]
        )

        # Eremuak gehitu
        layer.CreateField(ogr.FieldDefn("b5mcode", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("name", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("name_eu", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("name_es", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("type_eu", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("type_es", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("description_eu", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("description_es", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("observation_eu", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("observation_es", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("b5midname", ogr.OFTString))

        # Atributuen datu alfanumerikoak gehitu
        kont = 0
        for erregistroa in cursor:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("b5mcode", str(erregistroa[0]))
            feature.SetField("name", str(erregistroa[1]))
            feature.SetField("name_eu", str(erregistroa[2]))
            feature.SetField("name_es", str(erregistroa[3]))
            feature.SetField("type_eu", str(erregistroa[4]))
            feature.SetField("type_es", str(erregistroa[5]))
            feature.SetField("description_eu", str(erregistroa[6]))
            feature.SetField("description_es", str(erregistroa[7]))
            feature.SetField("observation_eu", str(erregistroa[8]))
            feature.SetField("observation_es", str(erregistroa[9]))
            feature.SetField("b5midname", str(erregistroa[10]))

            layer.CreateFeature(feature)
            feature = None
            kont += 1

            # Progresua erakutsi 1000 erregistroko
            if kont % 1000 == 0:
                print(f"[{ora_data()}] {kont} erregistro prozesatu dira...")

        denbora_att = time.time() - att_hasiera
        print(f"[{ora_data()}] {att_taula_izena} taula alfanumerikoa sortu da ({kont} erregistro, {denbora_att:.2f} segundo)")

    except Exception as e:
        print(f"[{ora_data()}] ERROREA: {att_taula_izena} taula sortzean - {str(e)}")
        raise

    # ==============================================
    # 3. Erlazioen taula alfanumerikoak sortu
    # ==============================================
    rel_taula_izena = f"{oinarrizko_izena}_rel"
    print(f"\n[{ora_data()}] {rel_taula_izena} taula alfanumerikoa sortzen...")
    rel_hasiera = time.time()

    sql_rel = """
    select
      a.idut as b5midut,
      b.idnombre b5midname
    from
      b5mweb_25830.vialesind a
    join
      b5mweb_nombres.v_vialtramo b on b.idut = a.idut
    where
      b.nomtipo_e = 'errepidea'
    order by
      a.idut
    """

    try:
        cursor.execute(sql_rel)

        # Atributuen taula alfanumerikoa sortu
        layer = datuak.CreateLayer(
            rel_taula_izena,
            None,
            ogr.wkbNone,
            ["OVERWRITE=YES"]
        )

        # Eremuak gehitu
        layer.CreateField(ogr.FieldDefn("b5midut", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("b5midname", ogr.OFTString))

        # Atributuen datu alfanumerikoak gehitu
        kont = 0
        for erregistroa in cursor:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("b5midut", str(erregistroa[0]))
            feature.SetField("b5midname", str(erregistroa[1]))

            layer.CreateFeature(feature)
            feature = None
            kont += 1

            # Progresua erakutsi 1000 erregistroko
            if kont % 1000 == 0:
                print(f"[{ora_data()}] {kont} erregistro prozesatu dira...")

        denbora_rel = time.time() - rel_hasiera
        print(f"[{ora_data()}] {rel_taula_izena} taula alfanumerikoa sortu da ({kont} erregistro, {denbora_rel:.2f} segundo)")

    except Exception as e:
        print(f"[{ora_data()}] ERROREA: {rel_taula_izena} taula sortzean - {str(e)}")
        raise

    # ==============================================
    # 4. Bista sortu eta GPKG metadata eguneratu
    # ==============================================
    bista_izena = f"{oinarrizko_izena}_view"
    print(f"\n[{ora_data()}] {bista_izena} bista eta metadata prestatzen...")
    bista_hasiera = time.time()

    try:
        # Bista sortu
        sql_bista = f"""
        CREATE VIEW {bista_izena} AS
        SELECT
          a.b5mcode,
          a.name,
          a.name_eu,
          a.name_es,
          a.type_eu,
          a.type_es,
          g.bridge_tunnel,
          a.description_eu,
          a.description_es,
          a.observation_eu,
          a.observation_es,
          g.b5midut,
          r.b5midname,
          g.geom
        FROM
          {rel_taula_izena} r
        JOIN
          {geom_taula_izena} g ON r.b5midut = g.b5midut
        JOIN
          {att_taula_izena} a ON r.b5midname = a.b5midname
        """

        # Bista sortu
        datuak.ExecuteSQL(sql_bista)

        # GPKG metadata taulak eguneratu
        # gpkg_contents eguneratu
        sql_contents = f"""
        INSERT INTO gpkg_contents
        (table_name, identifier, data_type, srs_id)
        VALUES
        ('{bista_izena}', '{bista_izena}', 'features', 25830)
        """
        datuak.ExecuteSQL(sql_contents)

        # gpkg_geometry_columns eguneratu
        sql_geom_columns = f"""
        INSERT INTO gpkg_geometry_columns
        (table_name, column_name, geometry_type_name, srs_id, z, m)
        VALUES
        ('{bista_izena}', 'geom', 'LINESTRING', 25830, 0, 0)
        """
        datuak.ExecuteSQL(sql_geom_columns)

        denbora_view = time.time() - bista_hasiera
        print(f"[{ora_data()}] {bista_izena} bista ondo sortu da eta metadata eguneratu da ({denbora_view:.2f} segundo)")

    except Exception as e:
        print(f"[{ora_data()}] ERROREA: bista sortzean edo metadata eguneratzean - {str(e)}")
        raise

    # ==============================================
    # Denbora-estatistikak erakutsi
    # ==============================================
    guztira_denbora = time.time() - prozesu_hasiera

    print(f"\n[{ora_data()}] PROZESU OROKORRA AMAITU DA")
    print("====================================")
    print("Denbora-estatistikak:")
    print(f"- Taula geografikoa: {denbora_geom:.2f} segundo")
    print(f"- Atributuen taula alfanumerikoa: {denbora_att:.2f} segundo")
    print(f"- Erlazioen taula alfanumerikoa: {denbora_rel:.2f} segundo")
    print(f"- Bista eta metadata: {denbora_view:.2f} segundo")
    print(f"GUZTIRA: {guztira_denbora:.2f} segundo")
    print("====================================\n")

    # Itxi konexioak
    datuak = None
    cursor.close()
    konexioa.close()

def main():
    """Programa nagusia"""
    print(f"[{ora_data()}] Script-a hasi da")
    script_hasiera = time.time()

    parser = argparse.ArgumentParser(
        description='Oracle 11g-tik datuak esportatzeko eta GPKG fitxategia sortzeko scripta.',
        prog=sys.argv[0]
    )
    parser.add_argument(
        'gpkg_izena',
        type=str,
        help='Sortu nahi den GPKG fitxategiaren izena eta kokapena'
    )

    args = parser.parse_args()

    try:
        print(f"[{ora_data()}] {args.gpkg_izena} fitxategia sortzeko prozesua hasi da")
        gpkg_sortu(args.gpkg_izena)
        datuak_esportatu(args.gpkg_izena)

        denbora = time.time() - script_hasiera
        print(f"\n[{ora_data()}] Prozesua arrakastaz amaitu da. Guztira {denbora:.2f} segund0.")
    except Exception as e:
        denbora = time.time() - script_hasiera
        print(f"\n[{ora_data()}] ERROREA: Prozesua eten da {denbora:.2f} segundotan")
        print(f"Errore-mezua: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
