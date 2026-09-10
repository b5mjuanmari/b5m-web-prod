#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import geopandas as gpd
from rtree import index
from datetime import datetime

# =====================================================
# BIDEAK
# =====================================================

ruta_origen = "/home5/SHP/Tiles/r_oronimia_p.shp"

ruta_destino = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

ruta_oronimia = "/home5/SHP/Tiles/r_oronimia.shp"

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

origen = gpd.read_file(ruta_origen)

destino = gpd.read_file(ruta_destino)

oronimia = gpd.read_file(ruta_oronimia)

# CRS bateratu

if origen.crs != destino.crs:
    origen = origen.to_crs(destino.crs)

if oronimia.crs != destino.crs:
    oronimia = oronimia.to_crs(destino.crs)

log("Geruzak behar bezala kargatu dira")

# =====================================================
# KONFIGURAZIOA
# =====================================================

CAMPO_NOMBRE = "NOMBRE"

# =====================================================
# TESTUAK GARBITZEKO FUNTZIOA
# =====================================================

def limpiar(txt):

    if txt is None:
        return ""

    txt = str(txt).lower().strip()

    txt = re.sub(
        r"\bmendia\b",
        "",
        txt
    )

    txt = re.sub(
        r"\bmendi\b",
        "",
        txt
    )

    txt = " ".join(
        txt.split()
    )

    return txt

# =====================================================
# GAILURREN INDIZE ESPAZIALA
# =====================================================

cimas = {}

indice_cimas = index.Index()

for idx, f in origen.iterrows():

    if f["TIPO_E"] != "gailurra":
        continue

    cimas[idx] = f

    indice_cimas.insert(
        idx,
        f.geometry.bounds
    )

log(
    "Gailurren indize espaziala sortu da: {}".format(
        len(cimas)
    )
)

# =====================================================
# MENDIEN PISUA KALKULATU
# =====================================================

peso_monte = {}

contador_montes = 0

for _, monte in oronimia.iterrows():

    if monte["TIPO_E"] != "mendia":
        continue

    contador_montes += 1

    nombre_monte = limpiar(
        monte[CAMPO_NOMBRE]
    )

    if not nombre_monte:

        peso_monte[
            str(monte["IDUT"])
        ] = 4

        continue

    geom_monte = monte.geometry

    candidatos = list(
        indice_cimas.intersection(
            geom_monte.bounds
        )
    )

    encontrado = False

    for id_cima in candidatos:

        cima = cimas[id_cima]

        if not geom_monte.contains(
            cima.geometry
        ):
            continue

        nombre_cima = limpiar(
            cima[CAMPO_NOMBRE]
        )

        if nombre_monte in nombre_cima:

            encontrado = True
            break

    peso_monte[
        str(monte["IDUT"])
    ] = 3 if encontrado else 4

log(
    "Aztertutako mendiak: {}".format(
        contador_montes
    )
)

# =====================================================
# HELBURUKO GERUZA EGUNERATU
# =====================================================

actualizados_3 = 0
actualizados_4 = 0

for idx, f in destino.iterrows():

    idut = str(f["IDUT"])

    if idut not in peso_monte:
        continue

    peso = peso_monte[idut]

    destino.at[
        idx,
        "ROTULAR_C"
    ] = peso

    destino.at[
        idx,
        "ROTULAR_E"
    ] = peso

    if peso == 3:
        actualizados_3 += 1
    else:
        actualizados_4 += 1

# =====================================================
# GORDE
# =====================================================

destino.to_file(
    ruta_destino,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# LABURPENA
# =====================================================

log(
    "Barruan dagoen eta izena bat datorren gailurra duten mendiak -> 3. maila: {}".format(
        actualizados_3
    )
)

log(
    "Gainerako mendiak -> 4. maila: {}".format(
        actualizados_4
    )
)

log("Prozesua amaitu da")
