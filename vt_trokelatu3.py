#!/usr/bin/env python3
"""
Bi GPKG poligonen arteko trokelatzea, 10x10 km-ko laukien bidez eta
«type» eremuaren arabera disolbatuta (eremu hori badago soilik).

=============================================================================
SARRERA / IRTEERA
=============================================================================
Sarrera:
  - GPKG_A (azpikoa): oinarrizko poligonoak eta haien atributuak.
                      'type' eremua (EREMU_DISOLBA) aukerakoa da: badago,
                      emaitza disolbatu egiten da; ez badago, ez da
                      disolbatzen.
  - GPKG_B (gainekoa): trokel gisa jokatzen duten poligonoak.

Irteera (bi modu, A-n 'type' eremua dagoen ala ez):
  - 'type' BADAGO -> DISOLBATUTAKO modua: (A ken B) diferentzia espaziala,
    'type' eremuaren arabera disolbatuta. Elementu bat 'type' balio
    bakoitzeko (geometria MultiPolygon izan ohi da). Eremuak: 'fid'
    (1, 2, 3, ...), 'type' eta geometria. A-ren gainerako atributuak ez
    dira mantentzen, disoluzioan zentzurik ez dutelako.
  - 'type' EZ BADAGO -> EZ DISOLBATU modua: (A ken B) diferentzia
    espaziala, A-ren elementu bakoitza bere aldetik. A-ren atributu guztiak
    mantentzen dira ('fid' izan ezik; 'fid' berria sortzen da). Guztiz
    estalitako elementuak ezabatzen dira. Elementu bakoitzaren laukiko
    zatiak elementu bakarrean berriro batzen dira (laukien mugak ez dira
    ikusten).

Erabilera:
  python3 <scripta> azpikoa.gpkg gainekoa.gpkg irteera.gpkg [log_fitxategia]

  log_fitxategia aukerakoa da:
    - ematen bada: mezuak log fitxategira (eta terminalera TTY bada)
    - ez bada ematen: mezuak terminalera soilik (TTY bada)

=============================================================================
ALGORITMOA (urratsez urrats)
=============================================================================
Ideia nagusia: diferentzia espaziala ez da geometria osoekin egiten
(poligono handiak + trokel konplexuak = motela), baizik eta 10x10 km-ko
lauki erregular batean zatituta. Lauki bakoitza lan-unitate independente
bat da, eta prozesu anitzetan bana daiteke. Azkenean laukien emaitzak
elkartu eta 'type' arabera disolbatzen dira; disoluzioak laukien arteko
mugak ezabatzen ditu.

  0. Egiaztapenak: sarrerako fitxategiak existitzen dira, irteera ez da
     sarrera bat, eta fitxategi izen bereko geruza hautatzen da (bestela
     lehen geruza).

  1. A irakurri eta 'type' eremua badagoela egiaztatu.

  2. CRS-ak egiaztatu (A eta B). Berdinak badira, B irakurtzean A-ren
     MBR-ak (bbox) iragazten du fitxategitik bertatik (azkarragoa). Ez
     badira berdinak, B osorik irakurri, A-ren CRS-ra birproiektatu eta
     gero iragazi.

  3. Geometriak garbitu (A eta B): nuluak/hutsak kendu, baliogabeak
     zuzendu (make_valid) eta poligonala ez dena murriztu/kendu.
     clip_by_rect eta difference eragiketek geometria baliodunak behar
     dituzte. Kendutako A elementuak logean zehazten dira (haien
     atributuak irteeran ez daude).

  4. LAUKIA DISEINATU: A-ren MBR-a (garbiketaren ondorengo total_bounds)
     hartu eta MBR horren ezkerreko-beheko izkinatik hasita LAUKI_TAMAINA
     (10 000 m) aldeko laukiz estali. Lauki kopurua:
         nx = ceil(zabalera / 10000),  ny = ceil(altuera / 10000).
     Laukien koordenatuak 'hasiera + i*tamaina' gisa kalkulatzen dira
     (ez metatuz), beraz auzoko bi laukik muga-koordenatu BERDINA
     partekatzen dute bit mailan. Hori ezinbestekoa da 8. urratseko
     disoluzioak mugak zehatz itsats ditzan.

  5. Lauki bakoitzeko kandidatuak (prozesu nagusian, indize
     espazialarekin): lauki bakoitzaren bbox-a ukitzen duten A eta B
     geometrien indizeak. A kandidaturik gabeko laukiak baztertzen dira.
     Laukiak lan-kargaren arabera (A+B kandidatuak) handienetik txikienera
     ordenatzen dira, prozesuen artean karga hobeto orekatzeko.

  6. Lauki bakoitzaren kalkulua (prozesu anitzetan, fork):
       6.1. B kandidatu bakoitza laukira moztu (clip_by_rect) eta
            laukiaren TROKEL bakarrean batu (unary_union). Trokela
            laukiaren barruan soilik existitzen da.
       6.2. A kandidatu bakoitza laukira moztu (clip_by_rect). Hori da
            A-ren 'zatia' lauki horretan.
       6.3. Zati bakoitzarentzat:
              - trokelak ez badu ukitzen  -> zatia aldatu gabe geratzen da.
              - trokelak guztiz estaltzen badu (prep.covers) -> ezabatu.
              - bestela: trokela zatiaren bbox-era (+ marjina) moztu eta
                diferentzia txiki horrekin kalkulatu.
       Zati eta trokel biak laukira mozturik daudenez, emaitza zehatza da:
       (A ken B) ∩ lauki.

  7. Laukien emaitzak bildu: (A-ren indizea, geometria) bikoteak
     taldekatu. Taldekatze-gakoa:
       - 'type' badago: A-ren 'type' balioa (DISOLBATUTAKO modua).
       - 'type' ez badago: A-ren elementuaren indizea (EZ DISOLBATU modua).

  8. BATZEA: talde bakoitzeko zati guztiak unary_union-ekin batu.
       - DISOLBATUTAKO moduan, horrek (a) laukien arteko mugak ezabatzen
         ditu eta (b) 'type' bereko poligono ukitzaileak/gainjarriak
         bateratzen ditu.
       - EZ DISOLBATU moduan, A-ren elementu bakoitzaren zatiak soilik
         berriro itsasten dira (laukien mugak ezabatzeko); ez da inolako
         elementurik bateratzen.
     Taldeak prozesu anitzetan banatzen dira.

  9. Irteera osatu:
       - DISOLBATUTAKO moduan: 'fid' berria, 'type' eta geometria.
       - EZ DISOLBATU moduan: A-ren atributu guztiak (jatorrizko ordenan,
         'fid' berriarekin) eta geometria berria.
     Aukeran MultiPolygon-era bihurtu (BIHURTU_MULTI) eta GPKG-ra idatzi
     (atomikoki: '.tmp.gpkg' fitxategi tenporala + os.replace).

=============================================================================
OHARRAK
=============================================================================
  - Python 3.6+, Shapely 1.8.x eta 2.x-rekin bateragarria. Prozesu anitzak
    'fork' bidez (Linux); fork ez badago, prozesu bakarrean exekutatzen da.
  - 'type' eremua ez badago, ez da errorerik ematen: abisu bat idazten da
    eta EZ DISOLBATU moduan exekutatzen da.
  - 'type' balio nuluak talde propio gisa tratatzen dira (ez dira galtzen).
  - Laukien mugetan clip_by_rect-ek erpin berriak sortzen ditu. Auzoko
    laukietan kalkulu berdina egiten denez, disoluzioak ondo itsasten ditu;
    hala ere, koma higikorraren errore mikroskopikoak hutsune/sliver
    txikiak utz ditzake mugetan (oso arraroa). Horrelakorik ikusiz gero,
    emaitzaren azken garbiketa gehitu daiteke (area minimoaren iragazkia).
  - Diferentziak ez du tolerantziarik: A eta B-ren ertz ia-bateratuek
    sliver txikiak sor ditzakete.
"""

