#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poligonoak sare erregular batean zatitzen ditu (lehenespenez 5x5 km).

Zertarako: poligono erraldoiek (milioika ertice) MapServer/MVT tile-ak
motelarazten dituzte. Poligonoak gelaxka txikiagoetan zatituz, tile
bakoitzak ertice gutxiko poligonoak irakurri behar ditu.

Erabilera
---------
    python3 <script> <sarrera.gpkg> <irteera.gpkg> [hautaketa] [log_fitxategia]

Parametroak
-----------
  1. sarrera.gpkg   Jatorrizko GPKG fitxategia. Egon behar du. Geruza
                    bat baino gehiago badago, lehenengoa erabiltzen da.
  2. irteera.gpkg   GPKG helburua. Existitzen bada, ABIAN JARTZEAN
                    ezabatzen da (hautaketak elementurik ematen ez
                    badu, ordea, ez da ezer ezabatzen).
                    Irteerako geruzaren izena fitxategiarena izango da,
                    .gpkg atzizkirik gabe.
  3. hautaketa      (hautazkoa) Atributuen hautaketa-adierazpena, OGR SQL
                    WHERE sintaxiarekin, adib. "type = 'artificial'".
                    Jarriz gero, adierazpen horrek hautatzen dituen
                    elementuak BAKARRIK zatitzen dira; gainerakoak
                    aldatu gabe kopiatzen dira. Ez badago (edo ""),
                    elementu guztiak zatitzen dira. Elementurik hautatzen
                    ez bada, mezu bat ematen da eta ez da ezer egiten.
  4. log_fitxategia (hautazkoa) Log fitxategiaren bidea (append modua).
                    Ez bada ematen, mezuak terminalera soilik doaz.
                    Hautaketarik gabe log-a erabili nahi bada, jarri ""
                    hirugarren posizioan.

Adibideak
---------
    python3 <script> sarrera.gpkg irteera.gpkg
    python3 <script> sarrera.gpkg irteera.gpkg "type = 'artificial'"
    python3 <script> sarrera.gpkg irteera.gpkg "" /bidea/log.txt
    python3 <script> sarrera.gpkg irteera.gpkg "type = 'artificial'" /bidea/log.txt

Atalasea: SAREA_TAMAINA aldatu daiteke (metrotan, CRS-aren unitateetan).

