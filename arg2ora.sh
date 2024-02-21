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
csv3="/tmp/arg3.csv"
csv4="/tmp/arg4.csv"
kon="b5mweb_25830/web+@//exploracle:1521/bdet"
tau="fotosaereas"
tau0="${tau}0"
tau1="${tau}1"
tau2="${tau}2"
taup="${tau}p"
gg="giputz"
d1="${HOME}/SCRIPTS/GPKG"
d2="/home8/fotos/fotosaereas"
f1="EXP"
f2=".tar.gz"
logd="${d1}/log"
scr="$(echo "$0" | gawk 'BEGIN{FS="/"}{print $NF}')"
log="$(echo "$0" | gawk -v logd="$logd" 'BEGIN{FS="/"}{split($NF,a,".");print logd"/"a[1]".log"}')"
rm "$log" 2> /dev/null
log="/dev/tty"

# ========== #
#            #
# 1. Hasiera #
#            #
# ========== #

ini="Hasiera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$ini" >> "$log"

# =========================== #
#                             #
# 2. Fitxategia deskonprimatu #
#                             #
# =========================== #

echo "Fitxategia deskonprimatu: $scr - `date '+%Y-%m-%d %H:%M:%S'`" >> "$log"
rm "/tmp/${f1}${f2}" 2> /dev/null
cp "${d2}/${f1}${f2}" "/tmp/${f1}${f2}"
rm -rf "/tmp/${f1}" 2> /dev/null
cd /tmp
tar zxf "${f1}${f2}"
cd "$d1"
rm "/tmp/${f1}${f2}" 2> /dev/null

# ============= #
#               #
# 3. CSVak egin #
#               #
# ============= #

echo "CSVak egin: $scr - `date '+%Y-%m-%d %H:%M:%S'`" >> "$log"
rm "$csv1" 2> /dev/null
rm "$csv2" 2> /dev/null
rm "$csv3" 2> /dev/null
echo "\"ID\",\"FLIGHT\",\"FRAME\",\"GEOM\"" > "$csv1"
cp "$csv1" "$csv2"
cp "$csv1" "$csv3"
i=1
j=1
for a in `ls "/tmp/${f1}"`
do
	IFS='_' read -a b <<< "$a"
	c=`echo "$a" | gawk 'BEGIN { FS = "_" }{ split($1, a, "fotos"); print a[2] }'`
	IFS='.' read -a d <<< "${b[1]}"
	if [ "$a" = "${b[0]}_pf${c}.EE" ]
	then
		# Puntuak
		gawk -v i=$i -v a="${b[0]}" '
		BEGIN {
			OFS = ","
		}
		{
			if ( substr($2, 1, 1) == "p" )
				b = substr($2, 2, length($2)-1)
			else
				b = $2
			getline
			print i, "\"" a "\"", "\"" b "\"", "\"POINT (" $1 " " $2 ")\""
			i++
		}
		' "/tmp/${f1}/${a}" >> "$csv1"
		i=`tail -1 "$csv1" | gawk 'BEGIN { FS = "," }{ print $1 + 1 }'`
	else
		# Puntuak
		gawk -v j=$j -v a="${b[0]}" -v b="${d[0]}" '
		BEGIN {
			OFS = ","
		}
		{
			if ($1 == "1POINT" || $1 == "2POINT" ) {
				getline
				print j, "\"" a "\"", "\"" b "\"", "\"POINT (" $1 " " $2 ")\""
				exit
			}
		}
		' "/tmp/${f1}/${a}" >> "$csv2"

		# Poligonoak
		gawk -v j=$j -v a="${b[0]}" -v b="${d[0]}" '
		BEGIN {
			OFS = ","
		}
		{
			if ($1 == "1EDGE" ) {
				if ($2 == 2) {
					getline
					x1 = $1
					y1 = $2
					getline
					getline
					getline
					x2 = $1
					y2 = $2
					getline
					getline
					getline
					x3 = $1
					y3 = $2
					getline
					getline
					getline
					x4 = $1
					y4 = $2
				} else {
					getline
					x1 = $1
					y1 = $2
					getline
					x2 = $1
					y2 = $2
					getline
					x3 = $1
					y3 = $2
					getline
					x4 = $1
					y4 = $2
				}
			}
			if ($1 == "1POINT" || $1 == "2POINT" ) {
					print j, "\"" a "\"", "\"" b "\"", "\"POLYGON ((" x1 " " y1 ", " x2 " " y2 ", " x3 " " y3 ", " x4 " " y4 ", " x1 " " y1 "))\""
					exit
				}
		}
		' "/tmp/${f1}/${a}" >> "$csv3"
		let j=$j+1
	fi
done
rm -rf "/tmp/${f1}" 2> /dev/null

# ================== #
#                    #
# 4. Oraclen kargatu #
#                    #
# ================== #

echo "Oraclen kargatu: $scr - `date '+%Y-%m-%d %H:%M:%S'`" >> "$log"

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

drop table ${tau};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau}';
drop table ${taup};
delete from user_sdo_geom_metadata
where lower(table_name)='${taup}';
drop table ${tau0};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau0}';
drop table ${tau1};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
drop table ${tau2};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau2}';
commit;

exit;
EOF

