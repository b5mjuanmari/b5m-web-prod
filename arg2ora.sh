#!/bin/bash
#
# =============================================== #
#  +-------------------------------------------+  #
#  | arg2ora.sh                                |  #
#  | Airetiko argazkiak Oraclera               |  #
#  | Jatorria: Genamapeko ZF25 .EE fitxagegiak |  #
#  +-------------------------------------------+  #
# =============================================== #
#

# Inguruneko aldagaiak / Variables de entorno
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Aldagaiak / Variables
csv1="/tmp/arg1.csv"
csv2="/tmp/arg2.csv"
kon="b5mweb_25830/web+@//exploracle:1521/bdet"
tau="fotosaereas"
gg="giputz"
d1="${HOME}/SCRIPTS/GPKG"
d2="/home8/fotos/fotosaereas"
f1="EXP"
f2=".tar.gz"
logd="${dir}/log"
scr="$(echo "$0" | gawk 'BEGIN{FS="/"}{print $NF}')"
log="$(echo "$0" | gawk -v logd="$logd" 'BEGIN{FS="/"}{split($NF,a,".");print logd"/"a[1]".log"}')"

# ========== #
#            #
# 1. Hasiera #
#            #
# ========== #

ini="Hasiera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$ini"

# =========================== #
#                             #
# 2. Fitxategia deskonprimatu #
#                             #
# =========================== #

#echo "Fitxategia deskonprimatu: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
#rm "/tmp/${f1}${f2}" 2> /dev/null
#cp "${d2}/${f1}${f2}" "/tmp/${f1}${f2}"
#rm -rf "/tmp/${f1}" 2> /dev/null
#cd /tmp
#tar zxf "${f1}${f2}"
#cd "$d1"
#rm "/tmp/${f1}${f2}" 2> /dev/null

# ============= #
#               #
# 3. CSVak egin #
#               #
# ============= #

echo "CSVak egin: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
rm "$csv1" 2> /dev/null
echo "\"ID\",\"FLIGHT\",\"FRAME\",\"GEOM\"" > "$csv1"
i=1
for a in `ls "/tmp/${f1}"`
do
	IFS='_' read -a b <<< "$a"
	IFS='s_' read -a c <<< "$a"
	#echo "$a - ${b[0]} - ${c[1]}"
	#b=`echo "$a" | gawk 'BEGIN { FS = "_" }{ a = substr($2, 1, 2); print a }'`
	#if [ "$b" = "pf" ]
	if [ "$a" = "${b[0]}_pf${c[1]}.EE" ]
	then
		# Puntuak
		#echo "KK1: $a"
		gawk -v i=$i -v a="${b[0]}" '
		BEGIN {
			OFS = ","
		}
		{
			b=$2
			getline
			print i, "\"" a "\"", "\"" b "\"", "\"POINT (" $1 " " $2 ")\""
			i++
		}
		' "/tmp/${f1}/${a}" >> "$csv1"
	else
		d+=("$a")
	fi
done

# ================== #
#                    #
# 4. Oraclen kargatu #
#                    #
# ================== #

echo "Oraclen kargatu: $scr - `date '+%Y-%m-%d %H:%M:%S'`"

tau1="${tau}1"
sqlplus -s "$kon" <<-EOF > /dev/null
set serveroutput on
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0

drop table ${tau1};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
commit;

exit;
EOF
#ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "epsg:23030" -t_srs "epsg:25830" -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv"
#ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "+proj=utm +zone=30 +ellps=intl +nadgrids=sped2et.gsb +wktext" -t_srs "epsg:25830" -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv"
rm "$csv2" 2> /dev/null
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "+proj=utm +zone=30 +ellps=intl +nadgrids=sped2et.gsb +wktext" -t_srs "epsg:25830" -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv1"
ogr2ogr -skipfailures -f CSV -lco GEOMETRY=AS_XYZ "$csv2" OCI:${kon}:${gg} -sql "select * from $tau1 order by id"
rm "$csv1" 2> /dev/null
gawk '
BEGIN {
	FS = ","
	OFS = ","
	print "\"ID\"","\"FLIGHT\"","\"FRAME\"","\"GEOM\""
}
{
	if (NR == 1)
		getline
	gsub("\"", "")
	a = sprintf("%.0f", $1)
	b = sprintf("%.0f", $2)
	print $5, "\"" $6 "\"", "\"" $7 "\"", "\"POINT(" a " " b ")\""
}
' "$csv2" > "$csv1"
rm "$csv2" 2> /dev/null
sqlplus -s "$kon" <<-EOF > /dev/null
set serveroutput on
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0

drop table ${tau1};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
commit;

exit;
EOF
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv1"
rm "$csv1" 2> /dev/null

# ========== #
#            #
# 9. Bukaera #
#            #
# ========== #

#rm "$csv1" 2> /dev/null
#rm -rf "$f1" 2> /dev/null
echo ""
fin="Bukaera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$ini"
echo "$fin"

exit 0
