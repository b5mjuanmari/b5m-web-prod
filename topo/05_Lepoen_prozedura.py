#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import geopandas as gpd
import rasterio

from rtree import index
from datetime import datetime

# --------------------------------------------------
# GERUZAK
# --------------------------------------------------

RUTA_ORIGEN = "/home5/SHP/Tiles/r_oronimia_p.shp"

RUTA_MDT = "/home9/terrain/MDT2017_01_25830_COG.tif"

RUTA_DESTINO = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

origen = gpd.read_file(RUTA_ORIGEN)

destino = gpd.read_file(RUTA_DESTINO)

mdt = rasterio.open(RUTA_MDT)

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# --------------------------------------------------
# HASIERA
# --------------------------------------------------

log(sys.argv[0])
log("Prozesuaren hasiera")

# CRS bateratu

if origen.crs != destino.crs:

    origen = origen.to_crs(
        destino.crs
    )

log("Geruzak behar bezala kargatu dira")

# --------------------------------------------------
# EREMUAK
# --------------------------------------------------

for campo in ["ROTULAR_C", "ROTULAR_E", "IDUT"]:

    if campo not in destino.columns:

        raise Exception(
            "{} eremua ez da existitzen".format(
                campo
            )
        )

# --------------------------------------------------
# IDUT -> HELBURUKO ERREGISTROA
# --------------------------------------------------

destino_por_idut = {}

for idx, row in destino.iterrows():

    destino_por_idut[
        row["IDUT"]
    ] = idx

# --------------------------------------------------
# LEPOAK ETA GAILURRAK BANATU
# --------------------------------------------------

collados = origen[
    origen["TIPO_E"] == "lepoa"
].copy()

cimas = origen[
    origen["TIPO_E"] == "gailurra"
].copy()

log(
    "Gailurrak: {}".format(
        len(cimas)
    )
)

log(
    "Lepoak: {}".format(
        len(collados)
    )
)

# --------------------------------------------------
# INDIZE ESPAZIALA + ALTUERAK
# --------------------------------------------------

indice = index.Index()

cimas_alt = {}

for idx, row in cimas.iterrows():

    geom = row.geometry

    indice.insert(
        idx,
        geom.bounds
    )

    try:

        z = next(
            mdt.sample(
                [(geom.x, geom.y)]
            )
        )[0]

        cimas_alt[idx] = (
            geom,
            float(z)
        )

    except Exception:
        pass

log(
    "Altitude baliodun gailurrak: {}".format(
        len(cimas_alt)
    )
)

# --------------------------------------------------
# PROMINENTZIAK KALKULATU
# --------------------------------------------------

radio = 1000

result = []

procesados = 0

for _, row in collados.iterrows():

    pt = row.geometry

    try:

        z0 = next(
            mdt.sample(
                [(pt.x, pt.y)]
            )
        )[0]

    except Exception:
        continue

    bbox = (
        pt.x - radio,
        pt.y - radio,
        pt.x + radio,
        pt.y + radio
    )

    candidatos = indice.intersection(
        bbox
    )

    max_z = None

    for fid in candidatos:

        if fid not in cimas_alt:
            continue

        pt_cima, z_cima = cimas_alt[fid]

        if pt.distance(pt_cima) <= radio:

            if (
                max_z is None or
                z_cima > max_z
            ):
                max_z = z_cima

    if max_z is None:
        continue

    prom = max_z - z0

    result.append(
        (
            row["IDUT"],
            prom
        )
    )

    procesados += 1

log(
    "Kalkulatutako prominentziak: {}".format(
        procesados
    )
)

# --------------------------------------------------
# PROMINENTZIAREN ARABERA ORDENATU
# --------------------------------------------------

result_sorted = sorted(
    result,
    key=lambda x: x[1],
    reverse=True
)

log(
    "Sailkatutako lepoak: {}".format(
        len(result_sorted)
    )
)

# --------------------------------------------------
# MAILAK ESLEITU
# --------------------------------------------------

contador_6 = 0
contador_5 = 0
contador_4 = 0
contador_3 = 0

for i, (idut, prom) in enumerate(result_sorted):

    if i < 10:

        peso = 6
        contador_6 += 1

    elif i < 30:

        peso = 5
        contador_5 += 1

    elif i < 130:

        peso = 4
        contador_4 += 1

    else:

        peso = 3
        contador_3 += 1

    idx_destino = destino_por_idut.get(
        idut
    )

    if idx_destino is not None:

        destino.at[
            idx_destino,
            "ROTULAR_C"
        ] = peso

        destino.at[
            idx_destino,
            "ROTULAR_E"
        ] = peso

# --------------------------------------------------
# GORDE
# --------------------------------------------------

destino.to_file(
    RUTA_DESTINO,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# --------------------------------------------------
# LABURPENA
# --------------------------------------------------

log("================================")

log(
    "6. maila: {}".format(
        contador_6
    )
)

log(
    "5. maila: {}".format(
        contador_5
    )
)

log(
    "4. maila: {}".format(
        contador_4
    )
)

log(
    "3. maila: {}".format(
        contador_3
    )
)

log("Mailak behar bezala esleitu dira")

log("Prozesua amaitu da")
