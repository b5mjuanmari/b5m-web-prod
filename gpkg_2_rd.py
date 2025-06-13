#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPKG fitxategi sortzailea Oracle datubasetik

Script honek Oracle datubasetik bi kontsulta exekutatzen ditu eta
GPKG fitxategi bat sortzen du bi taula eta bista batekin.

Erabilera: python3 script_izena.py gpkg_fitxategi_bidea
"""

import sys
import os
import sqlite3
import cx_Oracle
from pathlib import Path

def main():
    """Programa nagusia"""

    # Parametroen egiaztapena
    if len(sys.argv) != 2:
        print(f"Erabilera: python3 {sys.argv[0]} <gpkg_fitxategi_bidea>")
        print("Adibidea: python3 gpkg_creator.py /bidea/nire_fitxategia.gpkg")
        sys.exit(1)

    gpkg_path = sys.argv[1]

    # GPKG fitxategiaren izena eta kokapena
    gpkg_file = Path(gpkg_path)
    base_name = gpkg_file.stem  # Fitxategiaren izena luzapenik gabe

    # Taula eta bista izenak
    geom_table = f"{base_name}_geom"
    data_table = f"{base_name}_dat"
    view_name = f"{base_name}_view"

    try:
        # Direktorioa sortu ez bada existitzen
        gpkg_dir = gpkg_file.parent
        if not gpkg_dir.exists():
            print(f"Direktorioa sortzen: {gpkg_dir}")
            gpkg_dir.mkdir(parents=True, exist_ok=True)

        # Direktorioa eta baimenak egiaztatu
        print(f"Egiaztapen informazioa:")
        print(f"  - GPKG bidea: {gpkg_path}")
        print(f"  - Direktorioa existitzen da: {gpkg_dir.exists()}")
        print(f"  - Direktorioa idazteko baimena: {os.access(gpkg_dir, os.W_OK)}")
        print(f"  - Fitxategi absolutu bidea: {gpkg_file.absolute()}")

        # Idazteko baimenik ez badago, beste direktorio bat proposatu
        if not os.access(gpkg_dir, os.W_OK):
            print(f"⚠️  Ez duzu idazteko baimenik '{gpkg_dir}' direktorioan")

            # Alternatibo direktorio bat sortu
            alt_path = Path.home() / gpkg_file.name
            print(f"💡 Direktorio alternatibo hau erabiliko da: {alt_path}")

            gpkg_path = str(alt_path)
            gpkg_file = alt_path

            # Izenak berriz kalkulatu
            base_name = gpkg_file.stem
            geom_table = f"{base_name}_geom"
            data_table = f"{base_name}_dat"
            view_name = f"{base_name}_view"

        # Existitzen bada, GPKG fitxategia ezabatu
        if gpkg_file.exists():
            print(f"Existitzen den GPKG fitxategia ezabatzen: {gpkg_path}")
            os.remove(gpkg_path)

        # Oracle konexioa sortu
        print("Oracle datubasera konektatzen...")
        oracle_conn = get_oracle_connection()

        # SQLite/GPKG konexioa sortu - errore informazio gehiagorekin
        print(f"GPKG fitxategia sortzen: {gpkg_path}")
        try:
            gpkg_conn = sqlite3.connect(gpkg_path)
            print("✓ GPKG konexioa arrakastaz sortua")
        except Exception as sqlite_error:
            print(f"❌ SQLite konexio errorea: {sqlite_error}")
            print(f"   Errore mota: {type(sqlite_error).__name__}")
            raise

        # GPKG egitura sortu
        setup_gpkg(gpkg_conn)

        # Oracle-tik datuak lortu eta GPKG-ra gehitu
        print("Datu geografikoak lortzen eta gehitzen...")
        create_geom_table(oracle_conn, gpkg_conn, geom_table)

        print("Datu alfanumerikoak lortzen eta gehitzen...")
        create_data_table(oracle_conn, gpkg_conn, data_table)

        # Bista sortu
        print("Bista sortzen...")
        create_view(gpkg_conn, view_name, geom_table, data_table)

        # Konexioak itxi
        oracle_conn.close()
        gpkg_conn.close()

        print(f"✓ GPKG fitxategia arrakastaz sortua: {gpkg_path}")
        print(f"  - Taula geografikoa: {geom_table}")
        print(f"  - Taula alfanumerikoa: {data_table}")
        print(f"  - Bista: {view_name}")

    except Exception as e:
        print(f"❌ Errorea: {e}")
        sys.exit(1)

def get_oracle_connection():
    """Oracle datubasera konexioa sortu"""
    # Hemen zure Oracle konexio parametroak konfiguratu behar dituzu
    # Adibidea:
    # return cx_Oracle.connect("erabiltzailea/pasahitza@localhost:1521/xe")

    # Ingurune aldagaietatik irakurri
    user = os.getenv('ORACLE_USER', 'b5mweb_nombres')
    password = os.getenv('ORACLE_PASSWORD', 'web+')
    dsn = os.getenv('ORACLE_DSN', 'exploracle:1521/bdet')

    return cx_Oracle.connect(f"{user}/{password}@{dsn}")

def setup_gpkg(conn):
    """GPKG fitxategiaren oinarrizko egitura sortu"""
    cursor = conn.cursor()

    # Spatial metadata taulak sortu
    cursor.execute("""
        CREATE TABLE gpkg_spatial_ref_sys (
            srs_name TEXT NOT NULL,
            srs_id INTEGER NOT NULL PRIMARY KEY,
            organization TEXT NOT NULL,
            organization_coordsys_id INTEGER NOT NULL,
            definition TEXT NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE gpkg_contents (
            table_name TEXT NOT NULL PRIMARY KEY,
            data_type TEXT NOT NULL,
            identifier TEXT UNIQUE,
            description TEXT DEFAULT '',
            last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
            min_x REAL,
            min_y REAL,
            max_x REAL,
            max_y REAL,
            srs_id INTEGER,
            CONSTRAINT fk_gc_r_srs_id FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE gpkg_geometry_columns (
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            geometry_type_name TEXT NOT NULL,
            srs_id INTEGER NOT NULL,
            z TINYINT NOT NULL,
            m TINYINT NOT NULL,
            CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
            CONSTRAINT uk_gc_table_name UNIQUE (table_name),
            CONSTRAINT fk_gc_tn FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name),
            CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
        )
    """)

    # EPSG:25830 sistema geografikoa gehitu (ETRS89 / UTM zone 30N)
    cursor.execute("""
        INSERT INTO gpkg_spatial_ref_sys VALUES
        ('ETRS89 / UTM zone 30N', 25830, 'EPSG', 25830,
         'PROJCS["ETRS89 / UTM zone 30N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","25830"]]',
         'ETRS89 / UTM zone 30N')
    """)

    conn.commit()

def create_geom_table(oracle_conn, gpkg_conn, table_name):
    """Datu geografikoen taula sortu"""

    # Oracle kontsulta - geometria WKT formatuan lortu
    sql_geom = """
    select
      a.idut as b5midut,
      b.puente_tunel as bridge_tunnel,
      b.idnombre as b5midname,
      sdo_util.to_wktgeometry(a.polyline) as geom
    from
      b5mweb_25830.vialesind a
    join
      b5mweb_nombres.v_vialtramo b on b.idut = a.idut
    where
      b.nomtipo_e = 'errepidea'
    order by
      a.idut
    """

    oracle_cursor = oracle_conn.cursor()
    oracle_cursor.execute(sql_geom)

    # GPKG taula sortu
    gpkg_cursor = gpkg_conn.cursor()
    gpkg_cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            b5midut INTEGER,
            bridge_tunnel TEXT,
            b5midname INTEGER,
            geom GEOMETRY
        )
    """)

    # Datuak gehitu
    row_count = 0
    for row in oracle_cursor:
        b5midut, bridge_tunnel, b5midname, geom_wkt = row

        # WKT geometria zuzenean erabili
        if geom_wkt and hasattr(geom_wkt, 'read'):
            # CLOB bada
            geom_wkt = geom_wkt.read()

        gpkg_cursor.execute(f"""
            INSERT INTO {table_name} (b5midut, bridge_tunnel, b5midname, geom)
            VALUES (?, ?, ?, ?)
        """, (b5midut, bridge_tunnel, b5midname, geom_wkt))

        row_count += 1

    # Metadata gehitu
    gpkg_cursor.execute("""
        INSERT INTO gpkg_contents VALUES (?, 'features', ?, 'Errepide geometriak', datetime('now'), NULL, NULL, NULL, NULL, 25830)
    """, (table_name, table_name))

    gpkg_cursor.execute("""
        INSERT INTO gpkg_geometry_columns VALUES (?, 'geom', 'GEOMETRY', 25830, 0, 0)
    """, (table_name,))

    gpkg_conn.commit()
    oracle_cursor.close()

    print(f"  ✓ {row_count} erregistro geografiko gehituta")

