#!/bin/bash
#
# genAero.sh - Script para crear, a partir de restoind, un shapefile
# de tipo punto con la ubicación de los aerogeneradores, a partir de restoind
#

# Variables de Oracle
con="o_mw_25830/web+@//exploracle:1521/bdet"
tabres="restoind"
dir="/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles"

# Log
o="$(pwd)"
prc="$(echo "$0" | gawk 'BEGIN{FS="/"}{split($NF,a,".");print a[1]}')"
gaur="$(date +'%Y%m%d')"
log="${o}/log/${prc}_${gaur}.log"
rm "$log" 2> /dev/null

# Tabla y shapefile de aerogeneradores
tab="t_aerogen"

# Tag de los aerogeneradores en restoind
tag="AEROGENERADOR"

has="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Hasiera: $has" >> "$log"

# Extracción de los puntos de ubicación de los aerogeneradores a partir
# de los círculos con tag AEROGENERADOR de restoind
tabu="$(echo "$tab" | gawk '{print toupper($0)}')"
sqlplus -s "$con" <<-EOF > /dev/null 2> /dev/null

-- Creación tabla provisional aerogeneradores
drop table ${tab};

delete from user_sdo_geom_metadata
where lower(table_name)='${tab}';

create table ${tab}
as select *
from ${tabres}
where etiqueta='${tag}';

insert into user_sdo_geom_metadata
select '${tabu}',column_name,diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tabres}'
and lower(column_name)='polyline';

-- Los aerogeneradores son círculos cuyos diámetros expresan el alcance de las aspas
-- Esos círculos son polilíneas. Se pasan a polygono y se calcula su centro
alter table $tab
add polygon sdo_geometry;

update $tab
set polygon=polyline;

update $tab a
set
a.polygon.sdo_gtype=2003,
a.polygon.sdo_elem_info=sdo_elem_info_array(1,1003,1);

insert into user_sdo_geom_metadata
select '${tabu}','POLYGON',diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tabres}'
and lower(column_name)='polyline';

alter table $tab
add point sdo_geometry;

update $tab a
set point=(
select sdo_geom.sdo_centroid(b.polygon,m.diminfo)
from $tab b,user_sdo_geom_metadata m
where a.idutagr=b.idutagr
and m.table_name='${tabu}'
and m.column_name='POLYGON'
);

insert into user_sdo_geom_metadata
select '${tabu}','POINT',diminfo,srid
from user_sdo_geom_metadata
where lower(table_name)='${tabres}}'
and lower(column_name)='polyline';

commit;

exit;

EOF

# Exportación a shapefile de la tabla provisional de aerogeneradores
rm ${dir}/${tab}.* 2> /dev/null
ogr2ogr -f "ESRI Shapefile" -s_srs "EPSG:25830" -t_srs "EPSG:25830" ${dir}/${tab}.shp OCI:${con}:${tab} -sql "select \
idutagr,etiqueta,point \
from o_mw_25830.${tab} \
where point is not null"

# Borrado de la tabla de aerogeneradores de Oracle
sqlplus -s "$con" <<-EOF > /dev/null 2> /dev/null
drop table ${tab};

delete from user_sdo_geom_metadata
where lower(table_name)='${tab}';

commit;

exit;

EOF

buk="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Bukaera: $buk" >> "$log"

exit 0
