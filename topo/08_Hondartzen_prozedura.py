#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import geopandas as gpd

# =====================================================
# GERUZAK
# =====================================================

RUTA_PUNTOS_ORIGEN = "/home5/SHP/Tiles/r_oronimia_p.shp"

RUTA_PUNTOS_DESTINO = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

RUTA_POLIGONOS = "/home5/SHP/Tiles/r_oronimia.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# HASIERA
# =====================================================

log(sys.argv[0])
log("Prozesuaren hasiera")

# =====================================================
# GERUZAK KARGATU
# =====================================================

puntos_origen = gpd.read_file(
    RUTA_PUNTOS_ORIGEN
)

puntos_destino = gpd.read_file(
    RUTA_PUNTOS_DESTINO
)

poligonos = gpd.read_file(
    RUTA_POLIGONOS
)

# CRS bateratu

if poligonos.crs != puntos_destino.crs:

    poligonos = poligonos.to_crs(
        puntos_destino.crs
    )

if puntos_origen.crs != puntos_destino.crs:

    puntos_origen = puntos_origen.to_crs(
        puntos_destino.crs
    )

log("Geruzak behar bezala kargatu dira")

# =====================================================
# KONFIGURAZIOA
# =====================================================

SUPERFICIE_1HA = 10000.0

# =====================================================
# IDUT -> AZALERA
# =====================================================

superficies = {}

contador_poligonos = 0

for _, feat in poligonos.iterrows():

    if feat["TIPO_E"] != "hondartza_orogra":
        continue

    contador_poligonos += 1

    superficies[
        feat["IDUT"]
    ] = feat.geometry.area

log(
    "Aztertutako hondartza-poligonoak: {}".format(
        contador_poligonos
    )
)

# =====================================================
# ROTULAR_C EREMUA
# =====================================================

if "ROTULAR_C" not in puntos_destino.columns:

    raise Exception(
        "ROTULAR_C eremua ez da aurkitu"
    )

# =====================================================
# IDUT -> HELBURUKO ERREGISTROA
# =====================================================

destino_por_idut = {}

for idx, feat in puntos_destino.iterrows():

    destino_por_idut[
        feat["IDUT"]
    ] = idx

# =====================================================
# BALIOAK ESLEITU
# =====================================================

contador_1 = 0
contador_7 = 0
contador_5 = 0

for _, feat in puntos_origen.iterrows():

    if feat["TIPO_E"] != "hondartza_orogra":
        continue

    idx_destino = destino_por_idut.get(
        feat["IDUT"]
    )

    if idx_destino is None:
        continue

    # Marea arteko hondartza

    if feat["TIPO_UT"] == "playa intermareal":

        puntos_destino.at[
            idx_destino,
            "ROTULAR_C"
        ] = 1

        contador_1 += 1

        continue

    superficie = superficies.get(
        feat["IDUT"],
        0
    )

    if superficie > SUPERFICIE_1HA:

        valor = 7
        contador_7 += 1

    else:

        valor = 5
        contador_5 += 1

    puntos_destino.at[
        idx_destino,
        "ROTULAR_C"
    ] = valor

# =====================================================
# GORDE
# =====================================================

puntos_destino.to_file(
    RUTA_PUNTOS_DESTINO,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# LABURPENA
# =====================================================

log(
    "Marea arteko hondartzak -> 1. maila: {}".format(
        contador_1
    )
)

log(
    "1 hektareatik gorako hondartzak -> 7. maila: {}".format(
        contador_7
    )
)

log(
    "1 hektarea edo txikiagoko hondartzak -> 5. maila: {}".format(
        contador_5
    )
)

log("Prozesua amaitu da")
