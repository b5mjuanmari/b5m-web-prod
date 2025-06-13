#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import cx_Oracle
from osgeo import ogr
import time

def konexioa_egin():
    """Oracle datu-basearekin konexioa egiteko funtzioa"""
    # Aldatu konexio parametroak zure ingurunearen arabera
    konexioa = cx_Oracle.connect(
        user="b5mweb_nombres",
        password="web+",
        dsn="exploracle:1521/bdet"
    )
    return konexioa

def gpkg_sortu(gpkg_izena):
    """GPKG fitxategia sortu edo existitzen bada ezabatu"""
    if os.path.exists(gpkg_izena):
        os.remove(gpkg_izena)
        print(f"Oharra: {gpkg_izena} existitzen zen eta ezabatu da.")

    driver = ogr.GetDriverByName("GPKG")
    datuak = driver.CreateDataSource(gpkg_izena)
    datuak.Destroy()
    print(f"{gpkg_izena} fitxategia sortu da.")

def datuak_esportatu(gpkg_izena):
    """Datuak Oracle-tik esportatu eta GPKG fitxategian gorde"""
    hasiera_denbora = time.time()

    # 1. Konexioak sortu
    konexioa_hasiera = time.time()
    konexioa = konexioa_egin()
    cursor = konexioa.cursor()
    driver = ogr.GetDriverByName("GPKG")
    datuak = driver.Open(gpkg_izena, 1)
    konexioa_denbora = time.time() - konexioa_hasiera

    # Oinarrizko izena lortu
    oinarrizko_izena = os.path.splitext(os.path.basename(gpkg_izena))[0]

    # ==============================================
    # 1. Taula geografikoa sortu
    # ==============================================
    geom_taula_izena = f"{oinarrizko_izena}_geom"
    geom_hasiera = time.time()

    # SQL kontsulta, geometria WKT formatura bihurtzeko
    sql_geom = """
    SELECT
      a.idut as b5midut,
      b.puente_tunel as bridge_tunnel,
      b.idnombre b5midname,
      SDO_UTIL.TO_WKTGEOMETRY(a.polyline) as geom_wkt
    FROM
      b5mweb_25830.vialesind a
    JOIN
      b5mweb_nombres.v_vialtramo b on b.idut = a.idut
    WHERE
      b.nomtipo_e = 'errepidea'
    ORDER BY
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
        layer.CreateField(ogr.FieldDefn("b5midname", ogr.OFTString))

        # Datu geometrikoak gehitu
        for erregistroa in cursor:
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("b5midut", str(erregistroa[0]))
            feature.SetField("bridge_tunnel", str(erregistroa[1]))
            feature.SetField("b5midname", str(erregistroa[2]))

            if erregistroa[3] is not None:
                try:
                    geometria = ogr.CreateGeometryFromWkt(str(erregistroa[3]))
                    feature.SetGeometry(geometria)
                except Exception as e:
                    print(f"Errorea geometria prozesatzean: {str(e)}")

            layer.CreateFeature(feature)
            feature = None

        print(f"{geom_taula_izena} taula geografikoa sortu da.")

    except Exception as e:
        print(f"Errorea taula geografikoa sortzean: {str(e)}")
        raise

    geom_denbora = time.time() - geom_hasiera

    # ==============================================
    # 2. Taula alfanumerikoa sortu
    # ==============================================
    dat_taula_izena = f"{oinarrizko_izena}_dat"
    dat_hasiera = time.time()

    sql_dat = """
    SELECT DISTINCT
      a.url_2d as b5mcode,
      CASE WHEN a.nombre_e = a.nombre_c THEN a.nombre_e ELSE a.nombre_e || ' / ' || a.nombre_c END as name,
      a.nombre_e as name_eu,
      a.nombre_c as name_es,
      e.description_eu as type_eu,
      e.description_es as type_es,
      b.descripcion_e description_eu,
      b.descripcion_c description_es,
      b.observacion_e observation_eu,
      b.observacion_c observation_es,
      a.idnombre b5midname
    FROM
      b5mweb_nombres.solr_gen_toponimia_2d a
    JOIN
      b5mweb_nombres.v_vialtramo b ON b.idnombre = a.idnombre
    JOIN
      b5mweb_nombres.vv_color d ON TO_CHAR(d.codigo) = a.id_nombre1
    JOIN
      b5mweb_nombres.vv_color_desc e ON e.color = d.color
    WHERE
      a.id_nombre2 = '9000'
      AND b.nomtipo_e = 'errepidea'
    ORDER BY
      a.url_2d
    """

    try:
        cursor.execute(sql_dat)

        # Taula alfanumerikoa sortu
        layer = datuak.CreateLayer(
            dat_taula_izena,
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

        # Datu alfanumerikoak gehitu
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

        print(f"{dat_taula_izena} taula alfanumerikoa sortu da.")

    except Exception as e:
        print(f"Errorea taula alfanumerikoa sortzean: {str(e)}")
        raise

    dat_denbora = time.time() - dat_hasiera

    # ==============================================
    # 3. Bista sortu eta GPKG metadata eguneratu
    # ==============================================
    bista_hasiera = time.time()
    bista_izena = f"{oinarrizko_izena}_view"

    try:
        # Bista sortu
        sql_bista = f"""
        CREATE VIEW {bista_izena} AS
        SELECT
          g.b5midut,
          g.bridge_tunnel,
          g.b5midname,
          g.geom,
          d.b5mcode,
          d.name,
          d.name_eu,
          d.name_es,
          d.type_eu,
          d.type_es,
          d.description_eu,
          d.description_es,
          d.observation_eu,
          d.observation_es
        FROM
          {geom_taula_izena} g
        JOIN
          {dat_taula_izena} d ON g.b5midname = d.b5midname
        """
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
        ('{bista_izena}', 'geom', 'GEOMETRY', 25830, 0, 0)
        """
        datuak.ExecuteSQL(sql_geom_columns)

        print(f"{bista_izena} bista ondo sortu da eta metadata eguneratu da.")

    except Exception as e:
        print(f"Errorea bista sortzean edo metadata eguneratzean: {str(e)}")
        raise

    bista_denbora = time.time() - bista_hasiera

    # ==============================================
    # Denbora-estatistikak erakutsi
    # ==============================================
    guztira_denbora = time.time() - hasiera_denbora

    print("\nDenbora-estatistikak:")
    print(f"- Konexioak: {konexioa_denbora:.2f} segundu")
    print(f"- Taula geografikoa: {geom_denbora:.2f} segundu")
    print(f"- Taula alfanumerikoa: {dat_denbora:.2f} segundu")
    print(f"- Bista eta metadata: {bista_denbora:.2f} segundu")
    print(f"GUZTIRA: {guztira_denbora:.2f} segundu")

    # Itxi konexioak
    datuak = None
    cursor.close()
    konexioa.close()

def main():
    """Programa nagusia"""
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
        gpkg_sortu(args.gpkg_izena)
        datuak_esportatu(args.gpkg_izena)
        print("\nProzesua arrakastaz amaitu da.")
    except Exception as e:
        print(f"\nErrorea gertatu da: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
