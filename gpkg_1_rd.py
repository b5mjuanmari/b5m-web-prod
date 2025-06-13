import sys
import os
import sqlite3
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from shapely import wkb
import cx_Oracle

def create_gpkg(gpkg_path):
    # Ezabatu GPKG fitxategia existitzen bada
    if os.path.exists(gpkg_path):
        os.remove(gpkg_path)

    # Konektatu SQLite datu basera (GPKG fitxategia)
    engine = create_engine(f'sqlite:///{gpkg_path}')

    # Datu geografikoak lortzeko SQL kontsulta
    sql_geom = """
    SELECT
      a.idut AS b5midut,
      b.puente_tunel AS bridge_tunnel,
      b.idnombre AS b5midname,
      a.polyline AS geom
    FROM
      b5mweb_25830.vialesind a
    JOIN
      b5mweb_nombres.v_vialtramo b ON b.idut = a.idut
    WHERE
      b.nomtipo_e = 'errepidea'
    ORDER BY
      a.idut
    """

    # Datu alfanumerikoak lortzeko SQL kontsulta
    sql_dat = """
    SELECT DISTINCT
      a.url_2d AS b5mcode,
      CASE WHEN a.nombre_e = a.nombre_c THEN a.nombre_e ELSE a.nombre_e || ' / ' || a.nombre_c END AS name,
      a.nombre_e AS name_eu,
      a.nombre_c AS name_es,
      e.description_eu AS type_eu,
      e.description_es AS type_es,
      b.descripcion_e AS description_eu,
      b.descripcion_c AS description_es,
      b.observacion_e AS observation_eu,
      b.observacion_c AS observation_es,
      b.idnombre AS b5midname
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

    # Konektatu Oracle datu basera eta datuak lortu
    # Oracle datu basearen konexioa konfiguratu behar duzu
    oracle_engine = create_engine('oracle+cx_oracle://b5mweb_nombres:web+@exploracle:1521/bdet')

    try:
        # Datu geografikoak lortu eta GPKG fitxategian gorde
        with oracle_engine.connect() as connection:
            df_geom = pd.read_sql(sql_geom, connection)
            df_geom['geom'] = df_geom['geom'].apply(lambda x: wkb.loads(x.read()) if x else None)
            gdf_geom = gpd.GeoDataFrame(df_geom, geometry='geom')
            gdf_geom.to_file(gpkg_path, layer=os.path.splitext(os.path.basename(gpkg_path))[0] + '_geom', driver='GPKG')

        # Datu alfanumerikoak lortu eta GPKG fitxategian gorde
        df_dat = pd.read_sql(sql_dat, oracle_engine)
        df_dat.to_sql(os.path.splitext(os.path.basename(gpkg_path))[0] + '_dat', engine, if_exists='replace', index=False)

        # Bista sortu bi taulak erlazionatzeko
        with sqlite3.connect(gpkg_path) as conn:
            view_name = os.path.splitext(os.path.basename(gpkg_path))[0] + '_view'
            view_query = f"""
            CREATE VIEW {view_name} AS
            SELECT
                g.b5midut, g.bridge_tunnel, g.b5midname, g.geom,
                d.b5mcode, d.name, d.name_eu, d.name_es, d.type_eu, d.type_es,
                d.description_eu, d.description_es, d.observation_eu, d.observation_es
            FROM
                '{os.path.splitext(os.path.basename(gpkg_path))[0] + "_geom"}' g
            JOIN
                '{os.path.splitext(os.path.basename(gpkg_path))[0] + "_dat"}' d ON g.b5midname = d.b5midname
            """
            conn.execute(view_query)
    except Exception as e:
        print(f"Error connecting to Oracle database: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        script_name = os.path.basename(sys.argv[0])
        print(f"Erabilera: python3 {script_name} GPKG_fitxategiaren_izena_eta_kokapena")
        sys.exit(1)

    gpkg_path = sys.argv[1]
    create_gpkg(gpkg_path)
