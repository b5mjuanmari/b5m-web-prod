#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import geopandas as gpd
from rtree import index
from datetime import datetime

# -------------------------
# SHP bideak
# -------------------------

ruta_origen = "/home5/SHP/Tiles/r_oronimia_p.shp"

ruta_destino = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

ruta_carre = "/home5/SHP/Tiles/t_carre.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# -------------------------
# IDUT normalizatzeko funtzioa
# -------------------------

def normalizar_idut(valor):

    if valor is None:
        return None

    try:
        return str(int(round(float(valor))))

    except Exception:
        return str(valor).strip()

# =====================================================
# HASIERA
# =====================================================

log(sys.argv[0])
log("Prozesuaren hasiera")

# -------------------------
# Geruzak kargatu
# -------------------------

origen = gpd.read_file(ruta_origen)

destino = gpd.read_file(ruta_destino)

carreteras = gpd.read_file(ruta_carre)

# CRS bateratu

if carreteras.crs != destino.crs:

    carreteras = carreteras.to_crs(
        destino.crs
    )

if origen.crs != destino.crs:

    origen = origen.to_crs(
        destino.crs
    )

log("Geruzak behar bezala kargatu dira")

DIST_MAX = 300.0

prioridades = {
    "roja": 7,
    "naranja": 6,
    "verde": 5,
    "amarillo": 4,
    "gris principal": 4,
    "gris secundaria": 4
}

# =====================================================
# ERREPIDEEN INDIZE ESPAZIALA
# =====================================================

idx_carre = index.Index()

carreteras_dict = {}

for idx, row in carreteras.iterrows():

    idx_carre.insert(
        idx,
        row.geometry.bounds
    )

    carreteras_dict[idx] = row

log("Errepideen indize espaziala sortu da")

# =====================================================
# JATORRIKO MENDATEEN HIZTEGIA
# =====================================================

origen_idut = {}

for _, feat in origen.iterrows():

    if feat["TIPO_E"] == "mendatea":

        idut = normalizar_idut(
            feat["IDUT"]
        )

        origen_idut[idut] = feat

log(
    "Jatorriko mendateak kargatu dira: {}".format(
        len(origen_idut)
    )
)

# =====================================================
# ROTULAR EREMUEN EGIAZTAGIRIA
# =====================================================

for campo in ["ROTULAR_C", "ROTULAR_E"]:

    if campo not in destino.columns:

        raise Exception(
            "{} eremua ez da existitzen".format(
                campo
            )
        )

# =====================================================
# MENDATEAK PROZESATU
# =====================================================

aldatutakoak = 0

for idx_dest, puerto_dest in destino.iterrows():

    if puerto_dest["TIPO_E"] != "mendatea":
        continue

    idut = normalizar_idut(
        puerto_dest["IDUT"]
    )

    if idut not in origen_idut:

        log(
            "IDUT ez da aurkitu: {}".format(
                idut
            )
        )

        continue

    puerto_ori = origen_idut[idut]

    geom = puerto_ori.geometry

    x = geom.x
    y = geom.y

    nearest = list(
        idx_carre.nearest(
            (x, y, x, y),
            1
        )
    )

    if not nearest:

        log(
            "Ez dago hurbileko errepiderik: {}".format(
                puerto_ori["NOMBRE"]
            )
        )

        continue

    carretera = carreteras_dict[
        nearest[0]
    ]

    distancia = geom.distance(
        carretera.geometry
    )

    if distancia > DIST_MAX:

        log(
            "Barrutitik kanpo: {}".format(
                puerto_ori["NOMBRE"]
            )
        )

        continue

    tipo = str(
        carretera["TIPO"]
    ).strip()

    if tipo not in prioridades:

        log(
            "{} | ERREPIDE MOTA EZ EZAGUNA -> '{}'".format(
                puerto_ori["NOMBRE"],
                tipo
            )
        )

        continue

    valor = prioridades[tipo]

    destino.at[
        idx_dest,
        "ROTULAR_C"
    ] = valor

    destino.at[
        idx_dest,
        "ROTULAR_E"
    ] = valor

    aldatutakoak += 1

    log(
        "{} | MOTA={} | dist={} m | ROTULAR={}".format(
            puerto_ori["NOMBRE"],
            tipo,
            round(distancia, 1),
            valor
        )
    )

# =====================================================
# GORDE
# =====================================================

destino.to_file(
    ruta_destino,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log(
    "Eguneratutako elementuak: {}".format(
        aldatutakoak
    )
)

log("Aldaketak gorde dira")

# =====================================================
# AMAIERA
# =====================================================

log("Prozesua amaitu da")