import sys
import os
import math
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
LAUKI_TAMAINA = 10000.0   # Laukiaren aldea, CRS-aren unitatetan (EPSG:25830 -> m)
EREMU_DISOLBA = "type"    # Disoluzio-eremua (A-ren atributu bat)
PROZESU_KOPURUA = None    # None = CPU kopurua - 1 (gutxienez 1)
MARGINA_ERATIOA = 0.05    # Trokela zatira mozteko marjina (zatiaren tamainaren zatiki)
BIHURTU_MULTI = True      # True: irteerako geometria guztiak MultiPolygon
PROGRESO_ZATIA = 10       # logean progresua zenbat %-ro idatzi

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

# Prozesu-bikoteen artean partekatutako datuak. 'fork' bidez heredatzen dira
# (ez dira kopiatzen ez serializatzen), beraz prozesuak abiarazi AURRETIK
# bete behar dira.
_AZPI = None      # A-ren geometrien zerrenda
_GAIN = None      # B-ren geometrien zerrenda
_LAUKIAK = None   # [(minx, miny, maxx, maxy), ...]
_LAUKI_A = None   # {lauki indizea: [A kandidatuen indizeak]}
_LAUKI_B = None   # {lauki indizea: [B kandidatuen indizeak]}
_TALDEAK = None   # [(type balioa, [geometriak]), ...] disoluziorako