# tau0
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "+proj=utm +zone=30 +ellps=intl +nadgrids=sped2et.gsb +wktext" -t_srs "epsg:25830" -nln "$tau0" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv1"
rm "$csv4" 2> /dev/null
ogr2ogr -skipfailures -f CSV -lco GEOMETRY=AS_XY "$csv4" OCI:${kon}:${gg} -sql "select * from $tau0 order by id"
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
	print $4, "\"" $5 "\"", "\"" $6 "\"", "\"POINT(" a " " b ")\""
}
' "$csv4" > "$csv1"
rm "$csv4" 2> /dev/null

# tau1
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "+proj=utm +zone=30 +ellps=intl +nadgrids=sped2et.gsb +wktext" -t_srs "epsg:25830" -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv2"
rm "$csv4" 2> /dev/null
ogr2ogr -skipfailures -f CSV -lco GEOMETRY=AS_XY "$csv4" OCI:${kon}:${gg} -sql "select * from $tau1 order by id"
rm "$csv2" 2> /dev/null
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
	print $4, "\"" $5 "\"", "\"" $6 "\"", "\"POINT(" a " " b ")\""
}
' "$csv4" > "$csv2"
rm "$csv4" 2> /dev/null

# tau2
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -s_srs "+proj=utm +zone=30 +ellps=intl +nadgrids=sped2et.gsb +wktext" -t_srs "epsg:25830" -nln "$tau2" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv3"
ogr2ogr -skipfailures -f CSV -lco GEOMETRY=AS_WKT "$csv4" OCI:${kon}:${gg} -sql "select * from $tau2 order by id"
rm "$csv3" 2> /dev/null
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
	split($1, a, "\\(\\(")
	split(a[2], b, ",")
	split(b[1], c1, " ")
	split($2, c2, " ")
	split($3, c3, " ")
	split($4, c4, " ")
	x1 = sprintf("%.0f", c1[1])
	y1 = sprintf("%.0f", c1[2])
	x2 = sprintf("%.0f", c2[1])
	y2 = sprintf("%.0f", c2[2])
	x3 = sprintf("%.0f", c3[1])
	y3 = sprintf("%.0f", c3[2])
	x4 = sprintf("%.0f", c4[1])
	y4 = sprintf("%.0f", c4[2])
	print $7, "\"" $8 "\"", "\"" $9 "\"", "\"POLYGON ((" x1 " " y1 ", " x2 " " y2 ", " x3 " " y3 ", " x4 " " y4 ", " x1 " " y1 "))\""
}
' "$csv4" > "$csv3"
rm "$csv4" 2> /dev/null

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

drop table ${tau0};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau0}';
drop table ${tau1};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
drop table ${tau2};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau2}';
commit;

exit;
EOF

# tau0
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -nln "$tau0" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv1"
rm "$csv1" 2> /dev/null

# tau1
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -nln "$tau1" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv2"
rm "$csv2" 2> /dev/null

# tau2
ogr2ogr -skipfailures -f OCI OCI:${kon}:${gg} -nln "$tau2" -lco DIM=2 -lco SRID=25830 -lco GEOMETRY_NAME=GEOM -oo GEOM_POSSIBLE_NAMES="GEOM" -oo KEEP_GEOM_COLUMNS="NO" -oo AUTODETECT_TYPE="YES" "$csv3"
rm "$csv3" 2> /dev/null

# tau
tauu=`echo "$tau" | gawk '{ print toupper($0) }'`
taupu=`echo "$taup" | gawk '{ print toupper($0) }'`
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

drop table ${taup};
delete from user_sdo_geom_metadata
where lower(table_name)='${taup}';
drop table ${tau};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau}';

create table ${taup}(
id_framep number primary key,
flight varchar2(32),
frame varchar2(32),
point sdo_geometry
);

create table ${tau}(
id_frame number primary key,
flight varchar2(32),
frame varchar2(32),
point sdo_geometry,
polygon sdo_geometry
);

insert into user_sdo_geom_metadata
select '${taupu}','point',diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tau0}';
insert into user_sdo_geom_metadata
select '${tauu}','point',diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
insert into user_sdo_geom_metadata
select '${tauu}','polygon',diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tau1}';

insert into $taup
select id,flight,frame,geom
from $tau0
order by id;

insert into $tau
select a.id,a.flight,a.frame,a.geom,b.geom
from ${tau1} a,${tau2} b
where a.id=b.id
order by a.id;

drop table ${tau0};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau0}';
drop table ${tau1};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau1}';
drop table ${tau2};
delete from user_sdo_geom_metadata
where lower(table_name)='${tau2}';

create unique index ${taup}_idx
on ${taup}(flight,frame);
create index ${taup}_gidx
on ${taup}(point)
indextype is mdsys.spatial_index
parameters('layer_gtype=POINT');
create unique index ${tau}_idx
on ${tau}(flight,frame);
create index ${tau}1_gidx
on ${tau}(point)
indextype is mdsys.spatial_index
parameters('layer_gtype=POINT');
create index ${tau}2_gidx
on ${tau}(polygon)
indextype is mdsys.spatial_index
parameters('layer_gtype=POLYGON');
commit;

exit;
EOF

# ========== #
#            #
# 9. Bukaera #
#            #
# ========== #

echo "" >> "$log"
fin="Bukaera: $scr - `date '+%Y-%m-%d %H:%M:%S'`"
echo "$ini" >> "$log"
echo "$fin" >> "$log"

exit 0
