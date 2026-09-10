#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime


# =====================================================
# BIDEAK
# =====================================================

RUTA_ORIGEN = "/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles/r_oronimia_p.shp"
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

def borrar_shapefile(shp):
    extensiones = [
        ".shp",
        ".shx",
        ".dbf",
        ".prj",
        ".cpg",
        ".qix"
    ]

    base = os.path.splitext(shp)[0]

    for ext in extensiones:
        fichero = base + ext

        if os.path.exists(fichero):
            os.remove(fichero)
# =====================================================
# IRTEERAKO GERUZA SORTU
# =====================================================

if os.path.exists(RUTA_SALIDA):
    log("Borratzen")
    borrar_shapefile(RUTA_SALIDA)


copiar_shapefile(RUTA_ORIGEN, RUTA_SALIDA)

log("Irteerako geruza sortu da")
