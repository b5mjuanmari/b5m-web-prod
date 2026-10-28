#!/usr/bin/env python3
"""
GPKG fitxategi baten disolbatzea eremu baten arabera (QGISen "Disolbatu" /
native:dissolve prozesuaren portaera berarekin).

Erabilera:
    vt_disolbatu4.py JATORRIA.gpkg HELBURUA.gpkg EREMUA [LOG_FITXATEGIA]

Sarrera-parametroak:
    1. JATORRIA   Jatorrizko GPKG fitxategia. Existitu behar du.
    2. HELBURUA   Helburuko GPKG fitxategia. Aldez aurretik badago, ezabatu
                  egiten da (baita bere -wal / -shm fitxategi lagungarriak ere).
    3. EREMUA     Disolbatzeko erabiliko den eremuaren izena. Jatorrizko
                  geruzan existitu behar du.
    4. LOG        (Hautazkoa) log fitxategiaren bidea. Ez da ezabatzen,
                  mezuak amaieran gehitzen dira (append). Ematen ez bada,
                  mezuak terminalera soilik joaten dira (log_utils.Log-en
                  arabera, terminala interaktiboa bada).

QGISen portaerarekin bat datozen xehetasunak:
    - EREMUA-ren balio berdina duten geometria guztiak geometria bakar batean
      batzen dira (unary union). Muga komunak desagertzen dira.
    - Emaitzaren atributuak taldeko lehen objektuarenak dira (QGISek bezala).
    - Balio nulua (NULL) duten objektuek talde bat osatzen dute elkarren artean.
    - Emaitza geometria anizkoitza (Multi*) da, QGISen irteerako geruzak
      bezala; talde bateko emaitza banatuta (disjuntua) badago ere, objektu
      bakar gisa gordetzen da.
    - CRS jatorrizkoaren berdina da.
    - Emaitzako objektuen ordena: talde bakoitzaren lehen agerpenarena.

Oharrak:
    - GPKG fitxategiak geruza bat baino gehiago baditu, lehena erabiltzen da
      (abisu bat idazten da logean). Irteerako geruzak izen bera du.
    - Python 3.6rekin bateragarria (GeoPandas, Shapely, Fiona).

Irteera-kodeak:
    0 = ondo, 1 = errorea (fitxategia/eremua ez dago, irakurketa/idazketa
    errorea, etab.), 2 = argumentu okerrak (argparse).

Script-aren izena sys.argv[0]-tik hartzen da; beraz, fitxategiari izena
aldatuz gero ez da kodea aldatu behar.
"""

import os
import sys
import argparse

import fiona
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
from shapely.geometry import (
    MultiPoint,
    MultiLineString,
    MultiPolygon,
    Point,
    LineString,
    Polygon,
)

from log_utils import Log


# Bit-bit Polygon -> MultiPolygon bihurketa egiteko taula
_MULTI_MOTAK = {
    Point: MultiPoint,
    LineString: MultiLineString,
    Polygon: MultiPolygon,
}


# ----------------------------------------------------------------------
# Laguntza-funtzioak
# ----------------------------------------------------------------------
def anizkoitza_egin(geom):
    """
    Geometria sinplea bada, anizkoitz bihurtzen du (Polygon -> MultiPolygon,
    etab.). Jada anizkoitza bada (edo beste mota bat bada), ez du ezer egiten.

    :param geom: shapely geometria
    :return: shapely geometria (Multi* motakoa, ahal bada)
    """
    for sinplea, anizkoitza in _MULTI_MOTAK.items():
        if type(geom) is sinplea:
            return anizkoitza([geom])
    return geom


