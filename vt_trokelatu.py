#!/usr/bin/env python3
"""
Bi GPKG poligonen arteko trokelatzea, azpikoarekin fusionatuta.

Sarrera:
  - GPKG_A (azpikoa): oinarrizko poligonoa(k) eta haien atributuak.
  - GPKG_B (gainekoa): trokel gisa jokatzen duen poligonoa(k).

Irteera:
  - GPKG_IRTEERA: A-ren geometria ken B-ren geometria (diferentzia),
    A-ren atributuekin fusionatuta. Bi eremu:
      - fid: automatikoki sortutako identifikatzailea (1, 2, 3, ...)
      - type: azpiko GPKGtik jasotako balioa

Erabilera:
  python3 <scripta> azpikoa.gpkg gainekoa.gpkg irteera.gpkg
"""

import sys
import os
import time
import geopandas as gpd
from shapely.ops import unary_union
from shapely.validation import make_valid


def formatu_denbora(segundoak):
    """Denbora irakurgarri bihurtu: 1h 23m 45.6s / 12m 03.4s / 8.42s"""
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
    """GPKG fitxategiaren izena itzuli, .gpkg atzizkia kenduta."""
    izena = os.path.basename(gpkg_bidea)
    if izena.lower().endswith(".gpkg"):
        izena = izena[:-5]
    return izena


def aurkitu_type_eremua(gdf):
    """Azpiko GPKGan 'type' izena duen eremua bilatu."""
    hautagaiak = ["type", "TYPE", "Type", "mota", "MOTA"]
    for izena in hautagaiak:
        if izena in gdf.columns:
            return izena
    return None


def garbitu_geometriak(gdf, izena_testuingurua=""):
    """Geometria nuluak kendu eta baliogabeak zuzendu.

    'TopologyException' motako erroreak saihesteko erabiltzen da.
    Itzultzen du: (gdf_garbitua, kendutako_kopurua, zuzendutako_kopurua)
    """
    hasieran = len(gdf)

    # 1. Geometria nuluak / hutsak kendu
    maskara = gdf.geometry.notna() & ~gdf.geometry.is_empty
    kendutakoak = hasieran - maskara.sum()
    gdf = gdf[maskara].copy()

    if kendutakoak > 0:
        print(f"   {izena_testuingurua}: {kendutakoak} geometria nulu/huts kenduta.")

    # 2. Geometria baliogabeak zuzendu
    baliogabeak = ~gdf.geometry.is_valid
    zuzendutakoak = int(baliogabeak.sum())

    if zuzendutakoak > 0:
        print(f"   {izena_testuingurua}: {zuzendutakoak} geometria baliogabe "
              f"zuzentzen (make_valid)...")
        t0 = time.perf_counter()
        gdf.loc[baliogabeak, "geometry"] = gdf.loc[baliogabeak, "geometry"].apply(
            _zuzendu_geometria
        )
        # Zuzentzean agian geometria nuluak sortu dira; hauek berriro kendu
        maskara2 = gdf.geometry.notna() & ~gdf.geometry.is_empty
        kendutakoak2 = int((~maskara2).sum())
        if kendutakoak2 > 0:
            gdf = gdf[maskara2].copy()
            print(f"   {izena_testuingurua}: {kendutakoak2} geometria gehiago "
                  f"kenduta zuzentzearen ondoren.")
        print(f"   Zuzentzea: {formatu_denbora(time.perf_counter() - t0)}")

    return gdf, kendutakoak, zuzendutakoak


def _zuzendu_geometria(geom):
    """Geometria bakarra zuzendu. make_valid-ek huts egiten badu, buffer(0)
    erabili azken baliabide gisa."""
    try:
        return make_valid(geom)
    except Exception:
        try:
            return geom.buffer(0)
        except Exception:
            return None


