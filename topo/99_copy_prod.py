#!/usr/bin/env python3

import shutil
from pathlib import Path

src_base = Path(
    "/home9/SHP/tiles_saiakera/r_oronimia_p-dev-tmp"
)

dst_base = Path(
    "/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles/r_oronimia_p"
)

# =====================================================
# KANPO FUNTZIOAK
# =====================================================

from logger_eu import sortu_logger
log = sortu_logger(__file__)

# =====================================================
# Prozesua
# =====================================================

try:
    # Helburuko shapefilearen osagai guztiak ezabatu
    for f in dst_base.parent.glob(dst_base.stem + ".*"):
        f.unlink()

    # Jatorrizko shapefilearen osagai guztiak kopiatu
    for f in src_base.parent.glob(src_base.stem + ".*"):
        dst_file = dst_base.parent / f.name.replace(
            src_base.stem,
            dst_base.stem,
            1
        )
        shutil.copy2(f, dst_file)
        log(f"Kopiatuta: {dst_file}")

    log("Shapefilea ondo kopiatu da.")

except Exception as e:
    log(f"Errorea: {e}")
    raise
