#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import geopandas as gpd

# =====================================================
# BIDEAK
# =====================================================

ruta_destino = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

ruta_oronimia = "/home5/SHP/Tiles/r_oronimia.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# IDUT NORMALIZATU
# =====================================================

def normalizar_idut(valor):

    if valor is None:
        return None

    try:

        num = float(valor)

        if num.is_integer():

            return str(
                int(num)
            )

        return str(num)

    except Exception:

        return str(valor).strip()

# =====================================================
# HASIERA
# =====================================================

log(sys.argv[0])
log("Prozesuaren hasiera")

# =====================================================
# GERUZAK KARGATU
# =====================================================

capa_superficies = gpd.read_file(
    ruta_oronimia
)

capa_destino = gpd.read_file(
    ruta_destino
)

# CRS bateratu

if capa_superficies.crs != capa_destino.crs:

    capa_superficies = (
        capa_superficies.to_crs(
            capa_destino.crs
        )
    )

log("Geruzak behar bezala kargatu dira")

# =====================================================
# IDUT -> MAILA
# =====================================================

pesos = {}

for _, feat in capa_superficies.iterrows():

    if feat["TIPO_E"] != "urtegia":
        continue

    geom = feat.geometry

    if geom is None:
        continue

    if geom.is_empty:
        continue

    area = geom.area

    if area > 300000:

        peso = 6

    elif area >= 50000:

        peso = 5

    else:

        peso = 3

    idut = normalizar_idut(
        feat["IDUT"]
    )

    if idut:

        pesos[idut] = peso

log(
    "Aurkitutako urtegiak: {}".format(
        len(pesos)
    )
)

# =====================================================
# EREMUEN EGIAZTAPENA
# =====================================================

if "ROTULAR_C" not in capa_destino.columns:

    raise Exception(
        "ROTULAR_C eremua ez da aurkitu"
    )

# =====================================================
# ROTULAR_C EGUNERATU
# =====================================================

n_actualizados = 0

for idx, feat in capa_destino.iterrows():

    idut = normalizar_idut(
        feat["IDUT"]
    )

    if idut not in pesos:
        continue

    capa_destino.at[
        idx,
        "ROTULAR_C"
    ] = pesos[idut]

    n_actualizados += 1

# =====================================================
# GORDE
# =====================================================

capa_destino.to_file(
    ruta_destino,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# LABURPENA
# =====================================================

log(
    "Eguneratutako elementuak: {}".format(
        n_actualizados
    )
)

log("Prozesua amaitu da")
