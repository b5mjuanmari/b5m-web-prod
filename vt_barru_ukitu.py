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
    python3 vt_barru_ukitu.py <gpkg1> <gpkg2> <irteera_gpkg> [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)
"""

import sys
import os
import time

import geopandas as gpd

from log_utils import Log


# Oracle Spatialeko OVERLAPBDYINTERSECT erlazioaren DE-9IM maskara.
OVERLAPBDYINTERSECT = "T*T***T**"


def main():
    hasiera = time.time()

    script_izena = os.path.basename(sys.argv[0])

    # --- Argumentuak egiaztatu ---
    if len(sys.argv) not in (4, 5):
        print(
            f"Erabilera: {script_izena} <gpkg1> <gpkg2> <irteera_gpkg> "
            f"[log_fitxategia]",
            file=sys.stderr,
        )
        sys.exit(1)

    gpkg1_bidea = sys.argv[1]
    gpkg2_bidea = sys.argv[2]
    irteera_bidea = sys.argv[3]
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, script_izena, sys.argv[1:])

    try:
        # Sarrerako fitxategiak existitzen diren egiaztatu
        for bidea in (gpkg1_bidea, gpkg2_bidea):
            if not os.path.isfile(bidea):
                log.errorea(f"Ez da fitxategia aurkitu: {bidea}")
                sys.exit(1)

        # Irteerako fitxategia existitzen bada, ezabatu
        if os.path.exists(irteera_bidea):
            try:
                os.remove(irteera_bidea)
                log.info(f"Aurreko irteera ezabatu da: {irteera_bidea}")
            except OSError as e:
                log.errorea(f"Ezin izan da irteera ezabatu: {e}")
                sys.exit(1)

        # Irteerako geruzaren izena: fitxategiaren izena .gpkg gabe
        layer_izena = os.path.splitext(os.path.basename(irteera_bidea))[0]
        log.info(f"Irteerako geruzaren izena: {layer_izena}")

        # GPKGak irakurri
        log.info(f"{gpkg1_bidea} irakurtzen...")
        gdf1 = gpd.read_file(gpkg1_bidea)

        log.info(f"{gpkg2_bidea} irakurtzen...")
        gdf2 = gpd.read_file(gpkg2_bidea)

        log.info(f"gpkg1 elementuak: {len(gdf1)}")
        log.info(f"gpkg2 elementuak: {len(gdf2)}")

        # CRS bateratu
        if gdf1.crs != gdf2.crs:
            log.abisua(
                f"CRS desberdinak: {gdf1.crs} -> {gdf2.crs}. Bateratzen..."
            )
            gdf2 = gdf2.to_crs(gdf1.crs)

        # 'subtype' eremua beharrezkoa da
        if "subtype" not in gdf2.columns:
            log.errorea(
                "gpkg2-ko atributu taulan ez dago 'subtype' eremurik."
            )
            sys.exit(1)

        # Intertidal maskara
        intertidal_maskara = gdf2["subtype"] == "intertidal"
        log.info(
            f"'intertidal' motako elementuak (beti gehituko dira): "
            f"{intertidal_maskara.sum()}"
        )

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

        log.info(f"Hautatutako elementuak guztira: {len(emaitza)}")

        # Irteera gorde, layer izen egokiarekin
        emaitza.to_file(irteera_bidea, driver="GPKG", layer=layer_izena)
        log.info(
            f"Irteera gorde da: {irteera_bidea} (layer: {layer_izena})"
        )

        iraupena = time.time() - hasiera
        log.info(f"Exekuzio denbora: {iraupena:.2f} segundo")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
