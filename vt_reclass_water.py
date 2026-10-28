#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vt_reclass_water.py
===================

'type = "water other"' duten poligonoak birsailkatu, gertuen dagoen
poligonoaren 'type' balioarekin.

Prozesuaren laburpena
---------------------
1. Argumentuak egiaztatu (3 parametro) eta log fitxategia prestatu.
2. Sarrerako GPKG fitxategia irakurri.
3. Poligonoak bi taldetan banatu:
     - XEDEAK     : type = 'water other'  (birsailkatu beharrekoak)
     - KANDIDATUAK: type ez dena 'water', 'intertidal water' ez
                    'water other' (hartu daitezkeen balioen jabeak)
4. Xede bakoitzerako, gertuen dagoen kandidatua bilatu (distantzia
   geometrikoa, ez bounding box-arena) eta bere 'type' balioa kopiatu.
   Bilaketa indize espazialarekin azkartzen da (ikus 'gertuena').
5. Irteerako GPKG-a ezabatu existitzen bada, eta emaitza idatzi.
   Geruzaren izena = irteerako fitxategiaren izena (.gpkg gabe).
6. Denbora totala erregistratu.

Erabilera
---------
    python3 vt_reclass_water.py sarrera.gpkg irteera.gpkg [log_fitxategia.log]

    sarrera.gpkg      : sarrerako GPKG fitxategia (existitu behar du)
    irteera.gpkg      : irteerako GPKG fitxategia (existitzen bada, ezabatu egiten da)
    log_fitxategia.log: HAUTAZKOA. Log fitxategia (append moduan irekitzen da).
                        Ematen ez bada, mezuak terminalera soilik joaten dira
                        (terminal interaktiboa bada; ikus log_utils.py).

Scriptaren izena sys.argv[0]-tik hartzen da; beraz, fitxategiaren izena
aldatuz gero ez da kodea aldatu behar.

Beharrezkoak
------------
    Python 3.6+, GeoPandas (<= 0.9, sjoin_nearest gabe), rtree edo pygeos
    (indize espazialerako), eta log_utils.py script honen ondoan.

Oharrak
-------
- Lan egin CRS proiektatu batean (adib. EPSG:25830), distantziak metrotan
  egon daitezen. CRS geografikoa bada, abisu bat idazten da.
