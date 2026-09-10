#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from math import radians, cos, sin, sqrt
from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union

# ------------------------------------------------------------
# BIDEAK
# ------------------------------------------------------------

RUTA_TOPONIMIA = "/home5/SHP/Tiles/r_oronimia_p.shp"

RUTA_MAR = "/home5/SHP/Tiles/t_ITSASOind.shp"

RUTA_DESTINO = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

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

# ------------------------------------------------------------
# GERUZAK KARGATU
# ------------------------------------------------------------

toponimia = gpd.read_file(
    RUTA_TOPONIMIA
)

mar = gpd.read_file(
    RUTA_MAR
)

destino = gpd.read_file(
    RUTA_DESTINO
)

# CRS bateratu

if mar.crs != destino.crs:

    mar = mar.to_crs(
        destino.crs
    )

if toponimia.crs != destino.crs:

    toponimia = toponimia.to_crs(
        destino.crs
    )

log("Geruzak behar bezala kargatu dira")

# ------------------------------------------------------------
# IDUT NORMALIZAZIOA
# ------------------------------------------------------------

def normalizar_idut(valor):

    if valor is None:
        return None

    try:
        return int(
            round(
                float(valor)
            )
        )

    except Exception:
        return None

# ------------------------------------------------------------
# HELBURUKO EREMUAK
# ------------------------------------------------------------

for campo in ["ROTULAR_C", "ROTULAR_E"]:

    if campo not in destino.columns:

        raise Exception(
            "{} eremua ez da existitzen".format(
                campo
            )
        )

# ------------------------------------------------------------
# ITSASOAREN GEOMETRIA BATERATU
# ------------------------------------------------------------

mar_geom = unary_union(
    mar.geometry
)

log("Itsasoaren geometria bateratu da")

# ------------------------------------------------------------
# LURMUTURRAK HAUTATU
# ------------------------------------------------------------

cabos = []

for _, f in toponimia.iterrows():

    if f["TIPO_E"] == "lurmuturra":

        idut = normalizar_idut(
            f["IDUT"]
        )

        if idut is None:
            continue

        cabos.append(f)

log(
    "Aurkitutako lurmuturrak: {}".format(
        len(cabos)
    )
)

# ------------------------------------------------------------
# ITSASO ANGELU IREKIA
# ------------------------------------------------------------

def angulo_marino(
    pt,
    radio=500
):

    abiertas = 0

    for ang in range(0, 360, 6):

        x = (
            pt.x +
            radio * cos(
                radians(ang)
            )
        )

        y = (
            pt.y +
            radio * sin(
                radians(ang)
            )
        )

        p = Point(x, y)

        if mar_geom.contains(p):

            abiertas += 1

    return abiertas * 6

# ------------------------------------------------------------
# ANGELUTASUNA KALKULATU
# ------------------------------------------------------------

datos = []

for f in cabos:

    pt = f.geometry

    a500 = angulo_marino(
        pt,
        500
    )

    datos.append({
        "idut": normalizar_idut(
            f["IDUT"]
        ),
        "pt": pt,
        "angularidad": a500
    })

log("Angelutasuna kalkulatu da")

# ------------------------------------------------------------
# ISOLAMENDUA
# ------------------------------------------------------------

for d in datos:

    aislamiento = None

    for d2 in datos:

        if d["idut"] == d2["idut"]:
            continue

        if (
            d2["angularidad"]
            < d["angularidad"]
        ):
            continue

        dist = d["pt"].distance(
            d2["pt"]
        )

        if (
            aislamiento is None
            or
            dist < aislamiento
        ):
            aislamiento = dist

    if aislamiento is None:

        aislamiento = 50000

    d["aislamiento"] = aislamiento

    d["score"] = (
        d["angularidad"]
        *
        sqrt(aislamiento)
    )

log("Isolamendua kalkulatu da")

# ------------------------------------------------------------
# SAILKAPENA
# ------------------------------------------------------------

ranking = sorted(
    datos,
    key=lambda x: x["score"],
    reverse=True
)

log("Sailkapena sortu da")

# ------------------------------------------------------------
# MAILAK IDUT BAKOITZEKO
# ------------------------------------------------------------

pesos_por_idut = {}

for i, d in enumerate(ranking):

    if i < 10:

        peso = 7

    elif i < 20:

        peso = 6

    elif i < 40:

        peso = 5

    elif i < 60:

        peso = 4

    else:

        peso = 3

    pesos_por_idut[
        d["idut"]
    ] = peso

log(
    "Mailak kalkulatu dira {} entitaterentzat".format(
        len(pesos_por_idut)
    )
)

# ------------------------------------------------------------
# HELBURUKO GERUZA EGUNERATU
# ------------------------------------------------------------

actualizados = 0

for idx, feat in destino.iterrows():

    idut = normalizar_idut(
        feat["IDUT"]
    )

    if idut not in pesos_por_idut:
        continue

    peso = pesos_por_idut[idut]

    destino.at[
        idx,
        "ROTULAR_C"
    ] = peso

    destino.at[
        idx,
        "ROTULAR_E"
    ] = peso

    actualizados += 1

# ------------------------------------------------------------
# GORDE
# ------------------------------------------------------------

destino.to_file(
    RUTA_DESTINO,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# ------------------------------------------------------------
# AMAIERA
# ------------------------------------------------------------

log(
    "Prozesua amaitu da. "
    "Eguneratutako erregistroak: {}".format(
        actualizados
    )
)
