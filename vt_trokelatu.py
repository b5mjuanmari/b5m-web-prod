#!/usr/bin/env python3
"""
Bi GPKG poligonen arteko trokelatzea, azpikoarekin fusionatuta.

Sarrera:
  - GPKG_A (azpikoa): oinarrizko poligonoa(k) eta haien atributuak.
  - GPKG_B (gainekoa): trokel gisa jokatzen duen poligonoa(k).

Irteera:
  - GPKG_IRTEERA: A-ren geometria ken B-ren geometria (diferentzia).
    A-ren atributu guztiak mantentzen dira, 'fid' izan ezik; 'fid' berria
    automatikoki sortzen da (1, 2, 3, ...).

Erabilera:
  python3 <scripta> azpikoa.gpkg gainekoa.gpkg irteera.gpkg [log_fitxategia]

  log_fitxategia aukerakoa da:
    - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
    - ez bada ematen: mezuak terminalera soilik (TTY bada)

Oharra: Shapely 1.8.x-rekin bateragarria (query-ek geometriak itzultzen
ditu, ez indizeak).
"""

import sys
import os
import time
import warnings
import geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid
from shapely.strtree import STRtree

from log_utils import Log

# Shapely-ren STRtree deprecation abisua isildu.
# Shapely 2.0-ra igarotzean, hau ezabatu ahal izango da.
try:
    from shapely.errors import ShapelyDeprecationWarning
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
except ImportError:
    warnings.filterwarnings("ignore", message=".*STRtree.*")