def create_data_table(oracle_conn, gpkg_conn, table_name):
    """Datu alfanumerikoen taula sortu"""

    # Oracle kontsulta
    sql_data = """
    select distinct
      a.url_2d as b5mcode,
      case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
      a.nombre_e as name_eu,
      a.nombre_c as name_es,
      e.description_eu as type_eu,
      e.description_es as type_es,
      b.descripcion_e as description_eu,
      b.descripcion_c as description_es,
      b.observacion_e as observation_eu,
      b.observacion_c as observation_es,
      a.idnombre as b5midname
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

    oracle_cursor = oracle_conn.cursor()
    oracle_cursor.execute(sql_data)

    # GPKG taula sortu
    gpkg_cursor = gpkg_conn.cursor()
    gpkg_cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            b5mcode TEXT,
            name TEXT,
            name_eu TEXT,
            name_es TEXT,
            type_eu TEXT,
            type_es TEXT,
            description_eu TEXT,
            description_es TEXT,
            observation_eu TEXT,
            observation_es TEXT,
            b5midname INTEGER
        )
    """)

    # Datuak gehitu
    row_count = 0
    for row in oracle_cursor:
        gpkg_cursor.execute(f"""
            INSERT INTO {table_name}
            (b5mcode, name, name_eu, name_es, type_eu, type_es,
             description_eu, description_es, observation_eu, observation_es, b5midname)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

        row_count += 1

    # Attributes taula bezala metadata gehitu
    gpkg_cursor.execute("""
        INSERT INTO gpkg_contents VALUES (?, 'attributes', ?, 'Errepide datuak', datetime('now'), NULL, NULL, NULL, NULL, NULL)
    """, (table_name, table_name))

    gpkg_conn.commit()
    oracle_cursor.close()

    print(f"  ✓ {row_count} erregistro alfanumeriko gehituta")

def create_view(gpkg_conn, view_name, geom_table, data_table):
    """Bi taulen arteko bista sortu"""

    cursor = gpkg_conn.cursor()

    # Bista sortu b5midname bidez elkartuz
    cursor.execute(f"""
        CREATE VIEW {view_name} AS
        SELECT
            g.id as geom_id,
            g.b5midut,
            g.bridge_tunnel,
            g.geom,
            d.id as data_id,
            d.b5mcode,
            d.name,
            d.name_eu,
            d.name_es,
            d.type_eu,
            d.type_es,
            d.description_eu,
            d.description_es,
            d.observation_eu,
            d.observation_es,
            g.b5midname
        FROM {geom_table} g
        LEFT JOIN {data_table} d ON g.b5midname = d.b5midname
    """)

    # Bista metadata gehitu
    cursor.execute("""
        INSERT INTO gpkg_contents VALUES (?, 'features', ?, 'Errepide datu osoak', datetime('now'), NULL, NULL, NULL, NULL, 25830)
    """, (view_name, view_name))

    cursor.execute("""
        INSERT INTO gpkg_geometry_columns VALUES (?, 'geom', 'GEOMETRY', 25830, 0, 0)
    """, (view_name,))

    gpkg_conn.commit()

    print(f"  ✓ Bista sortua: {view_name}")

if __name__ == "__main__":
    main()
