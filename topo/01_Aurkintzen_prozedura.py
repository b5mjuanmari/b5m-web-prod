#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys

import geopandas as gpd
import pandas as pd
from rtree import index
from datetime import datetime

# =====================================================
# KONFIGURAZIOA
# =====================================================

DISTANCIAS = [1000, 800, 600, 400, 200, 0]

PORCENTAJES = {
    6: 0.01,
    5: 0.03,
    4: 0.12,
    3: 0.24
}

# =====================================================
# BIDEAK
# =====================================================

#RUTA_ORIGEN = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"
RUTA_BARRIOS = "/home5/SHP/Tiles/r_barrios_p.shp"
RUTA_ORONIMIA = "/home5/SHP/Tiles/r_oronimia.shp"

RUTA_SALIDA = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# FUNTZIOAK
# =====================================================

def copiar_shapefile(origen_shp, destino_shp):

    extensiones = [
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
        ".cpg",
        ".qix"
    ]

    base_origen = os.path.splitext(origen_shp)[0]
    base_destino = os.path.splitext(destino_shp)[0]

    for ext in extensiones:

        fichero_origen = base_origen + ext
        fichero_destino = base_destino + ext

        if os.path.exists(fichero_origen):
            shutil.copy2(
                fichero_origen,
                fichero_destino
            )

log(sys.argv[0])
log("Prozesuaren hasiera")

# =====================================================
# IRTEERAKO GERUZA SORTU
# =====================================================

#if not os.path.exists(RUTA_SALIDA):
#
#    copiar_shapefile(
#        RUTA_ORIGEN,
#        RUTA_SALIDA
#    )

#    log("Irteerako geruza sortu da")

# =====================================================
# DATUAK KARGATU
# =====================================================

topo = gpd.read_file(RUTA_SALIDA)
barrios = gpd.read_file(RUTA_BARRIOS)
oronimia = gpd.read_file(RUTA_ORONIMIA)

log("Geruzak behar bezala kargatu dira")

# =====================================================
# IRAGAZKIA
# =====================================================

topo_mask = topo["TIPO_E"] == "parajea, lekua"

# =====================================================
# AUZOEN INDIZE ESPAZIALA
# =====================================================

idx_barrios = index.Index()

barrios_dict = {}

for idx, row in barrios.iterrows():

    geom = row.geometry

    idx_barrios.insert(
        idx,
        geom.bounds
    )

    barrios_dict[idx] = geom

# =====================================================
# AZALERAK IDUT BAKOITZEKO
# =====================================================

sup_dict = {}

for _, row in oronimia.iterrows():

    idut = row["IDUT"]

    if pd.isna(idut):
        continue

    area = row.geometry.area

    sup_dict[idut] = (
        sup_dict.get(idut, 0.0)
        + area
    )

log(
    "Kargatutako IDUT kopurua: {}".format(
        len(sup_dict)
    )
)

# =====================================================
# ROTULAR_C EREMUA
# =====================================================

if "ROTULAR_C" not in topo.columns:

    topo["ROTULAR_C"] = None

topo.loc[topo_mask, "ROTULAR_C"] = None

# =====================================================
# 1. URRATSA
# 2. MAILA: 250 m-TAN AUZO BAT BAINO GEHIAGO
# =====================================================

candidatos = []

peso2 = 0

for idx_topo, row in topo[topo_mask].iterrows():

    geom = row.geometry

    vecinos = 0

    minx, miny, maxx, maxy = geom.buffer(250).bounds

    posibles = idx_barrios.intersection(
        (minx, miny, maxx, maxy)
    )

    for barrio_id in posibles:

        barrio_geom = barrios_dict[barrio_id]

        if geom.distance(barrio_geom) <= 250:

            vecinos += 1

            if vecinos > 1:
                break

    if vecinos > 1:

        topo.at[idx_topo, "ROTULAR_C"] = 2

        peso2 += 1

    else:

        candidatos.append({

            "idx": idx_topo,

            "geom": geom,

            "sup": sup_dict.get(
                row["IDUT"],
                0
            )
        })

log("2. mailako elementuak: {}".format(peso2))

# =====================================================
# AZALERAREN ARABERA ORDENATU
# =====================================================

candidatos.sort(
    key=lambda x: x["sup"],
    reverse=True
)

n = len(candidatos)

log(
    "Hautagai kopurua: {}".format(n)
)

objetivos = {}

for peso, pct in PORCENTAJES.items():

    objetivos[peso] = round(n * pct)

    log(
        "{}. mailarako helburua: {} elementu".format(
            peso,
            objetivos[peso]
        )
    )

# =====================================================
# HAUTAKETA ESPAZIATUA
# =====================================================

asignados = set()

for peso in [6, 5, 4, 3]:

    objetivo = objetivos[peso]

    seleccionados = []

    for distancia_min in DISTANCIAS:

        if len(seleccionados) >= objetivo:
            break

        for elem in candidatos:

            if elem["idx"] in asignados:
                continue

            valido = True

            for sel in seleccionados:

                if (
                    elem["geom"].distance(
                        sel["geom"]
                    )
                    < distancia_min
                ):

                    valido = False
                    break

            if not valido:
                continue

            topo.at[
                elem["idx"],
                "ROTULAR_C"
            ] = peso

            seleccionados.append(elem)

            asignados.add(
                elem["idx"]
            )

            if len(seleccionados) >= objetivo:
                break

    log(
        "{}. mailan esleituta: {}".format(
            peso,
            len(seleccionados)
        )
    )

# =====================================================
# GAINERAKOAK -> 2. MAILA
# =====================================================

mask_resto = (
    topo_mask &
    topo["ROTULAR_C"].isna()
)

peso2_final = mask_resto.sum()

topo.loc[
    mask_resto,
    "ROTULAR_C"
] = 2

log(
    "Azken 2. mailako elementuak: {}".format(
        peso2_final
    )
)

# =====================================================
# GORDE
# =====================================================

topo.to_file(
    RUTA_SALIDA,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# LABURPENA
# =====================================================

conteo = (
    topo.loc[topo_mask]
    .groupby("ROTULAR_C")
    .size()
)

print("\n===== LABURPENA =====")

for peso, cantidad in conteo.items():

    log(
        "{}. maila: {}".format(
            peso,
            cantidad
        )
    )

print("===== ********* =====\n")
log("Prozesua amaitu da")