# ---------------------------------------------------------------------------
# Laguntzaileak: denbora, geruzak, CRS-a
# ---------------------------------------------------------------------------
def formatu_denbora(segundoak):
    """Segundoak testu irakurgarri bihurtzen ditu (s / m s / h m s)."""
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
    """Fitxategi izenetik '.gpkg' luzapena kenduta geruza izena lortzen du."""
    izena = os.path.basename(gpkg_bidea)
    if izena.lower().endswith(".gpkg"):
        izena = izena[:-5]
    return izena


def _geruza_hautatu(gpkg_bidea, log):
    """
    Fitxategi izen bereko geruza badago, hura erabiltzen da; bestela None
    (GeoPandas-ek lehen geruza irakurriko du). Erabilitako geruza logean
    idazten da, eta geruza anitz badaude baina bat ere ez badator bat,
    abisua ematen da.
    """
    try:
        import fiona
        geruzak = fiona.listlayers(gpkg_bidea)
    except Exception:
        log.info(f"   {os.path.basename(gpkg_bidea)}: geruza lehenetsia.")
        return None

    izena = geruza_izena(gpkg_bidea)
    if izena in geruzak:
        log.info(f"   {os.path.basename(gpkg_bidea)}: geruza '{izena}'.")
        return izena

    if len(geruzak) > 1:
        log.abisua(
            f"{os.path.basename(gpkg_bidea)}: geruza anitz {geruzak}, "
            f"baina bat ere ez dator fitxategi izenarekin; lehena erabiliko da."
        )
    return None


def _lortu_crs(gpkg_bidea, geruza=None):
    """GPKG baten CRS-a irakurtzen du, geometria guztia kargatu gabe."""
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


# ---------------------------------------------------------------------------
# Laguntzaileak: geometria garbiketa
# ---------------------------------------------------------------------------
def _soilik_poligonoak(geom):
    """
    Geometria poligonalera murrizten du: Polygon/MultiPolygon bere horretan,
    kolekzioetatik poligonoak soilik; gainerakoa (lerroak, puntuak) eta
    geometria hutsak None bihurtzen dira.
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
    GeoDataFrame bateko geometriak garbitzen ditu:
      - nulu/hutsak kendu,
      - baliogabeak zuzendu (make_valid),
      - poligonala ez dena poligonalera murriztu edo kendu.
    Itzulera: (gdf garbia, kendutako elementuak, zuzendutako elementuak).
    """
    hasieran = len(gdf)

    # 1) Nulu/hutsak
    maskara = gdf.geometry.notna() & ~gdf.geometry.is_empty
    kendutakoak = int(hasieran - maskara.sum())
    gdf = gdf[maskara].copy()
    if kendutakoak > 0:
        log.info(
            f"   {izena_testuingurua}: {kendutakoak} geometria "
            f"nulu/huts kenduta."
        )

    # 2) Baliogabeak zuzendu
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

    # 3) Poligonala ez dena murriztu
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

    # 4) Zuzentzeak/murrizteak hutsak sortu baditzake
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
# Laukia (grid-a)
# ---------------------------------------------------------------------------
def sortu_laukiak(bounds, tamaina):
    """
    MBR bat (minx, miny, maxx, maxy) 'tamaina' aldeko laukiz estaltzen du,
    MBR-aren ezkerreko-beheko izkinatik hasita.

    Lauki bakoitzaren koordenatuak 'hasiera + i*tamaina' bezala kalkulatzen
    dira (batuketa metatuaren ordez), horrela auzoko bi laukik muga-
    koordenatu BERDINA dute (bit mailan). Hori beharrezkoa da disoluzioak
    laukien arteko mugak garbi itsats ditzan.

    Itzulera: (laukiak, nx, ny); laukiak = [(minx, miny, maxx, maxy), ...]
    errenkadaka (hegotik iparrera, mendebaldetik ekialdera).
    """
    minx, miny, maxx, maxy = bounds

    nx = max(1, int(math.ceil((maxx - minx) / tamaina)))
    ny = max(1, int(math.ceil((maxy - miny) / tamaina)))
    # Koma higikorraren zehaztasunaren aurkako segurtasuna: laukiak MBR osoa
    # estali behar du.
    while minx + nx * tamaina < maxx:
        nx += 1
    while miny + ny * tamaina < maxy:
        ny += 1

    laukiak = []
    for j in range(ny):
        for i in range(nx):
            laukiak.append((
                minx + i * tamaina,
                miny + j * tamaina,
                minx + (i + 1) * tamaina,
                miny + (j + 1) * tamaina,
            ))
    return laukiak, nx, ny


