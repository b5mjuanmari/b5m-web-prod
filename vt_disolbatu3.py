#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPKG fitxategi baten poligonoak 'type' eremuaren arabera disolbatzen ditu.

Erabilera:
    python3 <script_izena> sarrera.gpkg irteera.gpkg [log_fitxategia]

    log_fitxategia aukerakoa da:
      - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
      - ez bada ematen: mezuak terminalera soilik (TTY bada)

Oharrak:
  - Irteerako GPKG-an 'type' eremua bakarrik gordetzen da (gainerako
    atributuak galtzen dira disolbatzean). Irteerako geruzaren izena
    irteera-fitxategiaren izena da (luzapenik gabe).
  - Poligono ez diren geometriak eta eraztun baliogabeak dituzten
    geometriak baztertu egiten dira (kopuruak logean).
  - 'type' hutsik (NULL) duten poligonoak ez dira galtzen: talde
    independente bat osatzen dute eta irteeran NULL balioarekin geratzen dira.

Algoritmoa ("closing" teselatua eta paraleloa):
  1. Poligonoak mota + sareta-tesela (zentroidearen arabera) banatzen dira.
  2. Tesela bakoitzean: buffer(+EPS) eta unary_union (prozesu paraleloetan).
  3. Teselen emaitzak mailaz maila batzen dira (2x2 teselak batera),
     paraleloan, mota bakoitzeko geometria bakar bat geratu arte.
  4. Azkenik buffer(-EPS) egiten da poligono bakoitzari bereizita
     (paraleloan). Txikitzea azkenera arte atzeratzen da, tesela-mugetan
     zirrikiturik ez sortzeko.
