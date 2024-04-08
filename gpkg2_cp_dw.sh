#!/bin/bash
#
# ================================== #
#  +------------------------------+  #
#  | gpkg2_cp_dw.sh               |  #
#  | dw_ taulen kopia (deskargak) |  #
#  +------------------------------+  #
# ================================== #
#

# Inguruneko aldagaiak / Variables de entorno
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Tildeak eta eñeak / Tildes y eñes
export NLS_LANG=.AL32UTF8
set NLS_LANG=.UTF8
#export NLS_LANG=American_America.UTF8

# Aldagaiak / Variables
dir="${HOME}/SCRIPTS/GPKG"
sch="b5mweb_nombres"
con="${sch}/web+@//exploracle:1521/bdet"
bak="./bak"
logd="${dir}/log"
schu=`echo "$sch" | gawk '{ print toupper($0) }'`
crn=`echo "$0" | gawk 'BEGIN { FS = "/" }{ print NF }'`
scr=`echo "$0" | gawk 'BEGIN { FS = "/" }{ print $NF }'`
log=`echo "$0" | gawk -v logd="$logd" 'BEGIN{ FS="/" }{ split($NF, a, "."); print logd "/" a[1] ".log" }'`
if [ ! -d "$logd" ]
then
	mkdir "$logd" 2> /dev/null
fi
rm "$log" 2> /dev/null

# ========== #
#            #
# 1. Hasiera #
#            #
# ========== #

ini="Hasiera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$ini"

# Taulen zerrenda
a=`sqlplus -s "$con" <<-EOF
set serveroutput on
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0

select table_name
from user_tables
where lower(table_name) like 'dw_%';

exit;
EOF`

# Lan direktorioa
tdy=`date '+%Y%m%d'`
wrk="dw_tab_${tdy}"
if [ ! -d "$wrk" ]
then
	mkdir "$wrk"
fi

# Begizta nagusia
for b in $a
do
	echo "$b"

	# Datuak
	c="${wrk}/${b}.csv"
	rm "$c" 2> /dev/null
	sqlplus -s "$con" <<-EOF1 | gawk '
	{
		if (NR != 1)
			print $0
	}
	' > "$c"
	set serveroutput on
	set feedback off
	set linesize 32767
	set long 20000000
	set longchunksize 20000000
	set trim on
	set pages 0
	set tab on
	set spa 0
	set mark csv on

	select *
	from ${b};

	EOF1

	# DDL
	d="${wrk}/${b}.ddl"
	rm "$d" 2> /dev/null
	sqlplus -s "$con" <<-EOF1 | gawk '
	{
		print $0
	}
	' > "$d"
	set serveroutput on
	set feedback off
	set linesize 32767
	set long 20000000
	set longchunksize 20000000
	set trim on
	set pages 0
	set tab on
	set spa 0

	select dbms_metadata.get_ddl('TABLE', '${b}', '${schu}')
	from dual;

	EOF1
done

# Lan direktorioa konprimatu eta ezabatu
xz="${wrk}.tar.xz"
rm "$xz" 2> /dev/null
tar cJf "$xz" "$wrk"
rm -rf "$wrk"

# Kopia direktorioa
if [ ! -d "$bak" ]
then
	mkdir "$bak"
fi

# Mugitu
mv "$xz" "$bak"

# ========== #
#            #
# 9. Bukaera #
#            #
# ========== #

echo ""
fin="Bukaera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$fin"

exit 0
