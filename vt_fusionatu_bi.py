#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vt_fusionatu_bi.py

Bi GPKG fitxategi fusionatzen ditu hirugarren batean, geopandas erabiliz.
- Sarrerako fitxategi bakoitzak taula/geruza bakarra du.
- Bi taulen izenak ezberdinak badira ere, fusionatu egiten dira.
- Atributu-egiturak berdinak badira, egitura mantentzen da.
- Ezberdinak badira, eremu komunak mantentzen dira eta ezberdinak gehitzen dira.
- Eremu berrietan NULL jartzen da (pandas-ek NaN gisa).
- Irteerako geruzaren izena: irteerako fitxategiaren izena, .gpkg atzizkirik gabe.
"""

import os
import sys
import time

import geopandas as gpd
import pandas as pd


def usage(script_name):
    """Erabileraren mezua erakutsi."""
    print(f"Erabilera: {script_name} <sarrera1.gpkg> <sarrera2.gpkg> <irteera.gpkg>")
    print()
    print("  sarrera1.gpkg  : Lehenengo sarrerako GPKG fitxategia")
    print("  sarrera2.gpkg  : Bigarren sarrerako GPKG fitxategia")
    print("  irteera.gpkg   : Irteerako GPKG fitxategia (badago, ezabatu egingo da)")
    sys.exit(1)


def check_input(path, script_name):
    """Sarrerako fitxategia existitzen den eta irakurgarria den egiaztatu."""
    if not os.path.isfile(path):
        print(f"ERROREA: Sarrerako fitxategia ez da existitzen: {path}")
        usage(script_name)
    if not os.access(path, os.R_OK):
        print(f"ERROREA: Sarrerako fitxategia ezin da irakurri: {path}")
        sys.exit(1)


def remove_if_exists(path):
    """Irteerako fitxategia existitzen bada, ezabatu."""
    if os.path.exists(path):
        print(f"OHARRA: Irteerako fitxategia existitzen zen, ezabatu egingo da: {path}")
        os.remove(path)


def get_single_layer(path):
    """
    GPKG fitxategiko geruza-izen bakarra itzuli.
    Geruza bat baino gehiago badago, lehenengoa hartu eta ohartarazi.
    """
    import fiona
    layers = fiona.listlayers(path)
    if not layers:
        print(f"ERROREA: Ez dago geruzarik {path} fitxategian.")
        sys.exit(1)
    if len(layers) > 1:
        print(f"OHARRA: {path} fitxategian geruza bat baino gehiago dago: {layers}")
        print(f"        Lehenengoa erabiliko da: {layers[0]}")
    return layers[0]


def main():
    start = time.time()

    script_name = os.path.basename(sys.argv[0])

    if len(sys.argv) != 4:
        usage(script_name)

    input1, input2, output = sys.argv[1], sys.argv[2], sys.argv[3]

    check_input(input1, script_name)
    check_input(input2, script_name)
    remove_if_exists(output)

    print(f"==> Fusionatzen: {input1} + {input2} -> {output}")

    # Geruza-izenak lortu
    layer1 = get_single_layer(input1)
    layer2 = get_single_layer(input2)

    print(f"  Sarrera1 geruza: {layer1}")
    print(f"  Sarrera2 geruza: {layer2}")

    # Datuak irakurri
    gdf1 = gpd.read_file(input1, layer=layer1)
    gdf2 = gpd.read_file(input2, layer=layer2)

    print(f"\n  Sarrera1: {len(gdf1)} errenkada, zutabeak: {list(gdf1.columns)}")
    print(f"  Sarrera2: {len(gdf2)} errenkada, zutabeak: {list(gdf2.columns)}")

    # Atributu-egiturak konparatu
    cols1 = list(gdf1.columns)
    cols2 = list(gdf2.columns)

    print(f"\n--- Atributu-egiturak konparatzen ---")
    if cols1 == cols2:
        print("  Egiturák berdinak dira. Egitura mantendu.")
    else:
        print("  Egiturák ezberdinak dira. Eremu komunak + berriak gehitu.")
        berriak2 = [c for c in cols2 if c not in cols1]
        berriak1 = [c for c in cols1 if c not in cols2]
        if berriak1:
            print(f"    Sarrera1ean bakarrik: {berriak1}")
        if berriak2:
            print(f"    Sarrera2an bakarrik: {berriak2}")

    # Geometria-zutabearen izena lortu
    geom_col1 = gdf1.geometry.name
    geom_col2 = gdf2.geometry.name
    out_geom_col = geom_col1

    # Geometria-motak
    geom_type1 = gdf1.geom_type.unique().tolist()
    geom_type2 = gdf2.geom_type.unique().tolist()
    print(f"\n  Sarrera1 geometria-motak: {geom_type1}")
    print(f"  Sarrera2 geometria-motak: {geom_type2}")

    # SRS bateratu: sarrera1-ekoa erabili
    srs1 = gdf1.crs
    srs2 = gdf2.crs
    if srs1 != srs2:
        print(f"OHARRA: SRS ezberdinak: {srs1} vs {srs2}")
        print(f"        Sarrera1-eko SRS-a erabiliko da: {srs1}")
        gdf2 = gdf2.to_crs(srs1)

    # Sarrera2-ko geometria-zutabea berrizendatu behar bada
    if geom_col2 != out_geom_col:
        gdf2 = gdf2.rename_geometry(out_geom_col)

    # Zutabeen batasuna
    merged_cols = list(cols1)
    for c in cols2:
        if c not in merged_cols:
            merged_cols.append(c)

    # Bi GeoDataFrame-ak zutabe berdinak izan ditzaten
    gdf1_align = gdf1.reindex(columns=merged_cols)
    gdf2_align = gdf2.reindex(columns=merged_cols)

    from geopandas import GeoDataFrame
    gdf1_align = GeoDataFrame(gdf1_align, geometry=out_geom_col, crs=srs1)
    gdf2_align = GeoDataFrame(gdf2_align, geometry=out_geom_col, crs=srs1)

    print(f"\n  Irteerako zutabeak: {merged_cols}")

    # Fusionatu
    gdf_out = pd.concat([gdf1_align, gdf2_align], ignore_index=True)
    gdf_out = GeoDataFrame(gdf_out, geometry=out_geom_col, crs=srs1)

    # Irteera idatzi
    # Geruza-izena: irteerako fitxategiaren izena, .gpkg atzizkirik gabe
    out_layer = os.path.splitext(os.path.basename(output))[0]
    print(f"\n  Irteerako geruza: {out_layer}")
    print(f"  Irteerako errenkada kopurua: {len(gdf_out)}")

    gdf_out.to_file(output, layer=out_layer, driver="GPKG")

    elapsed = time.time() - start
    print(f"\n==> Prozesua amaituta. Denbora: {elapsed:.2f} segundo")


if __name__ == "__main__":
    main()
