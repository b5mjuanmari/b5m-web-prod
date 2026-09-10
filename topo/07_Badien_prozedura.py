#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import geopandas as gpd

# =====================================================
# FITXATEGIAK
# =====================================================

input_path = "/home5/SHP/Tiles/r_oronimia.shp"

output_path = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# IDUT NORMALIZATZEKO FUNTZIOA
# =====================================================

def normalizatu_idut(value):

    if value is None:
        return None

    try:
        return str(
            int(
                float(value)
            )
        )

    except Exception:
        return str(value).strip()

# =====================================================
# HASIERA
# =====================================================

log(sys.argv[0])
log("Prozesuaren hasiera")

# =====================================================
# GERUZAK KARGATU
# =====================================================

capa_superficies = gpd.read_file(
    input_path
)

capa_out = gpd.read_file(
    output_path
)

# CRS bateratu

if capa_superficies.crs != capa_out.crs:

    capa_superficies = (
        capa_superficies.to_crs(
            capa_out.crs
        )
    )

log("Geruzak behar bezala kargatu dira")

# =====================================================
# IDUT -> MAILA HIZTEGIA
# =====================================================

pesos = {}

contador_badia = 0

for _, feat in capa_superficies.iterrows():

    if feat["TIPO_E"] != "badia":
        continue

    contador_badia += 1

    area = feat.geometry.area

    if area > 200000:

        peso = 7

    elif area >= 100000:

        peso = 6

    elif area >= 50000:

        peso = 5

    elif area >= 18000:

        peso = 4

    else:

        peso = 3

    idut = normalizatu_idut(
        feat["IDUT"]
    )

    pesos[idut] = peso

log(
    "Aztertutako badiak: {}".format(
        contador_badia
    )
)

# =====================================================
# EREMUEN EGIAZTAPENA
# =====================================================

if "ROTULAR_C" not in capa_out.columns:

    raise Exception(
        "ROTULAR_C eremua ez da aurkitu"
    )

# =====================================================
# ROTULAR_C EGUNERATU
# =====================================================

n_actualizados = 0

for idx, feat in capa_out.iterrows():

    idut = normalizatu_idut(
        feat["IDUT"]
    )

    if idut not in pesos:
        continue

    capa_out.at[
        idx,
        "ROTULAR_C"
    ] = pesos[idut]

    n_actualizados += 1

# =====================================================
# GORDE
# =====================================================

capa_out.to_file(
    output_path,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# AMAIERA
# =====================================================

log(
    "Eguneratutako elementuak: {}".format(
        n_actualizados
    )
)

log("Prozesua amaitu da")