def trokelatu(gpkg_azpikoa, gpkg_gainekoa, gpkg_irteera):
    t_hasiera = time.perf_counter()

    irteera_geruza = geruza_izena(gpkg_irteera)

    # --- 1. Geruzak kargatu ---
    t0 = time.perf_counter()
    gdf_azpi = gpd.read_file(gpkg_azpikoa)
    gdf_gain = gpd.read_file(gpkg_gainekoa)
    t_karga = time.perf_counter() - t0
    print(f"Karga: {formatu_denbora(t_karga)} "
          f"(azpikoa: {len(gdf_azpi)} elem., gainekoa: {len(gdf_gain)} elem.)")

    if gdf_azpi.empty:
        raise ValueError(f"Azpiko GPKGa hutsik dago: {gpkg_azpikoa}")
    if gdf_gain.empty:
        raise ValueError(f"Gaineko GPKGa hutsik dago: {gpkg_gainekoa}")

    # --- 2. 'type' eremua aurkitu azpikoan ---
    type_eremua = aurkitu_type_eremua(gdf_azpi)
    if type_eremua is None:
        raise ValueError(
            "Azpiko GPKGan ez da 'type' izeneko eremurik aurkitu. "
            f"Eskuragarri dauden eremuak: {list(gdf_azpi.columns)}"
        )
    print(f"'type' eremua aurkitu da: '{type_eremua}'")

    # --- 3. CRSa egiaztatu ---
    if gdf_azpi.crs is None or gdf_gain.crs is None:
        raise ValueError("Geruzaren batek ez du CRSrik definituta.")
    if gdf_azpi.crs != gdf_gain.crs:
        print(f"OHARRA: CRS desberdinak. Gainekoa {gdf_gain.crs}-tik "
              f"{gdf_azpi.crs}-ra birproiektatzen.")
        t0 = time.perf_counter()
        gdf_gain = gdf_gain.to_crs(gdf_azpi.crs)
        print(f"   Birproiekzioa: {formatu_denbora(time.perf_counter() - t0)}")

    # --- 4. Geometriak garbitu (errore topologikoak saihesteko) ---
    print("Geometriak garbitzen...")
    t0 = time.perf_counter()
    gdf_gain, _, _ = garbitu_geometriak(gdf_gain, "gainekoa")
    gdf_azpi, _, _ = garbitu_geometriak(gdf_azpi, "azpikoa")
    print(f"Garbiketa: {formatu_denbora(time.perf_counter() - t0)}")

    if gdf_gain.empty:
        raise ValueError("Gaineko GPKGan ez da geometria baliodunik geratzen.")
    if gdf_azpi.empty:
        raise ValueError("Azpiko GPKGan ez da geometria baliodunik geratzen.")

    # --- 5. Trokelaren poligono guztiak geometria bakarrean batu ---
    t0 = time.perf_counter()
    trokela = unary_union(gdf_gain.geometry.values)
    t_batuketa = time.perf_counter() - t0
    print(f"Trokela: {len(gdf_gain)} poligono batu dira "
          f"({formatu_denbora(t_batuketa)}).")

    # Trokelak berak baliogabea izan daiteke batuketaren ondoren
    if not trokela.is_valid:
        print("Trokela baliogabea da; make_valid aplikatzen...")
        trokela = make_valid(trokela)

    # --- 6. Diferentzia aplikatu (A - B) ---
    t0 = time.perf_counter()
    gdf_out = gdf_azpi.copy()
    gdf_out["geometry"] = gdf_out.geometry.difference(trokela)
    t_dif = time.perf_counter() - t0
    print(f"Diferentzia: {formatu_denbora(t_dif)}")

    # --- 7. Geometria hutsak / nuluak ezabatu (guztiz estalita daudenak) ---
    aurretik = len(gdf_out)
    gdf_out = gdf_out[~gdf_out.geometry.is_empty & gdf_out.geometry.notna()]
    ondoren = len(gdf_out)
    print(f"Elementuak: {aurretik} -> {ondoren} "
          f"({aurretik - ondoren} ezabatu dira guztiz estalita zeudelako).")

    if gdf_out.empty:
        print("OHARRA: Emaitza hutsik dago; trokelak azpikoa guztiz estaltzen du.")

    # --- 8. Fusionatu: 'fid' eta 'type' besterik ez ---
    gdf_out = gdf_out.reset_index(drop=True)
    gdf_out["fid"] = range(1, len(gdf_out) + 1)
    gdf_out["type"] = gdf_out[type_eremua]

    gdf_out = gdf_out[["fid", "type", "geometry"]]
    gdf_out = gdf_out.set_geometry("geometry")

    print(f"Fusioa: {len(gdf_out)} elementu, eremuak: fid, type, geometry")

    # --- 9. Emaitza gorde ---
    if os.path.exists(gpkg_irteera):
        os.remove(gpkg_irteera)

    t0 = time.perf_counter()
    gdf_out.to_file(gpkg_irteera, layer=irteera_geruza, driver="GPKG")
    t_idazketa = time.perf_counter() - t0
    print(f"Idazketa: {formatu_denbora(t_idazketa)}")
    print(f"Gordeta: {gpkg_irteera} (geruza: '{irteera_geruza}')")

    # --- Guztizko denbora ---
    t_guzti = time.perf_counter() - t_hasiera
    print("-" * 50)
    print(f"Guztizko denbora: {formatu_denbora(t_guzti)}")


def main():
    script_izena = os.path.basename(sys.argv[0]) or "trokelatu_gpkg.py"

    if len(sys.argv) != 4:
        print(f"Erabilera: python3 {script_izena} <azpikoa.gpkg> "
              f"<gainekoa.gpkg> <irteera.gpkg>")
        sys.exit(1)

    trokelatu(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