def formatu_denbora(segundoak):
    if segundoak >= 3600:
        h = int(segundoak // 3600)
        m = int((segundoak % 3600) // 60)
        s = segundoak % 60
        return f"{h}h {m:02d}m {s:05.2f}s"
    elif segundoak >= 60:
        m = int(segundoak // 60)
        s = segundoak % 60
        return f"{m}m {s:05.2f}s"
    else:
        return f"{segundoak:.2f}s"


def geruza_izena(gpkg_bidea):
    izena = os.path.basename(gpkg_bidea)
    if izena.lower().endswith(".gpkg"):
        izena = izena[:-5]
    return izena


def _zuzendu_geometria(geom):
    try:
        return make_valid(geom)
    except Exception:
        try:
            return geom.buffer(0)
        except Exception:
            return None


def garbitu_geometriak(gdf, log, izena_testuingurua=""):
    hasieran = len(gdf)

    maskara = gdf.geometry.notna() & ~gdf.geometry.is_empty
    kendutakoak = int(hasieran - maskara.sum())
    gdf = gdf[maskara].copy()

    if kendutakoak > 0:
        log.info(
            f"   {izena_testuingurua}: {kendutakoak} geometria "
            f"nulu/huts kenduta."
        )

    baliogabeak = ~gdf.geometry.is_valid
    zuzendutakoak = int(baliogabeak.sum())

    if zuzendutakoak > 0:
        log.info(
            f"   {izena_testuingurua}: {zuzendutakoak} geometria baliogabe "
            f"zuzentzen (make_valid)..."
        )
        t0 = time.perf_counter()
        gdf.loc[baliogabeak, "geometry"] = gdf.loc[
            baliogabeak, "geometry"
        ].apply(_zuzendu_geometria)
        maskara2 = gdf.geometry.notna() & ~gdf.geometry.is_empty
        kendutakoak2 = int((~maskara2).sum())
        if kendutakoak2 > 0:
            gdf = gdf[maskara2].copy()
            log.info(
                f"   {izena_testuingurua}: {kendutakoak2} geometria "
                f"gehiago kenduta zuzentzearen ondoren."
            )
        log.info(
            f"   Zuzentzea: {formatu_denbora(time.perf_counter() - t0)}"
        )

    return gdf, kendutakoak, zuzendutakoak


def trokelatu(gpkg_azpikoa, gpkg_gainekoa, gpkg_irteera, log):
    t_hasiera = time.perf_counter()

    irteera_geruza = geruza_izena(gpkg_irteera)

    # --- 1. Azpikoa irakurri ---
    t0 = time.perf_counter()
    gdf_azpi = gpd.read_file(gpkg_azpikoa)
    t_azpi = time.perf_counter() - t0
    log.info(
        f"Azpikoa kargatu: {formatu_denbora(t_azpi)} "
        f"({len(gdf_azpi)} elem.)"
    )

    if gdf_azpi.empty:
        raise ValueError(f"Azpiko GPKGa hutsik dago: {gpkg_azpikoa}")

    # --- 2. Gainekoa irakurri, azpikoaren bbox-arekin iragazita ---
    bbox = tuple(gdf_azpi.total_bounds)  # (minx, miny, maxx, maxy)
    t0 = time.perf_counter()
    gdf_gain = gpd.read_file(gpkg_gainekoa, bbox=bbox)
    t_gain = time.perf_counter() - t0
    log.info(
        f"Gainekoa kargatu (bbox iragazkiarekin): {formatu_denbora(t_gain)} "
        f"({len(gdf_gain)} elem.)"
    )

    if gdf_gain.empty:
        raise ValueError(f"Gaineko GPKGa hutsik dago: {gpkg_gainekoa}")

    # --- 3. CRSa egiaztatu ---
    if gdf_azpi.crs is None or gdf_gain.crs is None:
        raise ValueError("Geruzaren batek ez du CRSrik definituta.")
    if gdf_azpi.crs != gdf_gain.crs:
        log.abisua(
            f"CRS desberdinak. Gainekoa {gdf_gain.crs}-tik "
            f"{gdf_azpi.crs}-ra birproiektatzen."
        )
        t0 = time.perf_counter()
        gdf_gain = gdf_gain.to_crs(gdf_azpi.crs)
        log.info(
            f"   Birproiekzioa: {formatu_denbora(time.perf_counter() - t0)}"
        )

    # --- 4. Geometriak garbitu ---
    log.info("Geometriak garbitzen...")
    t0 = time.perf_counter()
    gdf_gain, _, _ = garbitu_geometriak(gdf_gain, log, "gainekoa")
    gdf_azpi, _, _ = garbitu_geometriak(gdf_azpi, log, "azpikoa")
    log.info(f"Garbiketa: {formatu_denbora(time.perf_counter() - t0)}")

    if gdf_gain.empty:
        raise ValueError(
            "Gaineko GPKGan ez da geometria baliodunik geratzen."
        )
    if gdf_azpi.empty:
        raise ValueError(
            "Azpiko GPKGan ez da geometria baliodunik geratzen."
        )

    # --- 5. STRtree eraiki ---
    log.info("STRtree-a eraikitzen...")
    t0 = time.perf_counter()
    geoms_gain = list(gdf_gain.geometry.values)
    zuhaitza = STRtree(geoms_gain)
    log.info(f"STRtree-a: {formatu_denbora(time.perf_counter() - t0)}")

    # --- 6. Diferentzia zatika ---
    log.info("Diferentzia zatika...")
    t0 = time.perf_counter()
    berria = []
    for geom_azpi in gdf_azpi.geometry:
        hautagaiak = zuhaitza.query(geom_azpi)
        baliozkoak = [g for g in hautagaiak if g.intersects(geom_azpi)]
        if len(baliozkoak) == 0:
            berria.append(geom_azpi)
            continue
        trokela_partziala = unary_union(baliozkoak)
        if not trokela_partziala.is_valid:
            trokela_partziala = make_valid(trokela_partziala)
        berria.append(geom_azpi.difference(trokela_partziala))
    t_dif = time.perf_counter() - t0
    log.info(f"Diferentzia: {formatu_denbora(t_dif)}")

    gdf_out = gdf_azpi.copy()
    gdf_out["geometry"] = berria

    # --- 7. Geometria hutsak / nuluak ezabatu ---
    aurretik = len(gdf_out)
    gdf_out = gdf_out[~gdf_out.geometry.is_empty & gdf_out.geometry.notna()]
    ondoren = len(gdf_out)
    log.info(
        f"Elementuak: {aurretik} -> {ondoren} "
        f"({aurretik - ondoren} ezabatu dira guztiz estalita zeudelako)."
    )

    if gdf_out.empty:
        log.abisua(
            "Emaitza hutsik dago; trokelak azpikoa guztiz estaltzen du."
        )

    # --- 8. 'fid' zaharra kendu, berria sortu ---
    gdf_out = gdf_out.reset_index(drop=True)

    if "fid" in gdf_out.columns:
        gdf_out = gdf_out.drop(columns=["fid"])
        log.info("'fid' zaharra kendu da azpiko GPKGtik.")

    gdf_out.insert(0, "fid", range(1, len(gdf_out) + 1))

    zutabeak = [c for c in gdf_out.columns if c != "geometry"] + ["geometry"]
    gdf_out = gdf_out[zutabeak]
    gdf_out = gdf_out.set_geometry("geometry")

    log.info(
        f"Fusioa: {len(gdf_out)} elementu, eremuak: "
        f"{list(gdf_out.columns)}"
    )

    # --- 9. Emaitza gorde ---
    if os.path.exists(gpkg_irteera):
        os.remove(gpkg_irteera)

    t0 = time.perf_counter()
    gdf_out.to_file(gpkg_irteera, layer=irteera_geruza, driver="GPKG")
    t_idazketa = time.perf_counter() - t0
    log.info(f"Idazketa: {formatu_denbora(t_idazketa)}")
    log.info(f"Gordeta: {gpkg_irteera} (geruza: '{irteera_geruza}')")

    # --- Guztizko denbora ---
    t_guzti = time.perf_counter() - t_hasiera
    log.info("-" * 50)
    log.info(f"Guztizko denbora: {formatu_denbora(t_guzti)}")


def main():
    script_izena = os.path.basename(sys.argv[0]) or "vt_trokelatu.py"

    # --- Argumentuak egiaztatu ---
    if len(sys.argv) not in (4, 5):
        print(
            f"Erabilera: python3 {script_izena} <azpikoa.gpkg> "
            f"<gainekoa.gpkg> <irteera.gpkg> [log_fitxategia]",
            file=sys.stderr,
        )
        sys.exit(1)

    gpkg_azpikoa = sys.argv[1]
    gpkg_gainekoa = sys.argv[2]
    gpkg_irteera = sys.argv[3]
    log_path = sys.argv[4] if len(sys.argv) == 5 else None

    # --- Log sistema abiarazi ---
    log = Log(log_path, script_izena, sys.argv[1:])

    try:
        trokelatu(gpkg_azpikoa, gpkg_gainekoa, gpkg_irteera, log)

    except Exception as e:
        log.errorea(f"Salbuespena: {type(e).__name__}: {e}")
        raise

    finally:
        log.bukaera()


if __name__ == "__main__":
    main()