def geometriak_batu(geometriak, log, eremu_balioa):
    """
    Geometria-zerrenda bat geometria bakar batean batzen du (unary union).
    Geometria baliogabeak badaude eta batzeak huts egiten badu, buffer(0)
    bidez konpontzen saiatzen da.

    :param geometriak: shapely geometrien zerrenda (None gabe)
    :param log: Log objektua
    :param eremu_balioa: taldearen balioa (abisu-mezuetarako)
    :return: batutako geometria
    """
    try:
        return unary_union(geometriak)
    except Exception as e:  # shapely TopologicalError, GEOSException...
        log.abisua(
            f"'{eremu_balioa}' taldeko geometriak batzean errorea ({e}); "
            f"buffer(0) bidez konpontzen saiatzen..."
        )
        konponduta = [g if g.is_valid else g.buffer(0) for g in geometriak]
        return unary_union(konponduta)


def disolbatu(gdf, eremua, log):
    """
    QGISen native:dissolve-ren pareko disolbatzea.

    :param gdf: GeoDataFrame jatorrizkoa
    :param eremua: disolbatzeko eremuaren izena
    :param log: Log objektua
    :return: GeoDataFrame disolbatua (taldeko lehen objektuaren atributuekin)
    """
    geom_zutabea = gdf.geometry.name

    # Taldeen identifikatzailea: pd.factorize-k NULL balioei -1 esleitzen die,
    # beraz NULL guztiak talde bakar batean geratzen dira (QGISen moduan).
    # (groupby-k NaN balioak baztertu egiten dituenez, ezin da zuzenean
    # eremuaren gainean egin.)
    kodeak, _ = pd.factorize(gdf[eremua])

    emaitza_errenkadak = []
    emaitza_geometriak = []

    # Taldeak lehen agerpenaren ordenan prozesatzeko
    taldeak = pd.Series(range(len(gdf))).groupby(kodeak).apply(list)
    taldeak = sorted(taldeak.tolist(), key=lambda posizioak: posizioak[0])

    for posizioak in taldeak:
        lehena = gdf.iloc[posizioak[0]]
        geometriak = [
            g for g in gdf.geometry.iloc[posizioak]
            if g is not None and not g.is_empty
        ]
        if not geometriak:
            log.abisua(
                f"'{lehena[eremua]}' taldeak ez du geometria baliozkorik; "
                f"baztertu egin da."
            )
            continue

        geom = geometriak_batu(geometriak, log, lehena[eremua])
        emaitza_errenkadak.append(lehena.drop(labels=[geom_zutabea]))
        emaitza_geometriak.append(anizkoitza_egin(geom))

    atributuak = pd.DataFrame(emaitza_errenkadak).reset_index(drop=True)
    # Atributu-zutabeen ordena eta motak ahalik eta gehien mantentzen dira
    for zutabea in atributuak.columns:
        try:
            atributuak[zutabea] = atributuak[zutabea].astype(gdf[zutabea].dtype)
        except (ValueError, TypeError):
            pass  # NULL balioak daudenean int motak huts egin dezake; utzi

    return gpd.GeoDataFrame(
        atributuak,
        geometry=gpd.GeoSeries(emaitza_geometriak, crs=gdf.crs),
        crs=gdf.crs,
    )


def helburua_ezabatu(bidea, log):
    """
    Helburuko GPKG fitxategia ezabatzen du existitzen bada, baita SQLite-ren
    fitxategi lagungarriak (-wal, -shm) ere.
    """
    for atzizkia in ("", "-wal", "-shm"):
        fitxategia = bidea + atzizkia
        if os.path.exists(fitxategia):
            os.remove(fitxategia)
            log.info(f"Lehendik zegoen fitxategia ezabatu da: {fitxategia}")