# ---------------------------------------------------------------------------
# Lauki bakoitzaren kalkulua (prozesu-bikote bakoitzean exekutatzen da)
# ---------------------------------------------------------------------------
def _prozesatu_laukia(k):
    """
    k. laukiaren (A ken B) diferentzia kalkulatzen du. 'fork'-ean
    heredatutako globalak erabiltzen ditu.

    Itzulera: (k, [(A-ren indizea, geometria), ...], akatsak)
      - Zerrendak A-ren zatiak ditu laukiaren barruan, trokelatuta
        (guztiz estalitakoak ez dira agertzen).
      - 'akatsak': diferentzia kalkulatu ezinik zatia aldatu gabe utzi den
        aldiak (logean abisatzeko).
    """
    lauki = _LAUKIAK[k]
    a_ids = _LAUKI_A[k]
    b_ids = _LAUKI_B[k]
    akatsak = 0

    # 6.1. TROKELA: B kandidatuak laukira moztu eta batu.
    # clip_by_rect azkarra da (ez du topologia osoa kalkulatzen).
    zatiak_b = []
    for b in b_ids:
        z = _soilik_poligonoak(clip_by_rect(_GAIN[b], *lauki))
        if z is not None:
            zatiak_b.append(z)

    trokela = None
    p_trokela = None
    if zatiak_b:
        try:
            trokela = unary_union(zatiak_b)
        except Exception:
            trokela = unary_union([z.buffer(0) for z in zatiak_b])
        if trokela is not None and not trokela.is_empty:
            p_trokela = prep(trokela)   # predikatu azkarrak (intersects/covers)
        else:
            trokela = None

    emaitza = []
    for a in a_ids:
        # 6.2. A-ren zatia laukian.
        # Laukiaren ertzean ukitzen duen geometriak lerro/puntu hutsak sor
        # ditzake; _soilik_poligonoak-ek baztertzen ditu.
        zatia = _soilik_poligonoak(clip_by_rect(_AZPI[a], *lauki))
        if zatia is None:
            continue

        # 6.3. Diferentzia.
        if p_trokela is None or not p_trokela.intersects(zatia):
            emaitza.append((a, zatia))          # trokelik gabe: aldatu gabe
            continue
        if p_trokela.covers(zatia):
            continue                            # guztiz estalita: ezabatu

        # Trokela zatiaren inguruko leihora moztu (diferentzia txikiagoa).
        minx, miny, maxx, maxy = zatia.bounds
        marjina = max(maxx - minx, maxy - miny) * MARGINA_ERATIOA + 1e-9
        t = _soilik_poligonoak(clip_by_rect(
            trokela,
            minx - marjina, miny - marjina,
            maxx + marjina, maxy + marjina,
        ))
        if t is None:
            emaitza.append((a, zatia))
            continue

        try:
            r = zatia.difference(t)
        except Exception:
            # Ihesbidea: buffer(0) topologia arazoetarako.
            try:
                r = zatia.buffer(0).difference(t.buffer(0))
            except Exception:
                akatsak += 1
                emaitza.append((a, zatia))      # ezin izan da; aldatu gabe
                continue

        r = _soilik_poligonoak(r)
        if r is not None:
            emaitza.append((a, r))

    return (k, emaitza, akatsak)


