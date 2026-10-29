#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vt_moztu2.py
============

GPKG fitxategi bat beste GPKG fitxategi baten poligonoekin mozten du
(QGISeko «Moztu» / «Clip» tresnaren baliokidea).

Funtzionamendua
---------------
1. Sarrerako parametroak egiaztatzen ditu (jatorrizko eta mozteko fitxategiak
   existitu behar dute).
2. Mozteko GPKGko geometria guztiak batu egiten dira (unary_union), QGISek
   egiten duen bezala. Mozteko geruzaren atributuak ez dira kontuan hartzen.
3. Jatorrizko GPKGko elementu bakoitza mozteko eremuarekin ebakitzen da:
     - Guztiz kanpoan geratzen dena baztertu egiten da.
     - Guztiz barruan geratzen dena aldatu gabe mantentzen da.
     - Partzialki barruan geratzen dena ebaki egiten da.
   Jatorrizko elementuen atributu guztiak mantentzen dira.
4. Emaitzaren geometria-dimentsioa jatorrizkoarena izaten da (poligonoa ->
   poligonoak, lerroa -> lerroak, puntua -> puntuak); ebaketan sortutako
   beste dimentsioko zatiak (adib. bi poligonoren ukipen-lerroa) baztertu
   egiten dira.
5. Helburuko GPKG fitxategia idazten da. Aldez aurretik existitzen bada,
   ezabatu egiten da. Taularen (geruzaren) izena helburuko fitxategiaren
   izena da, «.gpkg» atzizkirik gabe.
6. Prozesuaren iraupena MM:SS formatuan erakusten da.

Erabilera
---------
    <script_izena> jatorria.gpkg moztekoa.gpkg helburua.gpkg [log_fitxategia]

Parametroak
-----------
    1. jatorria.gpkg   Moztu beharreko GPKG fitxategia (existitu behar du).
    2. moztekoa.gpkg   Mozteko erabiliko den GPKG fitxategia (existitu behar
                       du). Fitxategi honen barruan dagoena moztuko da
                       jatorrizkotik.
    3. helburua.gpkg   Sortuko den GPKG fitxategia (badago, ezabatu egiten da).
    4. log_fitxategia  (Hautazkoa) Log mezuak gordetzeko fitxategia. Ez da
                       ezabatzen, mezuak ondoan gehitzen dira. Eman ezean,
                       mezuak terminalera idazten dira.

Irteera-kodeak
--------------
    0  Ondo
    1  Parametro okerrak edo fitxategiren bat falta da
    2  Errorea prozesuan zehar

Oharrak
-------
    - Python 3.6 bateragarria (GeoPandas + Shapely + Fiona).
    - Bi fitxategiek CRS desberdina badute, mozteko geruza jatorrizkoaren
      CRSra birproiektatzen da.
    - GPKG batek geruza bat baino gehiago badauka, lehenengoa erabiltzen da
      (log-ean jakinarazten da).
    - log_utils.py modulua beharrezkoa da (script honen ondoan). Hasiera eta
      Bukaera mezuak automatikoki idazten ditu; terminalera mezuak
      sys.stdout.isatty() True bada soilik idazten dira.