Menpekotasunak: geopandas, shapely, GDAL/OGR (osgeo), log_utils.py
(scriptaren karpeta berean edo PYTHONPATH-ean).
"""

import os
import sys
import time
from math import floor

import geopandas as gpd
from osgeo import ogr
from shapely.geometry import box

from log_utils import Log

# Sarearen gelaxka-tamaina (CRS-aren unitateetan; EPSG:25830 -> metroak).
SAREA_TAMAINA = 5000

# Aurrerapen-mezua zenbat elementuro idatzi.
AURRERAPEN_URRATSA = 10000


def formatu_denbora(segundoak):
    """Segundoak 'O:MM:SS' formatuan itzultzen ditu."""
    segundoak = int(round(segundoak))
    ordu, hondar = divmod(segundoak, 3600)
    minutu, seg = divmod(hondar, 60)
    return f"{ordu}:{minutu:02d}:{seg:02d}"


def erabilera(script_izena):
    """Erabileraren mezua stderr-era idazten du."""
    print(
        f"Erabilera: python3 {script_izena} <sarrera.gpkg> <irteera.gpkg> "
        f"[hautaketa] [log_fitxategia]\n"
        f"  hautaketa: OGR SQL WHERE adierazpena, adib. \"type = 'artificial'\"\n"
        f"             (\"\" = elementu guztiak)",
        file=sys.stderr,
    )


def konpondu_geometria(geom):
    """Geometria baliogabea bada, konpontzen saiatzen da."""
    if geom.is_valid:
        return geom, False
    try:  # Shapely >= 1.8
        from shapely.validation import make_valid
        return make_valid(geom), True
    except ImportError:  # Shapely zaharra (adib. 1.7)
        return geom.buffer(0), True


def zatitu_geometria(geom, tamaina):
    """
    Geometria bat sare erregular baten gelaxketan zatitzen du.

    Gelaxka bakarrean sartzen bada, geometria bera itzultzen da (ebaketarik
    gabe). Bestela, gelaxka bakoitzarekin ebakitzen da.

    :param geom: shapely geometria (Polygon edo MultiPolygon)
    :param tamaina: gelaxkaren aldea
    :return: Polygon zatien zerrenda
    """
    minx, miny, maxx, maxy = geom.bounds
    ix0, ix1 = int(floor(minx / tamaina)), int(floor(maxx / tamaina))
    iy0, iy1 = int(floor(miny / tamaina)), int(floor(maxy / tamaina))

    if ix0 == ix1 and iy0 == iy1:
        gelaxkak = [(ix0, iy0)]
    else:
        gelaxkak = [(ix, iy)
                    for ix in range(ix0, ix1 + 1)
                    for iy in range(iy0, iy1 + 1)]

    zatiak = []
    for ix, iy in gelaxkak:
        gelaxka = box(ix * tamaina, iy * tamaina,
                      (ix + 1) * tamaina, (iy + 1) * tamaina)
        zati = geom if len(gelaxkak) == 1 else geom.intersection(gelaxka)
        if zati.is_empty:
            continue
        # Ebaketak GeometryCollection eman dezake: poligonoak soilik hartu.
        for p in getattr(zati, "geoms", [zati]):
            if p.geom_type == "Polygon" and p.area > 0:
                zatiak.append(p)
            elif p.geom_type == "MultiPolygon":
                zatiak.extend(q for q in p.geoms if q.area > 0)
    return zatiak


def fid_zerrendak(bidea, hautaketa, log):
    """
    OGR bidez, geruzaren FID guztiak (ordenan) eta hautatutakoak lortzen ditu.

    :return: (geruza_izena, fid_guztiak, hautatutako_fid_multzoa)
    :raises ValueError: hautaketa-adierazpena baliogabea bada
    """
    ds = ogr.Open(bidea)
    if ds is None:
        raise ValueError(f"Ezin izan da irekitzeko: {bidea}")
    if ds.GetLayerCount() > 1:
        log.abisua(
            f"Geruza bat baino gehiago ({ds.GetLayerCount()}) daude; "
            f"lehenengoa erabiliko da."
        )
    geruza = ds.GetLayer(0)
    izena = geruza.GetName()

    hautatuak = set()
    if hautaketa:
        try:
            ema = geruza.SetAttributeFilter(hautaketa)
        except RuntimeError as e:
            raise ValueError(f"Hautaketa baliogabea ({hautaketa}): {e}")
        if ema != 0:
            raise ValueError(f"Hautaketa baliogabea: {hautaketa}")
        geruza.ResetReading()
        for ft in geruza:
            hautatuak.add(ft.GetFID())
        geruza.SetAttributeFilter(None)

    geruza.ResetReading()
    guztiak = [ft.GetFID() for ft in geruza]
    ds = None
    return izena, guztiak, hautatuak


def nagusia(sarrera, irteera, hautaketa, log):
    """
    Prozesu nagusia.

    :return: irteera-kodea (0 ondo, 0 ez ezer egiteko, 1 errorea)
    """
    t0 = time.time()

    # 1. Sarrera egiaztatu
    if not os.path.isfile(sarrera):
        log.errorea(f"Sarrerako GPKG ez da existitzen: {sarrera}")
        return 1
    if os.path.abspath(sarrera) == os.path.abspath(irteera):
        log.errorea("Sarrera eta irteera fitxategi berdina dira.")
        return 1
    log.info(f"Sarrera: {sarrera}")
    log.info(f"Irteera: {irteera}")

    # 2. Hautaketa (irteera ezabatu aurretik, ezer egin behar ez bada)
    log.info("Elementuen FID-ak irakurtzen...")
    try:
        geruza_izena, guztiak, hautatuak = fid_zerrendak(
            sarrera, hautaketa, log)
    except ValueError as e:
        log.errorea(str(e))
        return 1
    log.info(f"Sarrerako geruza: {geruza_izena}; elementuak: {len(guztiak)}")

    if hautaketa:
        log.info(f"Hautaketa: {hautaketa} -> {len(hautatuak)} elementu")
        if not hautatuak:
            log.info("Hautaketak ez du elementurik hautatu. Ez da ezer egingo.")
            return 0
    else:
        log.info("Hautaketarik gabe: elementu guztiak zatituko dira.")

    # 3. Irteera ezabatu existitzen bada
    if os.path.exists(irteera):
        log.abisua(f"Irteerako fitxategia existitzen da; ezabatzen: {irteera}")
        os.remove(irteera)

    # 4. Datuak irakurri
    log.info("Datuak irakurtzen...")
    gdf = gpd.read_file(sarrera, layer=geruza_izena)
    if len(gdf) != len(guztiak):
        log.errorea(
            f"Elementu kopurua ez dator bat (geopandas {len(gdf)}, "
            f"OGR {len(guztiak)})."
        )
        return 1
    zatitu_mask = [(not hautaketa) or (fid in hautatuak) for fid in guztiak]

    # 5. Zatitu
    zutabeak = [c for c in gdf.columns if c != "geometry"]
    atributuak = gdf[zutabeak].to_dict("records")
    log.info(
        f"Zatitzen ({SAREA_TAMAINA} x {SAREA_TAMAINA} sarea): "
        f"{sum(zatitu_mask)} elementu..."
    )

    erregistroak, geometriak = [], []
    konponduak = 0
    zatitutakoak = 0
    for i, (geom, attr, zatitu) in enumerate(
            zip(gdf.geometry, atributuak, zatitu_mask), start=1):
        if geom is None or geom.is_empty:
            continue
        if zatitu:
            geom, konpondu = konpondu_geometria(geom)
            konponduak += int(konpondu)
            zatiak = zatitu_geometria(geom, SAREA_TAMAINA)
            zatitutakoak += 1
        else:
            zatiak = [geom]
        for zati in zatiak:
            erregistroak.append(attr)
            geometriak.append(zati)
        if i % AURRERAPEN_URRATSA == 0:
            log.info(f"  {i}/{len(gdf)} elementu prozesatuta "
                     f"({len(geometriak)} zati)")

    if konponduak:
        log.abisua(f"{konponduak} geometria baliogabe konpondu dira.")

    # 6. Idatzi (geruza-izena = fitxategi-izena, .gpkg gabe)
    irteera_geruza = os.path.splitext(os.path.basename(irteera))[0]
    out = gpd.GeoDataFrame(erregistroak, geometry=geometriak,
                           columns=zutabeak, crs=gdf.crs)
    out = out.explode().reset_index(drop=True)  # MultiPolygon -> Polygon
    log.info(f"Idazten: {irteera} (geruza: {irteera_geruza}, "
             f"{len(out)} elementu)")
    out.to_file(irteera, layer=irteera_geruza, driver="GPKG")

    log.info(f"Zatitutako jatorrizko elementuak: {zatitutakoak}")
    log.info(f"Sarrerako elementuak: {len(gdf)} -> irteerakoak: {len(out)}")
    log.info(f"Guztizko denbora: {formatu_denbora(time.time() - t0)}")
    return 0


def main():
    # Scriptaren izena argv-tik hartzen da: fitxategia berrizendatzen bada,
    # ez da kodea aldatu behar.
    script_izena = os.path.basename(sys.argv[0])

    if not 3 <= len(sys.argv) <= 5:
        erabilera(script_izena)
        sys.exit(2)

    sarrera = sys.argv[1]
    irteera = sys.argv[2]
    hautaketa = sys.argv[3].strip() if len(sys.argv) >= 4 else ""
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # Log-aren eraikitzaileak "Hasiera" mezua idazten du berez.
    log = Log(log_path, script_izena, sys.argv[1:])
    kodea = 1
    try:
        kodea = nagusia(sarrera, irteera, hautaketa, log)
    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
    finally:
        log.bukaera()
    sys.exit(kodea)


if __name__ == "__main__":
    main()
