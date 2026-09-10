#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import geopandas as gpd

# ------------------------------------------------------------
# GERUZAK
# ------------------------------------------------------------

ruta_origen = "/home5/SHP/Tiles/r_oronimia_p.shp"

ruta_destino = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# ------------------------------------------------------------
# HASIERA
# ------------------------------------------------------------

log(sys.argv[0])
log("Prozesuaren hasiera")

origen = gpd.read_file(
    ruta_origen
)

destino = gpd.read_file(
    ruta_destino
)

# CRS bateratu

if origen.crs != destino.crs:

    origen = origen.to_crs(
        destino.crs
    )

log("Geruzak behar bezala kargatu dira")

# ------------------------------------------------------------
# HELBURUKO EREMUA
# ------------------------------------------------------------

if "ROTULAR_C" not in destino.columns:

    raise Exception(
        "ROTULAR_C eremua ez da existitzen"
    )

# ------------------------------------------------------------
# HELBURUKO ELEMENTUEN HIZTEGIA IDUT BIDEZ
# ------------------------------------------------------------

destino_idut = {}

for idx, feat in destino.iterrows():

    try:

        idut = int(
            round(
                float(feat["IDUT"])
            )
        )

        destino_idut[idut] = idx

    except Exception:
        pass

log(
    "Helburuko IDUT kopurua: {}".format(
        len(destino_idut)
    )
)

# ------------------------------------------------------------
# TIPO_E ARABERAKO MAILAK
# ------------------------------------------------------------

pisuak_tipo = {
    "espazio naturala": 9,
    "mendigunea": 8,
    "mendilerroa": 8,
    "gune singularra": 4,
    "muinoa": 3,
    "iturria": 3,
    "sarbegia": 3,
    "ur jauzia": 3,
    "baltsa": 2
}

# ------------------------------------------------------------
# UHARTEEN MAILA BEREZIAK
# ------------------------------------------------------------

uharte_pisuak = {
    417489: 3,
    418037: 6,
    418985: 3,
    418024: 7,
    417487: 3,
    417488: 3,
    417651: 4,
    418192: 4,
    418822: 8,
    417553: 3,
    718091: 6,
    718115: 3,
    718114: 3,
    718113: 5,
    731817: 3,
    719608: 5
}

# ------------------------------------------------------------
# EGUNERAKETA
# ------------------------------------------------------------

actualizados_tipo = 0
actualizados_uharte = 0

for _, feat in origen.iterrows():

    try:

        idut = int(
            round(
                float(feat["IDUT"])
            )
        )

    except Exception:
        continue

    if idut not in destino_idut:
        continue

    idx_destino = destino_idut[idut]

    tipo = feat["TIPO_E"]

    if tipo is not None:

        tipo_norm = str(tipo).strip().lower()

        if tipo_norm in pisuak_tipo:

            destino.at[
                idx_destino,
                "ROTULAR_C"
            ] = pisuak_tipo[tipo_norm]

            actualizados_tipo += 1

    if idut in uharte_pisuak:

        destino.at[
            idx_destino,
            "ROTULAR_C"
        ] = uharte_pisuak[idut]

        actualizados_uharte += 1

# ------------------------------------------------------------
# GORDE
# ------------------------------------------------------------

destino.to_file(
    ruta_destino,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# ------------------------------------------------------------
# LABURPENA
# ------------------------------------------------------------

log(
    "TIPO_E bidez eguneratutako elementuak: {}".format(
        actualizados_tipo
    )
)

log(
    "IDUT bidez eguneratutako uharteak: {}".format(
        actualizados_uharte
    )
)

log("Prozesua behar bezala amaitu da")
