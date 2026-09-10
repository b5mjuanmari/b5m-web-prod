#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import geopandas as gpd
import pandas as pd
import rasterio

from rtree import index
from shapely.geometry import Point
from difflib import SequenceMatcher
from datetime import datetime
import unicodedata

# =====================================================
# BIDEAK
# =====================================================

ORONIMIA = "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp.shp"

MENDIKAT = "/home9/SHP/tiles_saiakera/KanpokoDatuak/mendikat.txt"

MENDIAK = "/home9/SHP/tiles_saiakera/KanpokoDatuak/mendiak.geojson"

MDT = "/home9/terrain/MDT2017_01_25830_COG.tif"

DISTANCIA = 500

UMBRAL_SIMILITUD = 0.5

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# FUNTZIOAK
# =====================================================

def normalize(txt):

    if txt is None:
        return ""

    txt = str(txt)

    txt = ''.join(
        c
        for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )

    txt = txt.lower()

    return txt.strip()

def similarity(a, b):

    a = normalize(a)

    if not a or not b:
        return 0

    parts = normalize(b).replace("/", " ").split()

    return max(
        (
            SequenceMatcher(
                None,
                a,
                p
            ).ratio()
            for p in parts
        ),
        default=0
    )

# =====================================================
# HASIERA
# =====================================================

log(sys.argv[0])
log("Prozesuaren hasiera")

# =====================================================
# GERUZAK KARGATU
# =====================================================

oronimia = gpd.read_file(ORONIMIA)

mendiak = gpd.read_file(MENDIAK)

mendikat = pd.read_csv(
    MENDIKAT,
    delimiter=","
)

mdt = rasterio.open(MDT)

# CRS bateratu

mendiak = mendiak.to_crs(
    oronimia.crs
)

# Mendikat GeoDataFrame

mendikat = gpd.GeoDataFrame(
    mendikat,
    geometry=gpd.points_from_xy(
        mendikat["x"],
        mendikat["y"]
    ),
    crs=oronimia.crs
)

log("Geruzak behar bezala kargatu dira")

# =====================================================
# MENDIKAT INDIZEA
# =====================================================

idx_mendikat = index.Index()

mendikat_dict = {}

for idx, row in mendikat.iterrows():

    geom = row.geometry

    idx_mendikat.insert(
        idx,
        geom.bounds
    )

    mendikat_dict[idx] = row

log("Mendikat indizea sortu da")

# =====================================================
# MENDIAK INDIZEA
# =====================================================

idx_mendiak = index.Index()

mendiak_dict = {}

for idx, row in mendiak.iterrows():

    geom = row.geometry

    idx_mendiak.insert(
        idx,
        geom.bounds
    )

    mendiak_dict[idx] = row

log("Mendiak indizea sortu da")

# =====================================================
# 1. URRATSA
# MENDIKAT -> 5
# =====================================================

contador_5 = 0

for idx, row in oronimia.iterrows():

    if str(row["TIPO_E"]).strip().lower() != "gailurra":
        continue

    rot = row["ROTULAR_C"]

    if rot == 7:
        continue

    nombre = row["NOMBRE_E"]

    if pd.isna(nombre):
        continue

    geom = row.geometry

    bbox = geom.buffer(
        DISTANCIA
    ).bounds

    candidatos = idx_mendikat.intersection(
        bbox
    )

    mejor = 0

    for cid in candidatos:

        m_row = mendikat_dict[cid]

        distancia = geom.distance(
            m_row.geometry
        )

        if distancia > DISTANCIA:
            continue

        score = similarity(
            nombre,
            m_row["name"]
        )

        mejor = max(
            mejor,
            score
        )

    if mejor > UMBRAL_SIMILITUD:

        oronimia.at[
            idx,
            "ROTULAR_C"
        ] = 5

        contador_5 += 1

log(
    "5. mailako elementuak: {}".format(
        contador_5
    )
)

# =====================================================
# 2. URRATSA
# MENDIAK -> 4
# =====================================================

contador_4 = 0

for idx, row in oronimia.iterrows():

    if str(row["TIPO_E"]).strip().lower() != "gailurra":
        continue

    rot = row["ROTULAR_C"]

    if rot in [7, 5]:
        continue

    nombre = row["NOMBRE_E"]

    if pd.isna(nombre):
        continue

    geom = row.geometry

    bbox = geom.buffer(
        DISTANCIA
    ).bounds

    candidatos = idx_mendiak.intersection(
        bbox
    )

    mejor = 0

    for cid in candidatos:

        m_row = mendiak_dict[cid]

        distancia = geom.distance(
            m_row.geometry
        )

        if distancia > DISTANCIA:
            continue

        score = similarity(
            nombre,
            m_row["name"]
        )

        mejor = max(
            mejor,
            score
        )

    if mejor > UMBRAL_SIMILITUD:

        oronimia.at[
            idx,
            "ROTULAR_C"
        ] = 4

        contador_4 += 1

log(
    "4. mailako elementuak: {}".format(
        contador_4
    )
)

# =====================================================
# 3. URRATSA
# MDT -> ALTUERAK
# =====================================================

alturas = {}

for idx, row in oronimia.iterrows():

    if str(row["TIPO_E"]).strip().lower() != "gailurra":
        continue

    rot = row["ROTULAR_C"]

    if rot in [7, 5, 4]:
        continue

    geom = row.geometry

    x = geom.x
    y = geom.y

    try:

        valor = next(
            mdt.sample(
                [(x, y)]
            )
        )[0]

        if valor is None:
            continue

        alturas[idx] = float(valor)

    except Exception:
        continue

log(
    "Kalkulatutako altuerak: {}".format(
        len(alturas)
    )
)

# =====================================================
# 4. URRATSA
# AZTERTU GABEKO GAILURREN INDIZEA
# =====================================================

idx_cimas = index.Index()

cimas = {}

for idx, row in oronimia.iterrows():

    if idx not in alturas:
        continue

    idx_cimas.insert(
        idx,
        row.geometry.bounds
    )

    cimas[idx] = row

log(
    "Aztertzeko gailurrak: {}".format(
        len(cimas)
    )
)

# =====================================================
# 5. URRATSA
# 3. MAILA / 2. MAILA
# =====================================================

contador_3 = 0
contador_2 = 0

for fid, feat in cimas.items():

    geom = feat.geometry

    mi_cota = alturas[fid]

    bbox = geom.buffer(
        DISTANCIA
    ).bounds

    candidatos = idx_cimas.intersection(
        bbox
    )

    maxima = True

    for cid in candidatos:

        if cid == fid:
            continue

        otro = cimas[cid]

        if (
            geom.distance(
                otro.geometry
            ) > DISTANCIA
        ):
            continue

        otra_cota = alturas[cid]

        if otra_cota > mi_cota:

            maxima = False
            break

    if maxima:

        oronimia.at[
            fid,
            "ROTULAR_C"
        ] = 3

        contador_3 += 1

    else:

        oronimia.at[
            fid,
            "ROTULAR_C"
        ] = 2

        contador_2 += 1

# =====================================================
# GORDE
# =====================================================

oronimia.to_file(
    ORONIMIA,
    driver="ESRI Shapefile",
    encoding="UTF-8"
)

log("Aldaketak gorde dira")

# =====================================================
# LABURPENA
# =====================================================

log("================================")
log("5. maila: {}".format(contador_5))
log("4. maila: {}".format(contador_4))
log("3. maila: {}".format(contador_3))
log("2. maila: {}".format(contador_2))
log("Prozesua amaitu da")