- Distantzia 0 bada (poligonoak ukitzen dira), aurkitutako lehena hartzen da.
- Kandidaturik aurkitzen ez duten poligonoak 'water other' gisa geratzen dira.
"""

import os
import sys
import time

import geopandas as gpd

from log_utils import Log

# ----------------------------------------------------------------------
# Konstanteak
# ----------------------------------------------------------------------

# Scriptaren izena, argv-tik: izena aldatuz gero ez da kodea aldatu behar.
SCRIPT_IZENA = os.path.basename(sys.argv[0])

# Birsailkatu beharreko 'type' balioa.
TARGET = "water other"

# Kandidatu gisa onartzen ez diren 'type' balioak. 'water other' ere
# kanpoan dago, xede batek beste xede baten balioa har ez dezan.
EXCLUDE = ("water", "intertidal water", "water other")

# Bilaketa-erradioaren hasierako balioa eta muga (CRS-aren unitateetan).
BILAKETA_HASIERA = 50.0
BILAKETA_MUGA = 50000.0


# ----------------------------------------------------------------------
# Funtzio laguntzaileak
# ----------------------------------------------------------------------

def erabilera():
    """Erabileraren mezua itzuli (scriptaren izena argv-tik)."""
    return "Erabilera: {} sarrera.gpkg irteera.gpkg [log_fitxategia.log]".format(
        SCRIPT_IZENA
    )


def ezabatu_gpkg(bidea):
    """
    GPKG fitxategia ezabatu, baita SQLite-ren fitxategi lagungarriak ere
    (-wal eta -shm), geratu badira. Horrela ez da arrastorik geratzen
    irteera berria idazterakoan.

    :param bidea: ezabatu beharreko GPKG fitxategiaren bidea
    """
    for atzizkia in ("", "-wal", "-shm"):
        if os.path.exists(bidea + atzizkia):
            os.remove(bidea + atzizkia)


def gertuena(geom, sidx, geoms, types,
             d=BILAKETA_HASIERA, dmax=BILAKETA_MUGA):
    """
    Emandako geometriaren gertuen dagoen kandidatuaren 'type' balioa itzuli.

    Algoritmoa:
      1. Geometriaren bounding box-a 'd' distantziaz zabaldu eta indize
         espazialari galdetu zein kandidatu dauden kaxa horren barruan.
      2. Aurkitutako kandidatuen distantzia exaktua kalkulatu.
      3. Distantzia minimoa <= d bada, kandidatu hori da benetan gertuena:
         kaxatik kanpo dagoen edozein kandidatuk d baino urrunago egon
         behar du. Kasu horretan, bere 'type' itzuli.
      4. Bestela (ez dago kandidaturik edo minimoa d baino handiagoa da),
         d bikoiztu eta berriz saiatu, dmax gainditu arte.

    :param geom: xede-geometria (shapely)
    :param sidx: kandidatuen indize espaziala (GeoDataFrame.sindex)
    :param geoms: kandidatuen geometriak (indizearen posizio berean)
    :param types: kandidatuen 'type' balioak (indizearen posizio berean)
    :param d: hasierako bilaketa-erradioa
    :param dmax: bilaketa-erradio maximoa
    :return: 'type' balioa, edo None ez bada kandidaturik aurkitu
    """
    # Geometria hutsa edo faltan: ezin da distantziarik kalkulatu.
    if geom is None or geom.is_empty:
        return None

    minx, miny, maxx, maxy = geom.bounds

    while d <= dmax:
        # Bounding box zabaldua ebakitzen duten kandidatuen posizioak.
        pos = list(sidx.intersection((minx - d, miny - d, maxx + d, maxy + d)))
        if pos:
            # Distantzia exaktua (poligonoen artekoa) kandidatu bakoitzera.
            dists = [geoms[i].distance(geom) for i in pos]
            dmin = min(dists)
            if dmin <= d:
                return types[pos[dists.index(dmin)]]
        d *= 2  # erradioa bikoiztu eta berriz saiatu

    return None


def birsailkatu(gdf, log):
    """
    'water other' poligonoak birsailkatu, GeoDataFrame-a bertan aldatuz.

    :param gdf: sarrerako GeoDataFrame-a ('type' eremua behar du)
    :param log: Log objektua
    :return: (birsailkatuak, kandidaturik gabe geratuak) kopuruak
    """
    # Xedeen maskara: birsailkatu beharreko poligonoak.
    mask = gdf["type"] == TARGET
    n_target = int(mask.sum())

    # Kandidatuak: 'water', 'intertidal water' eta 'water other' ez diren
    # poligonoak (ikus EXCLUDE).
    # Indizea berrezarri behar da, indize espazialaren posizioak (0..n-1)
    # 'geoms' eta 'types' arrayen posizioekin bat etor daitezen.
    cands = gdf.loc[~gdf["type"].isin(EXCLUDE), ["type", "geometry"]]
    cands = cands.reset_index(drop=True)

    log.info("'{}' poligonoak: {} | kandidatuak: {}".format(
        TARGET, n_target, len(cands)))

    # Kasu bereziak: ez dago zer egin.
    if n_target == 0:
        log.abisua("Ez dago birsailkatzeko poligonorik.")
        return 0, 0
    if len(cands) == 0:
        log.abisua("Ez dago kandidaturik; ez da ezer birsailkatuko.")
        return 0, n_target

    # Bilaketa azkartzeko egiturak: geometriak, balioak eta indize espaziala.
    geoms = cands.geometry.values
    types = cands["type"].values
    sidx = cands.sindex

    # Xede bakoitzaren gertuen dagoen kandidatuaren 'type' balioa kalkulatu.
    # Emaitza: Series bat, xedeen indizearekin (None = kandidaturik gabe).
    new_types = gdf.loc[mask, "geometry"].apply(
        lambda g: gertuena(g, sidx, geoms, types)
    )

    # Balio bat aurkitu duten xedeak soilik eguneratu.
    ok = new_types.notna()
    gdf.loc[new_types[ok].index, "type"] = new_types[ok]

    return int(ok.sum()), int((~ok).sum())


def main(log, sarrera, irteera):
    """
    Prozesu nagusia: irakurri, birsailkatu eta idatzi.

    :param log: Log objektua
    :param sarrera: sarrerako GPKG-aren bidea
    :param irteera: irteerako GPKG-aren bidea
    :return: irteera-kodea (0 = ondo, 1 = errorea)
    """
    # --- 1. Egiaztapenak -------------------------------------------------
    if not os.path.isfile(sarrera):
        log.errorea("Sarrerako GPKG fitxategia ez dago: {}".format(sarrera))
        return 1

    # Sarrera eta irteera berdinak badira, irteera ezabatzean sarrera
    # galduko litzateke.
    if os.path.abspath(sarrera) == os.path.abspath(irteera):
        log.errorea("Sarrera eta irteera fitxategi bera dira; ez da ezer egingo.")
        return 1

    # Denbora kontagailua hasi.
    t0 = time.time()

    # --- 2. Sarrera irakurri ---------------------------------------------
    # Geruza bat baino gehiago badago, lehenengoa irakurtzen da. Aldatzeko:
    # gpd.read_file(sarrera, layer="geruzaren_izena")
    log.info("Sarrera irakurtzen: {}".format(sarrera))
    gdf = gpd.read_file(sarrera)
    log.info("{} poligono irakurri dira".format(len(gdf)))

    if "type" not in gdf.columns:
        log.errorea("Sarrerak ez du 'type' eremurik.")
        return 1

    # CRS geografikoa bada, distantziak graduetan egongo lirateke.
    if gdf.crs is not None and getattr(gdf.crs, "is_geographic", False):
        log.abisua("CRS geografikoa da; distantziak graduetan kalkulatuko "
                   "dira. Hobe da CRS proiektatu batean lan egitea.")

    # --- 3. Birsailkapena ------------------------------------------------
    birsailkatuak, geratuak = birsailkatu(gdf, log)
    log.info("Birsailkatuak: {} | kandidaturik gabe geratuak: {}".format(
        birsailkatuak, geratuak))

    # --- 4. Irteera idatzi -----------------------------------------------
    # Irteerako fitxategia existitzen bada, ezabatu.
    if os.path.exists(irteera):
        log.info("Irteerako fitxategia existitzen da, ezabatzen: {}".format(
            irteera))
        ezabatu_gpkg(irteera)

    # Geruzaren izena = fitxategiaren izena, .gpkg atzizkirik gabe.
    geruza = os.path.splitext(os.path.basename(irteera))[0]
    log.info("Irteera idazten: {} (geruza: {})".format(irteera, geruza))
    gdf.to_file(irteera, layer=geruza, driver="GPKG")

    # --- 5. Denbora totala -----------------------------------------------
    dt = time.time() - t0
    log.info("Denbora totala: {:d}m {:04.1f}s".format(int(dt // 60), dt % 60))
    return 0


# ----------------------------------------------------------------------
# Sarrera-puntua
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Argumentuak egiaztatu Log sortu aurretik: log fitxategia (hautazkoa)
    # hirugarren argumentuan baitator. Errorea stderr-era doa, oraindik ez
    # dagoelako log-ik. Onartzen dira 2 edo 3 parametro (scriptaren izena
    # kenduta), hau da, sys.argv-n 3 edo 4 elementu.
    if len(sys.argv) not in (3, 4):
        print("Parametro kopuru okerra. " + erabilera(), file=sys.stderr)
        sys.exit(1)

    SARRERA, IRTEERA = sys.argv[1], sys.argv[2]

    # Log fitxategia hautazkoa da: ematen ez bada, None pasatzen zaio Log-i
    # eta mezuak terminalera soilik joango dira.
    LOG_BIDEA = sys.argv[3] if len(sys.argv) == 4 else None

    # Log fitxategiaren direktorioa sortu, ez badago.
    if LOG_BIDEA:
        os.makedirs(os.path.dirname(os.path.abspath(LOG_BIDEA)), exist_ok=True)

    # 'with' erabiliz, Hasiera/Bukaera mezuak automatikoki idazten dira, baita
    # salbuespenik gertatuz gero ere. sys.exit 'with'-etik kanpo dago,
    # SystemExit salbuespen gisa erregistratu ez dadin.
    with Log(LOG_BIDEA, SCRIPT_IZENA, sys.argv[1:]) as log:
        KODEA = main(log, SARRERA, IRTEERA)
    sys.exit(KODEA)
