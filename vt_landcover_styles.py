#!/usr/bin/env python3
"""
vt_landcover_styles.py

GeoPackage fitxategi batean QGIS estilo bat (.qml) gordetzen du
layer_styles taulan, QGIS-ek erabiltzen duen estrukturarekin.

Erabilera:
    python3 vt_landcover_styles.py <gpkg> <geruza_izena> <geom_eremua> <estilo_izena> <qml_fitxategia> [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)

Adibidea:
    python3 vt_landcover_styles.py ./dat/vt_landcover_SIOSEAR2.gpkg \
        vt_landcover_SIOSEAR2 geom vt_landcover_SIOSEAR2_style \
        /home9/SHP/vt_landcover/SIOSEAR/CONF/vt_landcover_SIOSEAR.qml
"""

import argparse
import os
import sqlite3
import sys

from log_utils import Log


def ensure_layer_styles_table(cur, log):
    """Sortu layer_styles taula QGIS-en estruktura ofizialarekin, ez badago."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS layer_styles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            f_table_catalog TEXT,
            f_table_schema TEXT,
            f_table_name TEXT,
            f_geometry_column TEXT,
            styleName TEXT,
            styleQML TEXT,
            styleSLD TEXT,
            useAsDefault BOOLEAN,
            description TEXT,
            owner TEXT,
            ui TEXT,
            update_time DATETIME
        )
    """)


def register_in_gpkg_contents(cur, log, table_name="layer_styles"):
    """Erregistratu layer_styles gpkg_contents-en, QGIS-ek egiten duen bezala.
    Taula edo eremuak ez badaude, isilpean jarraitu."""
    try:
        # Ziurtatu gpkg_contents existitzen dela (GeoPackage izan behar du)
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='gpkg_contents'
        """)
        if cur.fetchone() is None:
            return

        # Begiratu ea layer_styles jada erregistratuta dagoen
        cur.execute(
            "SELECT 1 FROM gpkg_contents WHERE table_name = ?",
            (table_name,),
        )
        if cur.fetchone() is not None:
            return

        # Lortu zein den srs_id erabilgarri (NULL onartzen bada)
        cur.execute("""
            INSERT INTO gpkg_contents
            (table_name, data_type, identifier, description,
             last_change, min_x, min_y, max_x, max_y, srs_id)
            VALUES (?, 'attributes', ?, 'QGIS layer styles',
                    datetime('now'), NULL, NULL, NULL, NULL, NULL)
        """, (table_name, table_name))
    except sqlite3.Error as e:
        # Ez da kritikoa; abisua eman eta jarraitu
        log.abisua(f"Ezin izan da gpkg_contents eguneratu: {e}")


def insert_style(gpkg, layer, geom_col, style_name, qml_path, log,
                 use_default=True):
    if not os.path.isfile(gpkg):
        raise FileNotFoundError(f"Ez da GPKG fitxategia aurkitu: {gpkg}")
    if not os.path.isfile(qml_path):
        raise FileNotFoundError(f"Ez da QML fitxategia aurkitu: {qml_path}")

    with open(qml_path, "r", encoding="utf-8") as f:
        qml = f.read()

    if not qml.strip():
        raise ValueError(f"QML fitxategia hutsik dago: {qml_path}")

    log.info(f"GPKG: {gpkg}")
    log.info(f"Geruza: {layer}")
    log.info(f"Geometria-eremua: {geom_col}")
    log.info(f"Estilo-izena: {style_name}")
    log.info(f"QML fitxategia: {qml_path}")
    log.info(f"QML luzera: {len(qml)} karaktere")
    log.info(f"Lehenetsi gisa: {'bai' if use_default else 'ez'}")

    con = sqlite3.connect(gpkg)
    try:
        cur = con.cursor()

        ensure_layer_styles_table(cur, log)
        register_in_gpkg_contents(cur, log)

        # Estilo bera bazegoen, ezabatu (berridazteko)
        cur.execute("""
            DELETE FROM layer_styles
            WHERE f_table_name = ? AND styleName = ?
        """, (layer, style_name))

        cur.execute("""
            INSERT INTO layer_styles
            (f_table_catalog, f_table_schema, f_table_name, f_geometry_column,
             styleName, styleQML, styleSLD, useAsDefault,
             description, owner, ui, update_time)
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, NULL, NULL, datetime('now'))
        """, ("", "", layer, geom_col, style_name, qml, 1 if use_default else 0))

        con.commit()

        # Egiaztapena
        cur.execute("""
            SELECT id, length(styleQML), useAsDefault
            FROM layer_styles
            WHERE f_table_name = ? AND styleName = ?
        """, (layer, style_name))
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Estiloa txertatu ondoren ez da aurkitu.")

        sid, qml_len, usedef = row
        log.info("OK: estiloa gorde da.")
        log.info(f"  ID:          {sid}")
        log.info(f"  QML luzera:  {qml_len} karaktere")
        log.info(f"  Lehenetsia:  {'bai' if usedef else 'ez'}")
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description="QGIS .qml estiloa GeoPackage baten layer_styles taulan sartu."
    )
    parser.add_argument("gpkg", help="GeoPackage fitxategiaren bidea")
    parser.add_argument("layer", help="Geruza-izena GPKG barruan (f_table_name)")
    parser.add_argument("geom_col", help="Eremu geometrikoa (adib. 'geom')")
    parser.add_argument("style_name", help="Estiloaren izena GPKG barruan")
    parser.add_argument("qml", help=".qml estilo fitxategiaren bidea")
    parser.add_argument(
        "log_path",
        nargs="?",
        default=None,
        help="Log fitxategiaren bidea (aukerakoa)",
    )
    parser.add_argument(
        "--no-default",
        action="store_true",
        help="Ez markatu estiloa lehenetsi gisa (useAsDefault=0)",
    )

    args = parser.parse_args()

    # --- Log sistema abiarazi ---
    izena = os.path.basename(sys.argv[0])
    log = Log(args.log_path, izena, sys.argv[1:])

    try:
        insert_style(
            gpkg=args.gpkg,
            layer=args.layer,
            geom_col=args.geom_col,
            style_name=args.style_name,
            qml_path=args.qml,
            log=log,
            use_default=not args.no_default,
        )
    except Exception as e:
        log.errorea(f"{type(e).__name__}: {e}")
        log.bukaera()
        sys.exit(1)

    log.bukaera()


if __name__ == "__main__":
    main()
