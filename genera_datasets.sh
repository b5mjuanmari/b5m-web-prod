#!/bin/bash

export HOME="/home/lidar"

cd "${HOME}/SCRIPTS/WEB_PROD"

python3 genera_datasets.py
python3 copy_local.py /home/data/datos_explotacion/CUR/datasets /home5

exit 0