"""

import argparse
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

from log_utils import Log

FIELD = "type"  # Disolbatzeko eremua

# Batzeko tolerantzia (geometriaren unitatean, adib. metrotan EPSG:25830-ean).
# "Closing" eragiketa: buffer(+EPS) -> batu -> buffer(-EPS). 2*EPS arteko
# zirrikitu mikroskopikoak ixten dira (eta 2*EPS baino txikiagoak diren
# zuloak betetzen dira). Balio txikia izan behar du, forma ez aldatzeko.
EPS = 0.01

# Buffer-aren parametroak: mitre-a erabiliz erpin kopurua ia konstante
# geratzen da (arku biribilduekin baino askoz azkarragoa).
BUFFER_KW = dict(join_style=2, mitre_limit=2.0)

# Tesela-tamaina (metrotan). Dentsitatea oso irregularra bada, 2000-3000 probatu.
TESELA = 5000.0

# Poligono erraldoiak (erpin kopurua > UMBRALA_ERPINAK) ez dira zuzenean
# txikitzen; kanpo-eraztuna eta zuloak bereizita tratatzen dira (ikus
# txikitu_handia). ZULO_LOTEA = zulo kopurua lan bakoitzeko.
UMBRALA_ERPINAK = 300000
ZULO_LOTEA = 2000

# Prozesu kopurua (None = CPU guztiak).
PROZESUAK = None

# 'type' NULL duten erregistroentzako barne-balioa (pandas zaharretan
# groupby-k NULL-ak baztertzen baititu).
NULL_BALIOA = "\x00NULL"

# Prozesu-multzoko (fork) geometria-zerrenda partekatua: Pool sortu aurretik
# esleitzen da, eta umeek kopiatu gabe ikusten dute (pickle-rik gabe).
_GEOMS = []


# ---------------------------------------------------------------------------
# Argumentuak eta egiaztapenak
# ---------------------------------------------------------------------------

def parseatu_argumentuak():
    # argparse-k berak hartzen du script-aren izena sys.argv[0]-tik
    # 'usage' mezuetarako, beraz script-a berrizendatuz gero ez da
    # kodea aldatu behar.
    parser = argparse.ArgumentParser(
        description="GPKG baten poligonoak 'type' eremuaren arabera disolbatu."
    )
    parser.add_argument("sarrera_gpkg", help="Sarrerako GPKG fitxategiaren bidea")
    parser.add_argument("irteera_gpkg", help="Irteerako GPKG fitxategiaren bidea")
    parser.add_argument(
        "log_fitxategia",
        nargs="?",
        default=None,
        help="(aukerakoa) log fitxategiaren bidea. Ez bada ematen, "
             "mezuak terminalera soilik joango dira (TTY bada).",
    )
    return parser.parse_args()


def egiaztatu_sarrera(bidea, log):
    if not os.path.isfile(bidea):
        log.errorea(
            "Sarrerako fitxategia ez da existitzen: {}".format(bidea)
        )
        sys.exit(1)


def egiaztatu_bideak(sarrera, irteera, log):
    if os.path.realpath(sarrera) == os.path.realpath(irteera):
        log.errorea("Sarrera eta irteera fitxategi bera dira: {}".format(sarrera))
        sys.exit(1)


def ezabatu_gpkg(bidea, log=None):
    """GPKG fitxategia eta haren -wal / -shm / -journal laguntzaileak ezabatu."""
    ezabatuta = False
    for atzizkia in ("", "-wal", "-shm", "-journal"):
        f = bidea + atzizkia
        if os.path.exists(f):
            os.remove(f)
            ezabatuta = True
    if ezabatuta and log is not None:
        log.info("Aurretik zegoen fitxategia ezabatu da: {}".format(bidea))


# ---------------------------------------------------------------------------
# Irakurketa
# ---------------------------------------------------------------------------

def garbitu_geometria(geom):
    """
    Geometria (GeoJSON motakoa) jaso eta baliogabeak diren eraztunak
    kentzen ditu (4 koordenatu-bikote baino gutxiago dituztenak).

    Kanpoko eraztuna (lehena) baliogabea bada, poligono/azpi-poligono osoa
    baztertzen da (EZ da barne-zulo bat kanpoko eraztun bihurtzen).
    Emaitzarik ez badago, None itzultzen da. Poligono ez diren geometriak
    ere None itzultzen dute.
    """
    mota = geom["type"]
    koordenatuak = geom["coordinates"]

    if mota == "Polygon":
        if not koordenatuak or len(koordenatuak[0]) < 4:
            return None
        return {
            "type": "Polygon",
            "coordinates": [e for e in koordenatuak if len(e) >= 4],
        }

    if mota == "MultiPolygon":
        poligonoak = [
            [e for e in p if len(e) >= 4]
            for p in koordenatuak
            if p and len(p[0]) >= 4
        ]
        if not poligonoak:
            return None
        return {"type": "MultiPolygon", "coordinates": poligonoak}

    return None


def irakurri_gpkg(bidea, log):
    """
    GPKG fitxategia fiona bidez erregistroz erregistro irakurri, geometria
    bakoitza garbitu eta baliogabeak (konponezinak) edo poligonalak ez diren
    erregistroak baztertu, gpd.read_file()-k egingo lukeen bezala guztiz
    huts egin beharrean.
    """
    erregistroak = []
    geometria_hutsa = 0
    ez_poligonala = 0
    baliogabea = 0

    with fiona.open(bidea) as jatorria:
        crs = jatorria.crs
        for erregistroa in jatorria:
            geom = erregistroa["geometry"]
            if geom is None:
                geometria_hutsa += 1
                continue

            if geom["type"] not in ("Polygon", "MultiPolygon"):
                ez_poligonala += 1
                continue

            geom_garbia = garbitu_geometria(geom)
            if geom_garbia is None:
                baliogabea += 1
                continue

            try:
                geometria = shape(geom_garbia)
            except Exception:
                baliogabea += 1
                continue

            erregistro_berria = dict(erregistroa["properties"])
            erregistro_berria["geometry"] = geometria
            erregistroak.append(erregistro_berria)

    log.info("{} erregistro irakurri dira (baliozkoak)".format(len(erregistroak)))
    if geometria_hutsa:
        log.abisua("{} erregistro baztertu dira geometriarik gabe".format(geometria_hutsa))
    if ez_poligonala:
        log.abisua("{} erregistro baztertu dira poligonoak ez direlako".format(ez_poligonala))
    if baliogabea:
        log.abisua("{} erregistro baztertu dira geometria baliogabea zutelako".format(baliogabea))

    if not erregistroak:
        return None

    return gpd.GeoDataFrame(erregistroak, crs=crs)


# ---------------------------------------------------------------------------
# Disolbatzea (paraleloa)
# ---------------------------------------------------------------------------

def _poligonoak(geom):
    """Geometria batetik Polygon ez-hutsak atera (Multi*/Collection barne)."""
    if geom is None or geom.is_empty:
        return []
    zatiak = geom.geoms if hasattr(geom, "geoms") else [geom]
    emaitza = []
    for p in zatiak:
        if hasattr(p, "geoms"):  # habiaratutako kolekzioa
            emaitza.extend(_poligonoak(p))
        elif p.geom_type == "Polygon" and not p.is_empty:
            emaitza.append(p)
    return emaitza


def _handitu_batu(lana):
    """1. fasea: tesela bateko poligonoak handitu eta batu."""
    gakoa, indizeak = lana
    handituak = [_GEOMS[i].buffer(EPS, **BUFFER_KW) for i in indizeak]
    return gakoa, unary_union(handituak)


def _erpin_kop(geom):
    """Geometriaren erpin kopurua (kanpo-eraztunak eta zuloak barne)."""
    return sum(
        len(p.exterior.coords) + sum(len(i.coords) for i in p.interiors)
        for p in _poligonoak(geom)
    )


def _batu(lana):
    """2. fasea: geometria zerrenda bat batu. (gakoa, geometria, segundoak)."""
    gakoa, geometriak = lana
    t = time.time()
    g = unary_union(geometriak)
    return gakoa, g, time.time() - t


def _txikitu(lana):
    """
    3. fasea: poligono bat txikitu (-EPS) eta Polygon-ak itzuli.
    (balioa, poligonoak, segundoak, sarrerako erpin kopurua).
    """
    balioa, geom = lana
    t = time.time()
    poligonoak = _poligonoak(geom.buffer(-EPS, **BUFFER_KW))
    return balioa, poligonoak, time.time() - t, _erpin_kop(geom)


def _kanpoa_txikitu(koordenatuak):
    """Poligono baten kanpo-eraztuna (zuloak gabe) txikitu."""
    return Polygon(koordenatuak).buffer(-EPS, **BUFFER_KW)


def _zuloak_handitu(eraztunak):
    """Zulo-lote bat handitu (+EPS) eta batu."""
    return unary_union(
        [Polygon(e).buffer(EPS, **BUFFER_KW) for e in eraztunak]
    )


def txikitu_handia(pool, geom, log):
    """
    Poligono erraldoi baten buffer(-EPS), eraztunak bereizita eginda:

        P erosioa = (kanpo-eraztunaren erosioa) - (zuloen dilatazioa)

    Identitate hau zehatza da (ez da hurbilketa bat). Horrela, zulo
    guztiak batera buffer-eragiketan (noding) sartu beharrean, zulo-loteak
    paraleloan handitzen dira, eta amaieran kenketa bakarra egiten da.
    """
    t = time.time()
    kanpoa_lana = pool.apply_async(_kanpoa_txikitu, (list(geom.exterior.coords),))

    zuloak = [list(i.coords) for i in geom.interiors]
    loteak = [zuloak[i:i + ZULO_LOTEA] for i in range(0, len(zuloak), ZULO_LOTEA)]
    handituak = list(pool.imap_unordered(_zuloak_handitu, loteak, chunksize=1))
    kanpoa = kanpoa_lana.get()
    log.info("   erraldoia: kanpoa + {} zulo handituta: {:.0f} s".format(
        len(zuloak), time.time() - t))

    t = time.time()
    zuloak_batua = unary_union(handituak)
    log.info("   erraldoia: zuloak batuta: {:.0f} s".format(time.time() - t))

    t = time.time()
    emaitza = kanpoa.difference(zuloak_batua)
    log.info("   erraldoia: kenketa: {:.0f} s".format(time.time() - t))
    return _poligonoak(emaitza)


def disolbatu(gdf, eremua, log):
    """
    Poligonoak 'eremua' zutabearen arabera disolbatu, talde bakoitzeko
    poligonoen arteko barne-mugak eta zirrikitu mikroskopikoak kenduz
    (closing teselatua eta paraleloa; ikus moduluaren docstring-a).

    Irteerako geometriak beti Polygon dira (ez MultiPolygon): talde bereko
    poligono bereiziak lerro independenteak izango dira, 'eremua'-ren
    balioa errepikatuz.
    """
    global _GEOMS

    nproz = PROZESUAK or os.cpu_count() or 1
    log.info("Prozesu kopurua: {}; tesela: {} m".format(nproz, TESELA))

    # Taldeak: NULL-ak sentinela batekin ordezkatu (groupby-k ez ditzan baztertu)
    gakoak = gdf[eremua].astype(object).where(gdf[eremua].notnull(), NULL_BALIOA)
    nulu_kop = int((gakoak == NULL_BALIOA).sum())
    if nulu_kop:
        log.abisua(
            "{} erregistrok '{}' eremua hutsik dute; talde independente "
            "bat osatuko dute (NULL)".format(nulu_kop, eremua)
        )

    zentroideak = gdf.geometry.centroid
    tx = np.floor(zentroideak.x.values / TESELA).astype(int)
    ty = np.floor(zentroideak.y.values / TESELA).astype(int)

    taula = pd.DataFrame({"g": gakoak.values, "tx": tx, "ty": ty})
    _GEOMS = list(gdf.geometry.values)

    # 1. fasearen lanak: (balioa, tx, ty) -> posizio-indizeak
    lanak = [
        (gakoa, indizeak)
        for gakoa, indizeak in taula.groupby(["g", "tx", "ty"]).indices.items()
    ]
    # Tesela handienak lehenik (karga hobeto banatzeko)
    lanak.sort(key=lambda l: -len(l[1]))

    t0 = time.time()
    pool = Pool(nproz)  # _GEOMS esleitu ondoren sortu behar da (fork)
    try:
        # --- 1. fasea ---
        log.info("1. fasea: {} tesela-lan (handitu + batu)".format(len(lanak)))
        uneko = {}
        for gakoa, geom in pool.imap_unordered(_handitu_batu, lanak, chunksize=1):
            uneko[gakoa] = geom
        log.info("1. fasea amaituta: {:.1f} s".format(time.time() - t0))

        # --- 2. fasea: teselak mailaz maila batu ---
        t1 = time.time()
        maila = 0
        while True:
            motak = Counter(k[0] for k in uneko)
            if all(n == 1 for n in motak.values()):
                break
            maila += 1
            taldeak = {}
            for (b, x, y), g in uneko.items():
                if maila > 16:  # babes-neurria (koordenatu negatiboak...)
                    berria = (b, 0, 0)
                else:
                    berria = (b, x // 2, y // 2)
                taldeak.setdefault(berria, []).append(g)

            berria_uneko = {}
            lan_batuak = []
            for gakoa, zerrenda in taldeak.items():
                if len(zerrenda) == 1:
                    berria_uneko[gakoa] = zerrenda[0]
                else:
                    lan_batuak.append((gakoa, zerrenda))
            lan_batuak.sort(key=lambda l: -len(l[1]))
            log.info(
                "2. fasea, {}. maila: {} batuketa".format(maila, len(lan_batuak))
            )
            denborak = []
            for gakoa, geom, seg in pool.imap_unordered(_batu, lan_batuak, chunksize=1):
                berria_uneko[gakoa] = geom
                denborak.append((seg, gakoa[0]))
            denborak.sort(reverse=True)
            if denborak:
                log.info("   motelenak: {}".format(
                    ["{} ({:.0f} s)".format(b, s) for s, b in denborak[:3]]
                ))
            uneko = berria_uneko
        log.info("2. fasea amaituta: {:.1f} s".format(time.time() - t1))

        # --- 3. fasea: poligono bakoitza txikitu ---
        t2 = time.time()
        zatiak = []
        for (b, _, _), geom in uneko.items():
            for p in _poligonoak(geom):
                zatiak.append((b, p))
        # Poligono konplexuenak lehenik (kanpo-eraztuna + zuloak)
        neurtuak = [(_erpin_kop(p), b, p) for b, p in zatiak]
        neurtuak.sort(key=lambda z: -z[0])
        handiak = [z for z in neurtuak if z[0] > UMBRALA_ERPINAK]
        zatiak = [(b, p) for n, b, p in neurtuak if n <= UMBRALA_ERPINAK]
        log.info("3. fasea: {} poligono txikitzen ({} erraldoi bereizita)".format(
            len(zatiak) + len(handiak), len(handiak)))

        emaitzak = []
        for erpinak, balioa, geom in handiak:
            t3 = time.time()
            log.info("   erraldoia: {} - {} erpin".format(
                "NULL" if balioa == NULL_BALIOA else balioa, erpinak))
            for p in txikitu_handia(pool, geom, log):
                emaitzak.append((balioa, p))
            log.info("   erraldoia amaituta: {:.0f} s".format(time.time() - t3))

        motelak = []
        for balioa, poligonoak, seg, erpinak in pool.imap_unordered(
                _txikitu, zatiak, chunksize=1):
            motelak.append((seg, balioa, erpinak))
            for p in poligonoak:
                emaitzak.append((balioa, p))
        motelak.sort(reverse=True)
        for seg, b, n in motelak[:5]:
            log.info("   motela: {} - {} erpin - {:.0f} s".format(
                "NULL" if b == NULL_BALIOA else b, n, seg))
        log.info("3. fasea amaituta: {:.1f} s".format(time.time() - t2))
    finally:
        pool.close()
        pool.join()
        _GEOMS = []

    # Ordena deterministikoa (paralelizazioak ordena aldatzen baitu)
    emaitzak.sort(key=lambda e: (e[0], e[1].bounds))

    balioak = [None if b == NULL_BALIOA else b for b, _ in emaitzak]
    disolbatuak = [p for _, p in emaitzak]

    return gpd.GeoDataFrame({eremua: balioak, "geometry": disolbatuak}, crs=gdf.crs)


# ---------------------------------------------------------------------------
# Nagusia
# ---------------------------------------------------------------------------

def main():
    script_izena = os.path.basename(sys.argv[0])

    # --help argparse-k kudeatzen du eta ez du Log-a behar.
    argumentuak = parseatu_argumentuak()

    # --- Log sistema abiarazi (argumentuak parseatu ondoren) ---
    log = Log(argumentuak.log_fitxategia, script_izena, sys.argv[1:])

    try:
        egiaztatu_sarrera(argumentuak.sarrera_gpkg, log)
        egiaztatu_bideak(argumentuak.sarrera_gpkg, argumentuak.irteera_gpkg, log)

        hasiera = time.time()

        log.info("Irakurtzen: {}".format(argumentuak.sarrera_gpkg))
        gdf = irakurri_gpkg(argumentuak.sarrera_gpkg, log)

        if gdf is None or gdf.empty:
            log.errorea("Ez dago poligono baliozkorik sarrerako fitxategian")
            sys.exit(1)

        if FIELD not in gdf.columns:
            log.errorea(
                "'{}' eremua ez dago sarrerako fitxategian".format(FIELD)
            )
            sys.exit(1)

        log.info(
            "Disolbatzen '{}' eremuaren arabera...".format(FIELD)
        )
        emaitza = disolbatu(gdf, FIELD, log)
        log.info(
            "{} poligono sarrera -> {} poligono irteera".format(len(gdf), len(emaitza))
        )

        if emaitza.empty:
            log.errorea("Disolbatzearen emaitza hutsik dago")
            sys.exit(1)

        # Fitxategi tenporalera idatzi eta amaieran ordezkatu: prozesuak huts
        # egiten badu, aurreko irteera (baldin bazegoen) ez da galtzen.
        irteera = argumentuak.irteera_gpkg
        tenporala = irteera + ".tmp.gpkg"
        ezabatu_gpkg(tenporala)
        geruza = os.path.splitext(os.path.basename(irteera))[0]

        log.info("Idazten: {}".format(irteera))
        emaitza.to_file(tenporala, layer=geruza, driver="GPKG")

        ezabatu_gpkg(irteera, log)
        os.replace(tenporala, irteera)

        bukaera = time.time()
        log.info(
            "Amaituta. Denbora: {:.2f} segundo".format(bukaera - hasiera)
        )

    except Exception as e:
        log.errorea("Salbuespena: {}: {}".format(type(e).__name__, e))
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