# ----------------------------------------------------------------------
# Programa nagusia
# ----------------------------------------------------------------------
def prozesatu(args, log):
    """
    Disolbatze prozesu osoa exekutatzen du.

    :param args: argparse-ren emaitza
    :param log: Log objektua
    :return: irteera-kodea (0 = ondo, 1 = errorea)
    """
    jatorria = args.jatorria
    helburua = args.helburua
    eremua = args.eremua

    # 1. Jatorrizko fitxategia egiaztatu
    if not os.path.isfile(jatorria):
        log.errorea(f"Jatorrizko fitxategia ez da existitzen: {jatorria}")
        return 1

    # Jatorria eta helburua berdinak badira, jatorria ezabatuko genuke
    if os.path.abspath(jatorria) == os.path.abspath(helburua):
        log.errorea("Jatorrizko eta helburuko fitxategiak berdinak dira.")
        return 1

    # 2. Geruzak eta eremua egiaztatu (datuak kargatu aurretik)
    try:
        geruzak = fiona.listlayers(jatorria)
    except Exception as e:
        log.errorea(f"Ezin izan da GPKG fitxategia irakurri: {e}")
        return 1

    if not geruzak:
        log.errorea("GPKG fitxategiak ez du geruzarik.")
        return 1

    geruza = geruzak[0]
    if len(geruzak) > 1:
        log.abisua(
            f"GPKG fitxategiak {len(geruzak)} geruza ditu ({', '.join(geruzak)}); "
            f"lehena erabiliko da: {geruza}"
        )

    try:
        with fiona.open(jatorria, layer=geruza) as src:
            eremuak = list(src.schema["properties"].keys())
    except Exception as e:
        log.errorea(f"Ezin izan da '{geruza}' geruzaren eskema irakurri: {e}")
        return 1

    if eremua not in eremuak:
        log.errorea(
            f"'{eremua}' eremua ez dago '{geruza}' geruzan. "
            f"Eremu erabilgarriak: {', '.join(eremuak)}"
        )
        return 1

    # 3. Datuak irakurri
    log.info(f"Irakurtzen: {jatorria} (geruza: {geruza})")
    try:
        gdf = gpd.read_file(jatorria, layer=geruza)
    except Exception as e:
        log.errorea(f"Errorea datuak irakurtzean: {e}")
        return 1
    log.info(f"{len(gdf)} objektu irakurri dira. CRS: {gdf.crs}")

    # 4. Disolbatu
    log.info(f"Disolbatzen '{eremua}' eremuaren arabera...")
    try:
        emaitza = disolbatu(gdf, eremua, log)
    except Exception as e:
        log.errorea(f"Errorea disolbatzean: {type(e).__name__}: {e}")
        return 1
    log.info(f"Disolbatzea amaituta: {len(emaitza)} objektu emaitzan.")

    # 5. Helburua ezabatu (badago) eta idatzi
    try:
        helburua_ezabatu(helburua, log)
        emaitza.to_file(helburua, driver="GPKG", layer=geruza)
    except Exception as e:
        log.errorea(f"Errorea emaitza idaztean: {e}")
        return 1
    log.info(f"Emaitza idatzi da: {helburua} (geruza: {geruza})")

    return 0


def main():
    # Script-aren izena argv-tik: izena aldatuz gero ez da kodea aldatu behar
    script_izena = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(
        prog=script_izena,
        description="GPKG fitxategia disolbatzen du eremu baten arabera "
                    "(QGISen 'Disolbatu' prozesuaren pareko).",
    )
    parser.add_argument("jatorria", help="Jatorrizko GPKG fitxategia")
    parser.add_argument(
        "helburua",
        help="Helburuko GPKG fitxategia (existitzen bada, ezabatu egiten da)",
    )
    parser.add_argument("eremua", help="Disolbatzeko eremuaren izena")
    parser.add_argument(
        "log",
        nargs="?",
        default=None,
        help="Log fitxategia (hautazkoa; ez da ezabatzen, append modua)",
    )
    args = parser.parse_args()

    # Log-a hasieratu: Hasiera/Bukaera mezuak automatikoki idazten dira.
    # 'with' erabiliz, salbuespenik gertatuz gero ere Bukaera mezua idazten da.
    kodea = 1
    with Log(args.log, script_izena, sys.argv[1:]) as log:
        kodea = prozesatu(args, log)
    return kodea


if __name__ == "__main__":
    sys.exit(main())