# ---------------------------------------------------------------------------
# Disoluzioa (prozesu-bikote bakoitzean exekutatzen da)
# ---------------------------------------------------------------------------
def _disolbatu_taldea(t):
    """
    t. 'type' taldeko geometria guztiak batasun bakarrean batzen ditu.
    Laukien arteko mugak ezabatzen dira, eta ukitzen/gainjartzen diren
    poligonoak bateratzen dira. Itzulera: (t, geometria | None).
    """
    geometriak = _TALDEAK[t][1]
    try:
        g = unary_union(geometriak)
    except Exception:
        g = unary_union([x.buffer(0) for x in geometriak])
    return (t, _soilik_poligonoak(g))


# ---------------------------------------------------------------------------
# Paralelizazio laguntzailea
# ---------------------------------------------------------------------------
def _exekutatu(funtzioa, zereginak, log, etiketa):
    """
    'funtzioa' zeregin bakoitzari aplikatzen dio, prozesu anitzetan ('fork')
    edo, aukerarik ez badago, prozesu bakarrean. Emaitzak zereginen
    ordenan itzultzen ditu. Progresua logean idazten du.

    Arazo batean (edo Ctrl-C-n) pool-a 'terminate()'-rekin hiltzen da,
    geratzen den lan guztiaren zain egon gabe.
    """
    guztira = len(zereginak)
    emaitzak = []
    if guztira == 0:
        return emaitzak

    nproc = PROZESU_KOPURUA
    if nproc is None:
        nproc = max(1, (os.cpu_count() or 2) - 1)
    nproc = max(1, min(nproc, guztira))

    fork_dago = "fork" in multiprocessing.get_all_start_methods()
    pool = None
    if nproc == 1 or not fork_dago:
        log.info(f"   {etiketa}: prozesu bakarra, {guztira} zeregin...")
        iteratzailea = map(funtzioa, zereginak)
    else:
        log.info(f"   {etiketa}: {nproc} prozesu, {guztira} zeregin...")
        ctx = multiprocessing.get_context("fork")
        pool = ctx.Pool(nproc)
        # chunksize=1: zeregin bakoitza astuna da (lauki osoa / type osoa).
        iteratzailea = pool.imap(funtzioa, zereginak, 1)

    try:
        zatia = max(1, (guztira * PROGRESO_ZATIA) // 100)
        t1 = time.perf_counter()
        for n, emaitza in enumerate(iteratzailea, 1):
            emaitzak.append(emaitza)
            if n % zatia == 0:
                log.info(
                    f"   {etiketa}: {n}/{guztira} ({100 * n // guztira}%) - "
                    f"{formatu_denbora(time.perf_counter() - t1)}"
                )
    except BaseException:
        if pool is not None:
            pool.terminate()
        raise
    else:
        if pool is not None:
            pool.close()
    finally:
        if pool is not None:
            pool.join()

    return emaitzak


def _type_gakoa(balioa):
    """
    'type' balioa taldekatzeko gako segurua bihurtzen du: NaN/None -> None
    (NaN != NaN denez, dict gako gisa arazoak emango lituzke).
    """
    if balioa is None or balioa != balioa:
        return None
    return balioa


# ---------------------------------------------------------------------------
# Prozesu nagusia
# ---------------------------------------------------------------------------
def trokelatu(gpkg_azpikoa, gpkg_gainekoa, gpkg_irteera, log):
    global _AZPI, _GAIN, _LAUKIAK, _LAUKI_A, _LAUKI_B, _TALDEAK

    t_hasiera = time.perf_counter()
    irteera_geruza = geruza_izena(gpkg_irteera)

    # --- 0. Egiaztapenak -------------------------------------------------
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

    geruza_azpi = _geruza_hautatu(gpkg_azpikoa, log)
    geruza_gain = _geruza_hautatu(gpkg_gainekoa, log)

    # --- 1. A irakurri eta 'type' eremua egiaztatu -------------------------
    t0 = time.perf_counter()
    gdf_azpi = gpd.read_file(gpkg_azpikoa, layer=geruza_azpi)
    log.info(
        f"Azpikoa kargatu: {formatu_denbora(time.perf_counter() - t0)} "
        f"({len(gdf_azpi)} elem.)"
    )

    if gdf_azpi.empty:
        raise ValueError(f"Azpiko GPKGa hutsik dago: {gpkg_azpikoa}")

    # Modua: 'type' eremua badago disolbatu egiten da; bestela ez.
    disolbatu = EREMU_DISOLBA in gdf_azpi.columns
    if disolbatu:
        log.info(f"'{EREMU_DISOLBA}' eremua aurkitu da: emaitza disolbatuko da.")
    else:
        log.abisua(
            f"Azpiko GPKGak ez du '{EREMU_DISOLBA}' eremurik: ez da "
            f"disolbatuko. A-ren elementu bakoitza bere aldetik trokelatuko "
            f"da, atributuak mantenduz. Eremuak: "
            f"{[c for c in gdf_azpi.columns if c != 'geometry']}"
        )

    # --- 2. CRS-ak egiaztatu (bbox iragazkia baino lehen) ----------------
    crs_azpi = _lortu_crs(gpkg_azpikoa, geruza_azpi)
    crs_gain = _lortu_crs(gpkg_gainekoa, geruza_gain)

    if crs_azpi is None or crs_gain is None:
        raise ValueError("Geruzaren batek ez du CRSrik definituta.")

    crs_berdinak = _crs_berdinak(crs_azpi, crs_gain)
    bbox = tuple(gdf_azpi.total_bounds)  # (minx, miny, maxx, maxy)

    # --- 3. B irakurri ----------------------------------------------------
    # CRS berdinak: fitxategitik bertatik A-ren bbox-ez iragazi (azkarra).
    # Desberdinak: osorik irakurri eta 4. urratsean birproiektatu/iragazi.
    t0 = time.perf_counter()
    if crs_berdinak:
        gdf_gain = gpd.read_file(
            gpkg_gainekoa, layer=geruza_gain, bbox=bbox
        )
    else:
        gdf_gain = gpd.read_file(gpkg_gainekoa, layer=geruza_gain)
    log.info(
        f"Gainekoa kargatu: {formatu_denbora(time.perf_counter() - t0)} "
        f"({len(gdf_gain)} elem.)"
    )

    # --- 4. CRS-a bateratu (behar bada) eta bbox-ez iragazi ----------------
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

    # --- 5. Geometriak garbitu -------------------------------------------
    log.info("Geometriak garbitzen...")
    t0 = time.perf_counter()
    if not gdf_gain.empty:
        gdf_gain, _, _ = garbitu_geometriak(gdf_gain, log, "gainekoa")
    gdf_azpi, azpi_kendutakoak, _ = garbitu_geometriak(
        gdf_azpi, log, "azpikoa"
    )
    log.info(f"Garbiketa: {formatu_denbora(time.perf_counter() - t0)}")

    if azpi_kendutakoak > 0:
        log.abisua(
            f"Azpikoaren {azpi_kendutakoak} elementu kendu dira garbiketan "
            f"(geometria baliogabe/hutsa); ez dira irteeran agertuko."
        )

    if gdf_azpi.empty:
        raise ValueError(
            "Azpiko GPKGan ez da geometria baliodunik geratzen."
        )

    # --- 6. LAUKIA diseinatu A-ren MBR-aren arabera -------------------------
    # MBR-a garbiketaren ondoren hartzen da: kendutako geometriek ez dute
    # irteeran parte hartuko, beraz ez dute laukia handitu behar.
    mbr = tuple(gdf_azpi.total_bounds)
    laukiak, nx, ny = sortu_laukiak(mbr, LAUKI_TAMAINA)
    log.info(
        f"Laukia: MBR = ({mbr[0]:.2f}, {mbr[1]:.2f}, {mbr[2]:.2f}, "
        f"{mbr[3]:.2f}); {nx} x {ny} = {len(laukiak)} lauki "
        f"({LAUKI_TAMAINA:g} x {LAUKI_TAMAINA:g})."
    )

    # --- 7. Lauki bakoitzeko kandidatuak (indize espazialarekin) --------------
    # Prozesu nagusian egiten da, 'fork'-aren aurretik: indizea ez da
    # prozesuen artean partekatu behar.
    azpi = list(gdf_azpi.geometry.values)
    gain = list(gdf_gain.geometry.values)
    tipoak = None
    if disolbatu:
        tipoak = [_type_gakoa(v) for v in gdf_azpi[EREMU_DISOLBA].values]

    log.info("Lauki bakoitzeko kandidatuak bilatzen...")
    t0 = time.perf_counter()
    sidx_a = gdf_azpi.sindex
    sidx_b = gdf_gain.sindex if gain else None

    lauki_a = {}
    lauki_b = {}
    for k, lauki in enumerate(laukiak):
        a_ids = list(sidx_a.intersection(lauki))
        if not a_ids:
            continue  # A-rik gabeko laukia: ez dago zer kalkulatu
        lauki_a[k] = a_ids
        lauki_b[k] = list(sidx_b.intersection(lauki)) if sidx_b else []
    log.info(
        f"   Kandidatuak: {formatu_denbora(time.perf_counter() - t0)} "
        f"({len(lauki_a)}/{len(laukiak)} laukik A dute)."
    )

    # Lan-kargaren arabera ordenatu (handienak lehenik) prozesuen oreka
    # hobetzeko.
    zereginak = sorted(
        lauki_a.keys(),
        key=lambda k: len(lauki_a[k]) + len(lauki_b[k]),
        reverse=True,
    )

    # --- 8. Laukien kalkulua prozesu anitzetan ----------------------------
    log.info("Diferentzia laukika...")
    t0 = time.perf_counter()
    _AZPI, _GAIN = azpi, gain
    _LAUKIAK, _LAUKI_A, _LAUKI_B = laukiak, lauki_a, lauki_b
    try:
        emaitzak = _exekutatu(_prozesatu_laukia, zereginak, log, "Laukiak")
    finally:
        _AZPI = _GAIN = _LAUKIAK = _LAUKI_A = _LAUKI_B = None

    # --- 9. Zatiak taldekatu ------------------------------------------------
    # Gakoa: 'type' balioa (disolbatu) edo A-ren indizea (ez disolbatu).
    taldeak = {}
    zati_guztira = 0
    akats_guztira = 0
    for _, zatiak, akatsak in emaitzak:
        akats_guztira += akatsak
        for a, geom in zatiak:
            gakoa = tipoak[a] if disolbatu else a
            taldeak.setdefault(gakoa, []).append(geom)
            zati_guztira += 1

    if akats_guztira > 0:
        log.abisua(
            f"{akats_guztira} zatitan diferentzia ezin izan da kalkulatu; "
            f"zati horiek trokelatu gabe geratu dira."
        )
    log.info(
        f"Diferentzia laukika: {formatu_denbora(time.perf_counter() - t0)} "
        f"({zati_guztira} zati, {len(taldeak)} "
        f"{'type balio' if disolbatu else 'azpiko elementu'})."
    )

    if not taldeak:
        log.abisua(
            "Emaitza hutsik dago; trokelak azpikoa guztiz estaltzen du."
        )

    # --- 10. BATZEA: disoluzioa ('type') edo elementu bakoitzaren zatiak ----
    # Taldeak ordenatzen dira irteera deterministikoa izan dadin: 'type'
    # moduan balioaren arabera (None azkenik); bestela A-ren jatorrizko
    # ordenan (indizea).
    if disolbatu:
        taldeak_zerrenda = sorted(
            taldeak.items(), key=lambda kv: (kv[0] is None, str(kv[0]))
        )
        log.info(f"Disoluzioa ('{EREMU_DISOLBA}' arabera)...")
    else:
        taldeak_zerrenda = sorted(taldeak.items(), key=lambda kv: kv[0])
        log.info("Elementu bakoitzaren zatiak batzen (disoluziorik gabe)...")
    t0 = time.perf_counter()
    _TALDEAK = taldeak_zerrenda
    try:
        # Zeregin handienak (zati gehien dituztenak) lehenik.
        disoluzio_zereginak = sorted(
            range(len(taldeak_zerrenda)),
            key=lambda t: len(taldeak_zerrenda[t][1]),
            reverse=True,
        )
        disolbatuak = _exekutatu(
            _disolbatu_taldea, disoluzio_zereginak, log, "Disoluzioa"
        )
    finally:
        _TALDEAK = None
    log.info(f"Disoluzioa: {formatu_denbora(time.perf_counter() - t0)}")

    # Taldeen ordena berreskuratu (disolbatuak ordena desberdinean etor
    # daitezke).
    disolbatuak.sort(key=lambda p: p[0])
    irteera_gakoak = []   # 'type' balioak (disolbatu) edo A-ren indizeak
    irteera_geom = []
    for t, geom in disolbatuak:
        if geom is None or geom.is_empty:
            continue
        irteera_gakoak.append(taldeak_zerrenda[t][0])
        irteera_geom.append(geom)

    # --- 11. Irteera osatu -----------------------------------------------
    if BIHURTU_MULTI:
        irteera_geom = [
            MultiPolygon([g]) if g.geom_type == "Polygon" else g
            for g in irteera_geom
        ]

    if disolbatu:
        # Eremuak: fid, type, geometry.
        gdf_out = gpd.GeoDataFrame(
            {
                "fid": list(range(1, len(irteera_geom) + 1)),
                EREMU_DISOLBA: irteera_gakoak,
                "geometry": irteera_geom,
            },
            geometry="geometry",
            crs=gdf_azpi.crs,
        )
        log.info(
            f"Elementuak: {len(gdf_azpi)} (azpikoa) -> {len(gdf_out)} "
            f"(disolbatuta, '{EREMU_DISOLBA}' balio bakoitzeko bat)."
        )
    else:
        # A-ren atributu guztiak mantendu (irteeran geratzen diren
        # elementuenak, jatorrizko ordenan) eta 'fid' berria sortu.
        gdf_out = gdf_azpi.iloc[irteera_gakoak].copy()
        gdf_out["geometry"] = irteera_geom
        gdf_out = gdf_out.reset_index(drop=True)
        if "fid" in gdf_out.columns:
            gdf_out = gdf_out.drop(columns=["fid"])
            log.info("'fid' zaharra kendu da azpiko GPKGtik.")
        gdf_out.insert(0, "fid", range(1, len(gdf_out) + 1))
        zutabeak = [c for c in gdf_out.columns if c != "geometry"]
        gdf_out = gdf_out[zutabeak + ["geometry"]].set_geometry("geometry")
        log.info(
            f"Elementuak: {len(gdf_azpi)} (azpikoa) -> {len(gdf_out)} "
            f"({len(gdf_azpi) - len(gdf_out)} ezabatu dira guztiz "
            f"estalita zeudelako)."
        )
    log.info(f"Eremuak: {list(gdf_out.columns)}")

    # --- 12. Emaitza gorde (atomikoki) -----------------------------------
    # Lehenik fitxategi tenporalean idazten da; ondoren os.replace-ek
    # ordezkatzen du. Horrela, huts egiten badu ez da lehengo irteera
    # hondatzen.
    tmp_irteera = gpkg_irteera + ".tmp.gpkg"
    if os.path.exists(tmp_irteera):
        os.remove(tmp_irteera)

    t0 = time.perf_counter()
    gdf_out.to_file(tmp_irteera, layer=irteera_geruza, driver="GPKG")
    t_idazketa = time.perf_counter() - t0

    os.replace(tmp_irteera, gpkg_irteera)

    log.info(f"Idazketa: {formatu_denbora(t_idazketa)}")
    log.info(f"Gordeta: {gpkg_irteera} (geruza: '{irteera_geruza}')")

    # --- Guztizko denbora ---
    log.info("-" * 50)
    log.info(
        f"Guztizko denbora: "
        f"{formatu_denbora(time.perf_counter() - t_hasiera)}"
    )


def main():
    script_izena = os.path.basename(sys.argv[0]) or "vt_trokelatu3.py"

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
