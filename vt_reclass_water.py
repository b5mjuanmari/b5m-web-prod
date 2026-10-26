#!/usr/bin/env python3
"""'water other' poligonoak birsailkatu gertuen dagoen poligonoaren 'type' balioarekin."""

import os
import sys
import time

import geopandas as gpd

from log_utils import Log

SCRIPT_IZENA = os.path.basename(sys.argv[0])
LOG_BIDEA = os.path.splitext(SCRIPT_IZENA)[0] + ".log"   # None jarri fitxategirik nahi ez bada

TARGET = "water other"
EXCLUDE = ("water", "water other")


def erabilera():
    return "Erabilera: {} sarrera.gpkg irteera.gpkg".format(SCRIPT_IZENA)


def ezabatu_gpkg(bidea):
    """GPKG fitxategia (eta SQLite -wal/-shm fitxategiak) ezabatu."""
    for atz in ("", "-wal", "-shm"):
        if os.path.exists(bidea + atz):
            os.remove(bidea + atz)


def birsailkatu(gdf, log):
    mask = gdf["type"] == TARGET
    n_target = int(mask.sum())
    cands = gdf.loc[~gdf["type"].isin(EXCLUDE), ["type", "geometry"]].reset_index(drop=True)
    log.info("'{}' poligonoak: {} | kandidatuak: {}".format(TARGET, n_target, len(cands)))

    if n_target == 0:
        log.abisua("Ez dago birsailkatzeko poligonorik.")
        return 0, 0
    if len(cands) == 0:
        log.abisua("Ez dago kandidaturik; ez da ezer birsailkatuko.")
        return 0, n_target

    geoms = cands.geometry.values
    types = cands["type"].values
    sidx = cands.sindex

    def gertuena(geom, d=50.0, dmax=50000.0):
        if geom is None or geom.is_empty:
            return None
        minx, miny, maxx, maxy = geom.bounds
        while d <= dmax:
            pos = list(sidx.intersection((minx - d, miny - d, maxx + d, maxy + d)))
            if pos:
                dists = [geoms[i].distance(geom) for i in pos]
                dmin = min(dists)
                if dmin <= d:   # ez dago bbox-etik kanpo hurbilagorik
                    return types[pos[dists.index(dmin)]]
            d *= 2
        return None

    new_types = gdf.loc[mask, "geometry"].apply(gertuena)
    ok = new_types.notna()
    gdf.loc[new_types[ok].index, "type"] = new_types[ok]
    return int(ok.sum()), int((~ok).sum())


def main(log):
    if len(sys.argv) != 3:
        log.errorea("Parametro kopuru okerra. " + erabilera())
        return 1

    sarrera, irteera = sys.argv[1], sys.argv[2]

    if not os.path.isfile(sarrera):
        log.errorea("Sarrerako GPKG fitxategia ez dago: {}".format(sarrera))
        return 1

    if os.path.abspath(sarrera) == os.path.abspath(irteera):
        log.errorea("Sarrera eta irteera fitxategi bera dira; ez da ezer egingo.")
        return 1

    t0 = time.time()

    log.info("Sarrera irakurtzen: {}".format(sarrera))
    gdf = gpd.read_file(sarrera)
    log.info("{} poligono irakurri dira".format(len(gdf)))

    if "type" not in gdf.columns:
        log.errorea("Sarrerak ez du 'type' eremurik.")
        return 1

    birsailkatuak, geratuak = birsailkatu(gdf, log)
    log.info("Birsailkatuak: {} | kandidaturik gabe geratuak: {}".format(birsailkatuak, geratuak))

    if os.path.exists(irteera):
        log.info("Irteerako fitxategia existitzen da, ezabatzen: {}".format(irteera))
        ezabatu_gpkg(irteera)

    geruza = os.path.splitext(os.path.basename(irteera))[0]
    log.info("Irteera idazten: {} (geruza: {})".format(irteera, geruza))
    gdf.to_file(irteera, layer=geruza, driver="GPKG")

    dt = time.time() - t0
    log.info("Denbora totala: {:d}m {:04.1f}s".format(int(dt // 60), dt % 60))
    return 0


if __name__ == "__main__":
    with Log(LOG_BIDEA, SCRIPT_IZENA, sys.argv[1:]) as log:
        kodea = main(log)
    sys.exit(kodea)