"""

import os
import sys
import time

# log_utils lehenengo inportatzen da: bere abisu-iragazkiek (FutureWarning etab.)
# geopandas, fiona eta abarrek sortutako abisuei eragin diezaieten.
from log_utils import Log

import fiona
import geopandas as gpd
from shapely.geometry import MultiLineString, MultiPoint, MultiPolygon


# ---------------------------------------------------------------------------
# Log-erako laguntzaileak
# ---------------------------------------------------------------------------
# log_utils.Log klasearen erabilera leku bakar honetan dago kontzentratuta
# (metodoak: info, abisua, errorea).

LOG = None  # main()-en hasieratzen da (Log objektua)


def log_info(mezua):
    LOG.info(mezua)


def log_warning(mezua):
    LOG.abisua(mezua)


def log_error(mezua):
    LOG.errorea(mezua)


# ---------------------------------------------------------------------------
# Denbora
# ---------------------------------------------------------------------------

def formatu_denbora(segundoak):
    """Segundoak MM:SS formatuko testu bihurtzen ditu (adib. 75 -> '01:15').

    Ordu bat baino gehiago irauten badu, minutuak 59tik gora joango dira
    (adib. 3725 s -> '62:05').
    """
    segundoak = int(round(segundoak))
    minutuak, seg = divmod(segundoak, 60)
    return "{:02d}:{:02d}".format(minutuak, seg)


# ---------------------------------------------------------------------------
# Geometria-laguntzaileak
# ---------------------------------------------------------------------------

def geometria_dimentsioa(geom):
    """Geometriaren dimentsioa itzultzen du: 0 puntua, 1 lerroa, 2 poligonoa.

    GeometryCollection-etan dimentsio altuena hartzen da.
    """
    gt = geom.geom_type
    if gt in ("Point", "MultiPoint"):
        return 0
    if gt in ("LineString", "LinearRing", "MultiLineString"):
        return 1
    if gt in ("Polygon", "MultiPolygon"):
        return 2
    # GeometryCollection
    dimentsioak = [geometria_dimentsioa(g) for g in geom.geoms if not g.is_empty]
    return max(dimentsioak) if dimentsioak else -1


def atera_dimentsioko_zatiak(geom, dim):
    """Geometriatik 'dim' dimentsioko zatiak bakarrik atera eta batu egiten ditu.

    Ebaketak GeometryCollection bat sor dezake (adib. poligono bat + lerro
    bat ukipen-puntuetan). QGISek bezala, jatorrizkoaren dimentsio bereko
    zatiak bakarrik mantentzen dira. Zatirik ez badago, None itzultzen du.
    """
    if geom is None or geom.is_empty:
        return None

    if geometria_dimentsioa(geom) == dim and geom.geom_type != "GeometryCollection":
        return geom

    # Zatiak bildu (GeometryCollection edo dimentsio nahasiak)
    zatiak = []

    def bildu(g):
        if g.is_empty:
            return
        if g.geom_type == "GeometryCollection":
            for azpi in g.geoms:
                bildu(azpi)
        elif g.geom_type.startswith("Multi"):
            for azpi in g.geoms:
                bildu(azpi)
        else:
            if geometria_dimentsioa(g) == dim:
                zatiak.append(g)

    bildu(geom)

    if not zatiak:
        return None
    if len(zatiak) == 1:
        return zatiak[0]
    if dim == 2:
        return MultiPolygon(zatiak)
    if dim == 1:
        return MultiLineString(zatiak)
    return MultiPoint(zatiak)


# ---------------------------------------------------------------------------
# Prozesu nagusia
# ---------------------------------------------------------------------------

def lehen_geruza(fitxategia):
    """GPKG baten lehenengo geruzaren izena itzultzen du (geruza gehiago
    badaude, abisua idazten da log-ean)."""
    geruzak = fiona.listlayers(fitxategia)
    if not geruzak:
        raise ValueError("Ez dago geruzarik fitxategian: {}".format(fitxategia))
    if len(geruzak) > 1:
        log_warning("{} fitxategiak {} geruza ditu; lehenengoa erabiliko da: '{}'"
                    .format(os.path.basename(fitxategia), len(geruzak), geruzak[0]))
    return geruzak[0]


def moztu(jatorria, moztekoa, helburua):
    """Mozketa burutzen du eta emaitza helburuko GPKGan idazten du."""

    # --- Geruzak irakurri --------------------------------------------------
    geruza_jat = lehen_geruza(jatorria)
    geruza_moz = lehen_geruza(moztekoa)

    log_info("Jatorrizkoa irakurtzen: {} (geruza: {})".format(jatorria, geruza_jat))
    gdf = gpd.read_file(jatorria, layer=geruza_jat)
    log_info("  {} elementu irakurri dira".format(len(gdf)))

    log_info("Mozteko geruza irakurtzen: {} (geruza: {})".format(moztekoa, geruza_moz))
    moz = gpd.read_file(moztekoa, layer=geruza_moz)
    log_info("  {} elementu irakurri dira".format(len(moz)))

    # --- CRS egiaztapena -----------------------------------------------------
    if gdf.crs != moz.crs:
        log_warning("CRS desberdinak (jatorria: {}, moztekoa: {}); mozteko geruza "
                    "jatorrizkoaren CRSra birproiektatzen".format(gdf.crs, moz.crs))
        moz = moz.to_crs(gdf.crs)

    # --- Mozteko geometria bateratua -----------------------------------------
    # Mozteko geruzako geometria guztiak batu egiten dira eremu bakar batean.
    log_info("Mozteko geometriak batzen...")
    moz_geoms = moz.geometry[moz.geometry.notnull() & ~moz.geometry.is_empty]
    if len(moz_geoms) == 0:
        raise ValueError("Mozteko geruzak ez dauka geometria baliodunik")
    mozteko_eremua = moz_geoms.buffer(0).unary_union  # buffer(0): geometria baliogabeak konpontzeko

    # Geometria prestatuak ebaketa-probak azkartzeko
    from shapely.prepared import prep
    prestatua = prep(mozteko_eremua)

    # --- Prefiltroa: bounding box-aren bidez ---------------------------------
    # Mozteko eremuaren MBRarekin ebakitzen ez diren elementuak azkar baztertzen dira.
    minx, miny, maxx, maxy = mozteko_eremua.bounds
    kandidatuak = gdf.cx[minx:maxx, miny:maxy]
    log_info("Prefiltroaren ondoren {} elementu geratzen dira aztertzeko (MBR bidez)"
             .format(len(kandidatuak)))

    # --- Elementuz elementuko mozketa ------------------------------------------
    log_info("Mozketa egiten...")
    geometriak = []
    indizeak = []
    guztiz_barruan = 0
    ebakiak = 0
    baztertuak = 0

    guztira = len(kandidatuak)
    urratsa = max(guztira // 10, 1)

    for n, (idx, geom) in enumerate(zip(kandidatuak.index, kandidatuak.geometry), 1):
        if geom is None or geom.is_empty:
            baztertuak += 1
        elif not prestatua.intersects(geom):
            baztertuak += 1
        elif prestatua.contains(geom):
            # Guztiz barruan: aldatu gabe
            geometriak.append(geom)
            indizeak.append(idx)
            guztiz_barruan += 1
        else:
            # Partzialki barruan: ebaketa
            dim = geometria_dimentsioa(geom)
            ebaketa = geom.intersection(mozteko_eremua)
            ebaketa = atera_dimentsioko_zatiak(ebaketa, dim)
            if ebaketa is None:
                baztertuak += 1
            else:
                geometriak.append(ebaketa)
                indizeak.append(idx)
                ebakiak += 1

        if n % urratsa == 0:
            log_info("  {}/{} aztertuta".format(n, guztira))

    log_info("Emaitza: {} guztiz barruan, {} ebaki, {} baztertu (kanpoan edo hutsik)"
             .format(guztiz_barruan, ebakiak, baztertuak
                     + (len(gdf) - guztira)))

    if not geometriak:
        raise ValueError("Mozketaren emaitza hutsik dago: ez dago elementurik "
                         "mozteko eremuaren barruan")

    # --- Emaitza GeoDataFrame gisa ---------------------------------------------
    # Jatorrizko atributuak mantentzen dira; geometria ebakitakoa da.
    emaitza = gdf.loc[indizeak].copy()
    emaitza["geometry"] = geometriak
    emaitza = gpd.GeoDataFrame(emaitza, geometry="geometry", crs=gdf.crs)
    emaitza = emaitza.reset_index(drop=True)

    # --- Idazketa --------------------------------------------------------------
    # Geruzaren izena = helburuko fitxategiaren izena, «.gpkg» atzizkirik gabe.
    geruza_izena = os.path.splitext(os.path.basename(helburua))[0]
    log_info("Emaitza idazten: {} (geruza: {}, {} elementu)"
             .format(helburua, geruza_izena, len(emaitza)))
    emaitza.to_file(helburua, layer=geruza_izena, driver="GPKG")


def main():
    global LOG

    script_izena = os.path.basename(sys.argv[0])
    erabilera = ("Erabilera: {} jatorria.gpkg moztekoa.gpkg helburua.gpkg "
                 "[log_fitxategia]".format(script_izena))

    # --- Parametroak -----------------------------------------------------------
    if len(sys.argv) not in (4, 5):
        print(erabilera)
        return 1

    jatorria = sys.argv[1]
    moztekoa = sys.argv[2]
    helburua = sys.argv[3]
    log_fitxategia = sys.argv[4] if len(sys.argv) == 5 else None

    hasiera = time.time()

    # Log sistema: fitxategia ez da ezabatzen (append modua); eman ezean
    # terminalera bakarrik. 'with' erabiliz, Hasiera/Bukaera mezuak eta
    # salbuespenen erregistroa automatikoki egiten dira.
    with Log(log_fitxategia, script_izena, sys.argv[1:]) as log:
        LOG = log

        # --- Egiaztapenak ------------------------------------------------------
        if not os.path.isfile(jatorria):
            log_error("Jatorrizko fitxategia ez dago: {}".format(jatorria))
            return 1
        if not os.path.isfile(moztekoa):
            log_error("Mozteko fitxategia ez dago: {}".format(moztekoa))
            return 1

        # Helburua aldez aurretik badago, ezabatu
        if os.path.exists(helburua):
            log_info("Helburuko fitxategia lehendik ere badago, ezabatzen: {}"
                     .format(helburua))
            os.remove(helburua)

        # --- Prozesua ----------------------------------------------------------
        try:
            moztu(jatorria, moztekoa, helburua)
        except Exception as e:
            log_error("Errorea prozesuan: {}".format(e))
            log_info("Iraupena: {}".format(formatu_denbora(time.time() - hasiera)))
            return 2

        log_info("Prozesua amaitu da. Iraupena: {}"
                 .format(formatu_denbora(time.time() - hasiera)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
