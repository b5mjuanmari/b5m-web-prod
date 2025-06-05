#!/bin/bash

# Oracle Settings
TMP=/tmp; export TMP
TMPDIR=$TMP; export TMPDIR
ORACLE_HOME=/opt/oracle/instantclient; export ORACLE_HOME
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:$ORACLE_HOME:/opt/bin:/snap/bin"
export LANG=C
export NLS_LANG=SPANISH_SPAIN.WE8ISO8859P15
export NLS_NUMERIC_CHARACTERS=.,
export NLS_DATE_FORMAT=dd-mm-yyyy
LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib; export LD_LIBRARY_PATH
CLASSPATH=$ORACLE_HOME/JRE:$ORACLE_HOME/jlib:$ORACLE_HOME/rdbms/jlib; export CLASSPATH
export PATH=.:$PATH

export HOME="/home/lidar"

cd "${HOME}/SCRIPTS/WEB_PROD"

./genAero.sh
./genRotu.sh
python3 copy_tiles.py /home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles /home5/SHP

exit 0
