#!/usr/bin/env python3
"""
Scripta: bi GPKG fitxategi hartu eta hirugarren bat sortu.

Araua:
  - gpkg2-ko elementuak hautatzen dira baldin eta gpkg1-eko edozein
    elementurekin CONTAINS (within) edo OVERLAPBDYINTERSECT erlazioa
    badute.
  - SALBUESPENA: gpkg2-ko elementuak 'subtype == "intertidal"' badira,
    ez dira erlazio horiek egiaztatzen; beti gehitzen dira emaitzari.

Irteerako GPKG-ren geruzaren izena fitxategiaren izena izango da,
.gpkg atzizkia gabe.

Erabilera:
    python3 script.py <gpkg1> <gpkg2> <irteera_gpkg>
"""

import sys
import os
import time

import geopandas as gpd


# Oracle Spatialeko OVERLAPBDYINTERSECT erlazioaren DE-9IM maskara.
OVERLAPBDYINTERSECT = "T*T***T**"


def main():
    hasiera = time.time()

    if len(sys.argv) != 4:
        script_izena = os.path.basename(sys.argv[0])
        print(f"Erabilera: {script_izena} <gpkg1> <gpkg2> <irteera_gpkg>")
        sys.exit(1)

    script_izena = os.path.basename(sys.argv[0])
    gpkg1_bidea = sys.argv[1]
    gpkg2_bidea = sys.argv[2]
    irteera_bidea = sys.argv[3]

    # Sarrerako fitxategiak existitzen diren egiaztatu
    for bidea in (gpkg1_bidea, gpkg2_bidea):
        if not os.path.isfile(bidea):
            print(f"[ERROREA] Ez da fitxategia aurkitu: {bidea}")
            sys.exit(1)

    # Irteerako fitxategia existitzen bada, ezabatu
    if os.path.exists(irteera_bidea):
        try:
            os.remove(irteera_bidea)
            print(f"[INFO] Aurreko irteera ezabatu da: {irteera_bidea}")
        except OSError as e:
            print(f"[ERROREA] Ezin izan da irteera ezabatu: {e}")
            sys.exit(1)

    # Irteerako geruzaren izena: fitxategiaren izena .gpkg gabe
    layer_izena = os.path.splitext(os.path.basename(irteera_bidea))[0]
    print(f"[INFO] Irteerako geruzaren izena: {layer_izena}")

    # GPKGak irakurri
    print(f"[INFO] {gpkg1_bidea} irakurtzen...")
    gdf1 = gpd.read_file(gpkg1_bidea)

    print(f"[INFO] {gpkg2_bidea} irakurtzen...")
    gdf2 = gpd.read_file(gpkg2_bidea)

    print(f"[INFO] gpkg1 elementuak: {len(gdf1)}")
    print(f"[INFO] gpkg2 elementuak: {len(gdf2)}")

    # CRS bateratu
    if gdf1.crs != gdf2.crs:
        print(f"[INFO] CRS desberdinak: {gdf1.crs} -> {gdf2.crs}. Bateratzen...")
        gdf2 = gdf2.to_crs(gdf1.crs)

    # 'subtype' eremua beharrezkoa da
    if "subtype" not in gdf2.columns:
        print("[ERROREA] gpkg2-ko atributu taulan ez dago 'subtype' eremurik.")
        sys.exit(1)

    # Intertidal maskara
    intertidal_maskara = gdf2["subtype"] == "intertidal"
    print(f"[INFO] 'intertidal' motako elementuak (beti gehituko dira): "
          f"{intertidal_maskara.sum()}")

    # gdf1-en indize espaziala
    gdf1_sindex = gdf1.sindex
    gdf1_geoms = gdf1.geometry.values

    hautatutako_indizeak = []

    for idx, geom2 in enumerate(gdf2.geometry):
        if geom2 is None or geom2.is_empty:
            continue

        # Intertidal bada, beti sartu (ez da erlazioa egiaztatu behar)
        if intertidal_maskara.iloc[idx]:
            hautatutako_indizeak.append(idx)
            continue

        # Bestela, CONTAINS edo OVERLAPBDYINTERSECT egiaztatu
        kandidatuak = gdf1_sindex.query(geom2, predicate="intersects")

        for k in kandidatuak:
            geom1 = gdf1_geoms[k]
            if geom1 is None or geom1.is_empty:
                continue

            # 1) CONTAINS: geom2 geom1-en barruan
            if geom2.within(geom1):
                hautatutako_indizeak.append(idx)
                break

            # 2) OVERLAPBDYINTERSECT: DE-9IM maskara
            if geom1.relate_pattern(geom2, OVERLAPBDYINTERSECT):
                hautatutako_indizeak.append(idx)
                break

    emaitza = gdf2.iloc[hautatutako_indizeak].copy()

    print(f"[INFO] Hautatutako elementuak guztira: {len(emaitza)}")

    # Irteera gorde, layer izen egokiarekin
    emaitza.to_file(irteera_bidea, driver="GPKG", layer=layer_izena)
    print(f"[INFO] Irteera gorde da: {irteera_bidea} (layer: {layer_izena})")

    iraupena = time.time() - hasiera
    print(f"[INFO] Exekuzio denbora: {iraupena:.2f} segundo")


if __name__ == "__main__":
    main()
