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

Algoritmoa (azkarra):
  1. Gaineko geometriak ez dira batasun global bakar batean fusionatzen.
  2. Azpiko poligono bakoitzarentzat, indize espazialarekin bere bbox-a
     ukitzen duten gaineko poligonoak soilik hartzen dira.
  3. Poligonoa ukitzen ez duena aldatu gabe geratzen da.
  4. Gaineko poligono batek guztiz estaltzen badu (prep.covers), ezabatu.
  5. Gainerakoetan, trokela poligonoaren bbox-era moztu (clip_by_rect)
     eta diferentzia txiki horrekin kalkulatu.
  6. Kalkulu astuna prozesu anitzetan banatzen da (fork, Linux).

Oharra: Python 3.6+, Shapely 1.8.x eta 2.x-rekin bateragarria.
"""

import sys
import os
import time
import warnings
import multiprocessing
import geopandas as gpd
from shapely.ops import unary_union, clip_by_rect
from shapely.validation import make_valid
from shapely.prepared import prep
from shapely.geometry import MultiPolygon

from log_utils import Log

# ---------------------------------------------------------------------------
# Parametro konfiguragarriak
# ---------------------------------------------------------------------------
PROZESU_KOPURUA = None   # None = CPU kopurua - 1 (gutxienez 1)
CHUNKSIZE = 200          # prozesu bakoitzari banatutako lan-zatiaren tamaina
MARGINA_ERATIOA = 0.05   # clip-eko marjina, poligonoaren tamainaren zatiki gisa
BIHURTU_MULTI = False    # True: irteerako geometria guztiak MultiPolygon
PROGRESO_ZATIA = 10      # logean progresua zenbat %-ro idatzi

POLIGONALAK = ("Polygon", "MultiPolygon")

# Abisu zaharrak isildu.
try:
    from shapely.errors import ShapelyDeprecationWarning
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
except ImportError:
    pass
warnings.filterwarnings(
    "ignore", message=".*GeoSeries.notna.*", category=UserWarning
)

# Prozesu-bikoteen artean partekatutako datuak (fork-aren bidez heredatzen
# dira, ez dira kopiatzen ez serializatzen).
_AZPI = None   # azpiko geometrien zerrenda
_GAIN = None   # gaineko geometrien zerrenda
_PREP = None   # gaineko geometria prestatuak
_KAND = None   # {azpiko indizea: [gaineko kandidatuen indizeak]}


# ---------------------------------------------------------------------------
# Laguntzaileak
# ---------------------------------------------------------------------------
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


def _geruza_hautatu(gpkg_bidea):
    """
    Fitxategi izen bereko geruza badago, hura erabiltzen da; bestela,
    None (GeoPandas-ek lehen geruza irakurriko du).
    """
    try:
        import fiona
        geruzak = fiona.listlayers(gpkg_bidea)
        izena = geruza_izena(gpkg_bidea)
        if izena in geruzak:
            return izena
    except Exception:
        pass
    return None


def _lortu_crs(gpkg_bidea, geruza=None):
    """
    GPKG baten CRS-a irakurtzen du, geometria guztia kargatu gabe.
    """
    try:
        import fiona
        with fiona.open(gpkg_bidea, layer=geruza) as src:
            return src.crs
    except Exception:
        try:
            gdf = gpd.read_file(gpkg_bidea, layer=geruza, rows=1)
            return gdf.crs
        except Exception:
            return None


def _crs_berdinak(a, b):
    """
    Bi CRS berdinak diren egiaztatzen du, irudikapen-aldeei erreparatu gabe
    (dict vs WKT vs EPSG kodea).
    """
    try:
        from pyproj import CRS
        return CRS.from_user_input(a) == CRS.from_user_input(b)
    except Exception:
        return a == b


def _soilik_poligonoak(geom):
    """
    Geometria poligonalera murrizten du: Polygon/MultiPolygon bere horretan,
    kolekzioetatik poligonoak soilik, eta gainerakoa (lerroak, puntuak)
    None bihurtzen du.
    """
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type in POLIGONALAK:
        return geom
    if hasattr(geom, "geoms"):
        zatiak = []
        for g in geom.geoms:
            g2 = _soilik_poligonoak(g)
            if g2 is not None:
                zatiak.append(g2)
        if not zatiak:
            return None
        return unary_union(zatiak)
    return None


def _zuzendu_geometria(geom):
    """
    Geometria baliogabea zuzentzen du eta emaitza poligonala bermatzen du
    (make_valid-ek lerroak edo kolekzioak itzul ditzake).
    """
    try:
        emaitza = make_valid(geom)
    except Exception:
        try:
            emaitza = geom.buffer(0)
        except Exception:
            return None

    emaitza = _soilik_poligonoak(emaitza)

    if emaitza is not None and not emaitza.is_valid:
        try:
            emaitza = _soilik_poligonoak(emaitza.buffer(0))
        except Exception:
            pass

    return emaitza


def garbitu_geometriak(gdf, log, izena_testuingurua=""):
    """
    - Geometria nulu/hutsak kendu.
    - Baliogabeak zuzendu (make_valid).
    - Poligonala ez den guztia poligonalera murriztu edo kendu.
    """
    hasieran = len(gdf)

    maskara = gdf.geometry.notna() & ~gdf.geometry.is_empty
    kendutakoak = int(hasieran - maskara.sum())
    gdf = gdf[maskara].copy()

    if kendutakoak > 0:
        log.info(
            f"   {izena_testuingurua}: {kendutakoak} geometria "
            f"nulu/huts kenduta."
        )

    # Baliogabeak zuzendu
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
        log.info(
            f"   Zuzentzea: {formatu_denbora(time.perf_counter() - t0)}"
        )

    # Poligonala ez dena (lerroak, puntuak, kolekzioak) murriztu
    ez_poligonala = ~gdf.geometry.geom_type.isin(POLIGONALAK)
    ez_poligonalak = int(ez_poligonala.sum())
    if ez_poligonalak > 0:
        log.info(
            f"   {izena_testuingurua}: {ez_poligonalak} geometria ez "
            f"poligonal poligonalera murrizten (edo kentzen)."
        )
        gdf.loc[ez_poligonala, "geometry"] = gdf.loc[
            ez_poligonala, "geometry"
        ].apply(_soilik_poligonoak)

    # Zuzentzeak edo murrizteak hutsak sortu baditzake
    maskara2 = gdf.geometry.notna() & ~gdf.geometry.is_empty
    kendutakoak2 = int((~maskara2).sum())
    if kendutakoak2 > 0:
        gdf = gdf[maskara2].copy()
        log.info(
            f"   {izena_testuingurua}: {kendutakoak2} geometria "
            f"gehiago kenduta zuzentzearen/murriztearen ondoren."
        )

    return gdf, kendutakoak + kendutakoak2, zuzendutakoak


# ---------------------------------------------------------------------------
# Diferentzia azkarra
# ---------------------------------------------------------------------------
def _prozesatu(i):
    """
    Azpiko i. poligonoaren diferentzia kalkulatzen du. Fork-aren bidez
    heredatutako globalak erabiltzen ditu. None itzultzen du guztiz
    estalita badago.
    """
    geom = _AZPI[i]
    kandidatuak = _KAND[i]

    minx, miny, maxx, maxy = geom.bounds
    marjina = max(maxx - minx, maxy - miny) * MARGINA_ERATIOA + 1e-9

    ukitzaileak = []
    for k in kandidatuak:
        p = _PREP[k]
        if not p.intersects(geom):
            continue
        if p.covers(geom):
            return None  # guztiz estalita
        ukitzaileak.append(k)

    if not ukitzaileak:
        return geom

    # Trokela poligonoaren inguruko leihora moztu
    zatiak = []
    for k in ukitzaileak:
        z = clip_by_rect(
            _GAIN[k],
            minx - marjina, miny - marjina,
            maxx + marjina, maxy + marjina,
        )
        if z is not None and not z.is_empty:
            zatiak.append(z)

    if not zatiak:
        return geom

    try:
        trokela = unary_union(zatiak)
        emaitza = geom.difference(trokela)
    except Exception:
        # Ihesbidea: moztu gabeko geometria eta buffer(0) topologia
        # arazoetarako.
        try:
            trokela = unary_union(
                [_GAIN[k].buffer(0) for k in ukitzaileak]
            )
            emaitza = geom.buffer(0).difference(trokela)
        except Exception:
            return geom  # ezin izan da kalkulatu; aldatu gabe utzi

    return _soilik_poligonoak(emaitza)


def diferentzia_azkarra(gdf_azpi, gdf_gain, log):
    """
    Azpiko geometria bakoitzari gaineko geometrien diferentzia aplikatzen
    dio, indize espazialaz eta paralelizazioaz baliatuz.
    Itzulera: geometrien zerrenda (None = guztiz estalita), azpikoaren ordenan.
    """
    global _AZPI, _GAIN, _PREP, _KAND

    azpi = list(gdf_azpi.geometry.values)
    gain = list(gdf_gain.geometry.values)
    guztira = len(azpi)

    # --- Kandidatuak (bbox-ak ukitzen direnak), prozesu nagusian ---
    log.info("   Indize espaziala eraikitzen eta kandidatuak bilatzen...")
    t0 = time.perf_counter()
    sidx = gdf_gain.sindex

    kandidatuak = {}
    for i, g in enumerate(azpi):
        kk = list(sidx.intersection(g.bounds))
        if kk:
            kandidatuak[i] = kk

    log.info(
        f"   Kandidatuak: {formatu_denbora(time.perf_counter() - t0)} "
        f"({len(kandidatuak)}/{guztira} poligonok gainjartze posiblea dute)."
    )

    emaitza = list(azpi)  # lehenetsia: aldatu gabe
    indizeak = sorted(kandidatuak.keys())

    if not indizeak:
        return emaitza

    _AZPI = azpi
    _GAIN = gain
    _PREP = [prep(g) for g in gain]
    _KAND = kandidatuak

    nproc = PROZESU_KOPURUA
    if nproc is None:
        nproc = max(1, (os.cpu_count() or 2) - 1)
    nproc = max(1, min(nproc, len(indizeak)))

    fork_dago = "fork" in multiprocessing.get_all_start_methods()
    if nproc == 1 or not fork_dago:
        log.info(f"   Prozesu bakarra, {len(indizeak)} poligono...")
        iteratzailea = (_prozesatu(i) for i in indizeak)
        pool = None
    else:
        log.info(f"   {nproc} prozesu, {len(indizeak)} poligono...")
        ctx = multiprocessing.get_context("fork")
        pool = ctx.Pool(nproc)
        iteratzailea = pool.imap(_prozesatu, indizeak, CHUNKSIZE)

    try:
        zatia = max(1, (len(indizeak) * PROGRESO_ZATIA) // 100)
        t1 = time.perf_counter()
        for n, (i, geom) in enumerate(zip(indizeak, iteratzailea), 1):
            emaitza[i] = geom
            if n % zatia == 0:
                log.info(
                    f"   Progresua: {n}/{len(indizeak)} "
                    f"({100 * n // len(indizeak)}%) - "
                    f"{formatu_denbora(time.perf_counter() - t1)}"
                )
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    _AZPI = _GAIN = _PREP = _KAND = None
    return emaitza


# ---------------------------------------------------------------------------
# Prozesu nagusia
# ---------------------------------------------------------------------------
def trokelatu(gpkg_azpikoa, gpkg_gainekoa, gpkg_irteera, log):
    t_hasiera = time.perf_counter()

    irteera_geruza = geruza_izena(gpkg_irteera)

    # --- 0. Egiaztapenak ---
    for bidea in (gpkg_azpikoa, gpkg_gainekoa):
        if not os.path.isfile(bidea):
            raise FileNotFoundError(f"Ez da fitxategia aurkitu: {bidea}")

    abs_irteera = os.path.abspath(gpkg_irteera)
    if abs_irteera in (
        os.path.abspath(gpkg_azpikoa), os.path.abspath(gpkg_gainekoa)
    ):
        raise ValueError(
            "Irteerako fitxategia ezin da sarrerako bat izan."
        )

    geruza_azpi = _geruza_hautatu(gpkg_azpikoa)
    geruza_gain = _geruza_hautatu(gpkg_gainekoa)

    # --- 1. Azpikoa irakurri ---
    t0 = time.perf_counter()
    gdf_azpi = gpd.read_file(gpkg_azpikoa, layer=geruza_azpi)
    t_azpi = time.perf_counter() - t0
    log.info(
        f"Azpikoa kargatu: {formatu_denbora(t_azpi)} "
        f"({len(gdf_azpi)} elem.)"
    )

    if gdf_azpi.empty:
        raise ValueError(f"Azpiko GPKGa hutsik dago: {gpkg_azpikoa}")

    # --- 2. CRS-a egiaztatu BBOX iragazkia baino lehen ---
    crs_azpi = _lortu_crs(gpkg_azpikoa, geruza_azpi)
    crs_gain = _lortu_crs(gpkg_gainekoa, geruza_gain)

    if crs_azpi is None or crs_gain is None:
        raise ValueError("Geruzaren batek ez du CRSrik definituta.")

    crs_berdinak = _crs_berdinak(crs_azpi, crs_gain)
    bbox = tuple(gdf_azpi.total_bounds)  # (minx, miny, maxx, maxy)

    # --- 3. Gainekoa irakurri ---
    t0 = time.perf_counter()
    if crs_berdinak:
        gdf_gain = gpd.read_file(
            gpkg_gainekoa, layer=geruza_gain, bbox=bbox
        )
    else:
        gdf_gain = gpd.read_file(gpkg_gainekoa, layer=geruza_gain)
    t_gain = time.perf_counter() - t0
    log.info(
        f"Gainekoa kargatu: {formatu_denbora(t_gain)} "
        f"({len(gdf_gain)} elem.)"
    )

    # --- 4. CRS-a bateratu (behar bada) eta bbox-ez iragazi ---
    if not crs_berdinak and not gdf_gain.empty:
        log.abisua(
            f"CRS desberdinak. Gainekoa {crs_gain}-tik "
            f"{crs_azpi}-ra birproiektatzen."
        )
        t0 = time.perf_counter()
        gdf_gain = gdf_gain.to_crs(gdf_azpi.crs)
        log.info(
            f"   Birproiekzioa: {formatu_denbora(time.perf_counter() - t0)}"
        )
        minx, miny, maxx, maxy = bbox
        gdf_gain = gdf_gain.cx[minx:maxx, miny:maxy].copy()
        log.info(f"   BBOX iragazkia: {len(gdf_gain)} elem. geratzen dira.")

    # --- 5. Geometriak garbitu ---
    log.info("Geometriak garbitzen...")
    t0 = time.perf_counter()
    if not gdf_gain.empty:
        gdf_gain, _, _ = garbitu_geometriak(gdf_gain, log, "gainekoa")
    gdf_azpi, _, _ = garbitu_geometriak(gdf_azpi, log, "azpikoa")
    log.info(f"Garbiketa: {formatu_denbora(time.perf_counter() - t0)}")

    if gdf_azpi.empty:
        raise ValueError(
            "Azpiko GPKGan ez da geometria baliodunik geratzen."
        )

    # --- 6. Diferentzia ---
    if gdf_gain.empty:
        log.abisua(
            "Gainekoak ez du geometriarik azpikoaren eremuan (edo "
            "garbiketaren ondoren hutsik dago). Ez da ezer trokelatuko."
        )
        gdf_out = gdf_azpi.copy()
    else:
        log.info("Diferentzia...")
        t0 = time.perf_counter()
        emaitza = diferentzia_azkarra(gdf_azpi, gdf_gain, log)
        gdf_out = gdf_azpi.copy()
        gdf_out["geometry"] = emaitza
        log.info(f"Diferentzia: {formatu_denbora(time.perf_counter() - t0)}")

    # --- 7. Geometria hutsak / nuluak ezabatu ---
    aurretik = len(gdf_out)
    mask = gdf_out.geometry.notna() & ~gdf_out.geometry.is_empty
    gdf_out = gdf_out[mask]
    ondoren = len(gdf_out)
    log.info(
        f"Elementuak: {aurretik} -> {ondoren} "
        f"({aurretik - ondoren} ezabatu dira guztiz estalita zeudelako)."
    )

    if gdf_out.empty:
        log.abisua(
            "Emaitza hutsik dago; trokelak azpikoa guztiz estaltzen du."
        )

    # --- 8. Aukerakoa: MultiPolygon bihurtu ---
    if BIHURTU_MULTI and not gdf_out.empty:
        gdf_out = gdf_out.copy()
        gdf_out["geometry"] = gdf_out.geometry.apply(
            lambda g: MultiPolygon([g]) if g.geom_type == "Polygon" else g
        )

    # --- 9. 'fid' zaharra kendu, berria sortu ---
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

    # --- 10. Emaitza gorde (atomikoki) ---
    tmp_irteera = gpkg_irteera + ".tmp"
    if os.path.exists(tmp_irteera):
        os.remove(tmp_irteera)

    t0 = time.perf_counter()
    gdf_out.to_file(tmp_irteera, layer=irteera_geruza, driver="GPKG")
    t_idazketa = time.perf_counter() - t0

    os.replace(tmp_irteera, gpkg_irteera)

    log.info(f"Idazketa: {formatu_denbora(t_idazketa)}")
    log.info(f"Gordeta: {gpkg_irteera} (geruza: '{irteera_geruza}')")

    # --- Guztizko denbora ---
    t_guzti = time.perf_counter() - t_hasiera
    log.info("-" * 50)
    log.info(f"Guztizko denbora: {formatu_denbora(t_guzti)}")


def main():
    script_izena = os.path.basename(sys.argv[0]) or "vt_trokelatu2.py"

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
