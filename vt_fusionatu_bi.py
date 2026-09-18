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
- 'type' eta 'subtype' zutabeak badaude eta 'subtype' NULL bada, 'type'-ren balioa ezartzen zaio.
- Irteerako geruzaren izena: irteerako fitxategiaren izena, .gpkg atzizkirik gabe.

Erabilera:
    python3 vt_fusionatu_bi.py <sarrera1.gpkg> <sarrera2.gpkg> <irteera.gpkg> [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)
"""

import os
import sys
import time

import geopandas as gpd
import pandas as pd

from log_utils import Log


def usage(script_name, log):
    """Erabileraren mezua erakutsi."""
    log.errorea(
        f"Erabilera: {script_name} <sarrera1.gpkg> <sarrera2.gpkg> "
        f"<irteera.gpkg> [log_fitxategia]"
    )
    log.errorea("  sarrera1.gpkg   : Lehenengo sarrerako GPKG fitxategia")
    log.errorea("  sarrera2.gpkg   : Bigarren sarrerako GPKG fitxategia")
    log.errorea(
        "  irteera.gpkg    : Irteerako GPKG fitxategia (badago, ezabatu egingo da)"
    )
    log.errorea(
        "  log_fitxategia  : (aukerakoa) log fitxategiaren bidea"
    )
    sys.exit(1)


def check_input(path, script_name, log):
    """Sarrerako fitxategia existitzen den eta irakurgarria den egiaztatu."""
    if not os.path.isfile(path):
        log.errorea(f"Sarrerako fitxategia ez da existitzen: {path}")
        usage(script_name, log)
    if not os.access(path, os.R_OK):
        log.errorea(f"Sarrerako fitxategia ezin da irakurri: {path}")
        sys.exit(1)


def remove_if_exists(path, log):
    """Irteerako fitxategia existitzen bada, ezabatu."""
    if os.path.exists(path):
        log.abisua(
            f"Irteerako fitxategia existitzen zen, ezabatu egingo da: {path}"
        )
        os.remove(path)


def get_single_layer(path, log):
    """
    GPKG fitxategiko geruza-izen bakarra itzuli.
    Geruza bat baino gehiago badago, lehenengoa hartu eta ohartarazi.
    """
    import fiona
    layers = fiona.listlayers(path)
    if not layers:
        log.errorea(f"Ez dago geruzarik {path} fitxategian.")
        sys.exit(1)
    if len(layers) > 1:
        log.abisua(
            f"{path} fitxategian geruza bat baino gehiago dago: {layers}"
        )
        log.abisua(f"Lehenengoa erabiliko da: {layers[0]}")
    return layers[0]


def main():
    start = time.time()

    script_name = os.path.basename(sys.argv[0])

    # --- Argumentuak egiaztatu ---
    if len(sys.argv) not in (4, 5):
        print(
            f"Erabilera: {script_name} <sarrera1.gpkg> <sarrera2.gpkg> "
            f"<irteera.gpkg> [log_fitxategia]",
            file=sys.stderr,
        )
        sys.exit(1)

    input1 = sys.argv[1]
    input2 = sys.argv[2]
    output = sys.argv[3]
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, script_name, sys.argv[1:])

    try:
        check_input(input1, script_name, log)
        check_input(input2, script_name, log)
        remove_if_exists(output, log)

        log.info(f"==> Fusionatzen: {input1} + {input2} -> {output}")

        # Geruza-izenak lortu
        layer1 = get_single_layer(input1, log)
        layer2 = get_single_layer(input2, log)

        log.info(f"  Sarrera1 geruza: {layer1}")
        log.info(f"  Sarrera2 geruza: {layer2}")

        # Datuak irakurri
        gdf1 = gpd.read_file(input1, layer=layer1)
        gdf2 = gpd.read_file(input2, layer=layer2)

        log.info(
            f"  Sarrera1: {len(gdf1)} errenkada, zutabeak: "
            f"{list(gdf1.columns)}"
        )
        log.info(
            f"  Sarrera2: {len(gdf2)} errenkada, zutabeak: "
            f"{list(gdf2.columns)}"
        )

        # Atributu-egiturak konparatu
        cols1 = list(gdf1.columns)
        cols2 = list(gdf2.columns)

        log.info("--- Atributu-egiturak konparatzen ---")
        if cols1 == cols2:
            log.info("  Egiturak berdinak dira. Egitura mantendu.")
        else:
            log.info(
                "  Egiturak ezberdinak dira. Eremu komunak + berriak gehitu."
            )
            berriak2 = [c for c in cols2 if c not in cols1]
            berriak1 = [c for c in cols1 if c not in cols2]
            if berriak1:
                log.info(f"    Sarrera1ean bakarrik: {berriak1}")
            if berriak2:
                log.info(f"    Sarrera2an bakarrik: {berriak2}")

        # Geometria-zutabearen izena lortu
        geom_col1 = gdf1.geometry.name
        geom_col2 = gdf2.geometry.name
        out_geom_col = geom_col1

        # Geometria-motak
        geom_type1 = gdf1.geom_type.unique().tolist()
        geom_type2 = gdf2.geom_type.unique().tolist()
        log.info(f"  Sarrera1 geometria-motak: {geom_type1}")
        log.info(f"  Sarrera2 geometria-motak: {geom_type2}")

        # SRS bateratu: sarrera1-ekoa erabili
        srs1 = gdf1.crs
        srs2 = gdf2.crs
        if srs1 != srs2:
            log.abisua(f"SRS ezberdinak: {srs1} vs {srs2}")
            log.abisua(f"Sarrera1-eko SRS-a erabiliko da: {srs1}")
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

        log.info(f"  Irteerako zutabeak: {merged_cols}")

        # Fusionatu
        gdf_out = pd.concat([gdf1_align, gdf2_align], ignore_index=True)
        gdf_out = GeoDataFrame(gdf_out, geometry=out_geom_col, crs=srs1)

        # 'type' eta 'subtype' zutabeak existitzen badira, bete 'subtype' NULL den tokietan
        if "type" in gdf_out.columns and "subtype" in gdf_out.columns:
            mask = gdf_out["subtype"].isna()
            n_filled = int(mask.sum())
            if n_filled > 0:
                gdf_out.loc[mask, "subtype"] = gdf_out.loc[mask, "type"]
                log.info(
                    f"  'subtype' eremua bete da 'type'-ren balioarekin "
                    f"{n_filled} errenkadatan."
                )
            else:
                log.info(
                    "  'subtype' eremuan ez dago balio ezezagunik; "
                    "ez da ezer aldatu."
                )
        else:
            if "type" not in gdf_out.columns:
                log.abisua(
                    "'type' zutabea ez da aurkitu; ez da 'subtype' bete."
                )
            if "subtype" not in gdf_out.columns:
                log.abisua(
                    "'subtype' zutabea ez da aurkitu; ez da ezer egin."
                )

        # Irteera idatzi
        out_layer = os.path.splitext(os.path.basename(output))[0]
        log.info(f"  Irteerako geruza: {out_layer}")
        log.info(f"  Irteerako errenkada kopurua: {len(gdf_out)}")

        gdf_out.to_file(output, layer=out_layer, driver="GPKG")

        elapsed = time.time() - start
        log.info(f"==> Prozesua amaituta. Denbora: {elapsed:.2f} segundo")

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
