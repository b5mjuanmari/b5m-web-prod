#!/bin/bash
#
# solr_poi.sh
#
# Hacer la tabla solr_poi_2d
#

# Variables de entorno
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Tildes y eines
export NLS_LANG=.AL32UTF8
set NLS_LANG=.UTF8

# Variables
dir="${HOME}/SCRIPTS/GPKG"
usu="b5mweb_nombres"
pas="web+"
bd="bdet"
tab="solr_poi_2d"
tabu="$(echo "$tab" | gawk '{print toupper($0)}')"

ini="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Inicio: $ini"

sqlplus -s ${usu}/${pas}@${bd} <<-EOF
drop table ${tab};

delete from user_sdo_geom_metadata
where lower(table_name)='${tab}'
and lower(column_name)='geom_cen';

create table $tab as
select
a.id_actividad id_poi,
'POI_' || a.id_actividad b5mcode,
a.cla_santi id_type_poi,
decode(a.nombre_comercial_e, null, a.nombre_comercial_c, a.nombre_comercial_e) name_eu,
a.nombre_comercial_c name_es,
e.title_eu class_eu,
e.title_es class_es,
e.title_en class_en,
e.description_eu class_description_eu,
e.description_es class_description_es,
e.description_en class_description_en,
i.url||'/'||g.icon class_icon,
d.title_eu category_eu,
d.title_es category_es,
d.title_en category_en,
d.description_eu category_description_eu,
d.description_es category_description_es,
d.description_en category_description_en,
i.url||'/'||h.icon category_icon,
'D_A'||a.id_postal b5mcode_d,
b.codmuni codmuni,
b.muni_e muni_eu,
b.muni_c muni_es,
b.codcalle codstreet,
b.calle_e street_eu,
b.calle_c street_es,
decode(substr(b.noportal,1,2),'00',substr(b.noportal,3,3),decode(substr(b.noportal,1,1),'0',substr(b.noportal,2,3),b.noportal)) door_number,
b.bis bis,
b.accesorio accessory,
b.codpostal postal_code,
'1' official,
sdo_geom.sdo_centroid(c.polygon,m.diminfo) geom_cen
from b5mweb_nombres.n_actipuerta a,b5mweb_nombres.n_edifdirpos b,b5mweb_25830.a_edifind c,b5mweb_nombres.poi_categories d,b5mweb_nombres.poi_classes e,b5mweb_nombres.poi_cat_class f,b5mweb_nombres.poi_icons g,b5mweb_nombres.poi_icons h,b5mweb_nombres.poi_icons_url i,all_sdo_geom_metadata m
where a.id_postal=b.idnombre
and a.idut=c.idut
and m.owner='B5MWEB_25830'
and m.table_name='A_EDIFIND'
and m.column_name='POLYGON'
and a.id_postal<>0
and d.id=f.poi_category_id
and e.id=f.poi_class_id
and a.cla_santi=e.code
and e.icon_id=g.id
and d.icon_id=h.id
and i.id=1
and d.enabled=1
order by a.id_actividad;

insert into user_sdo_geom_metadata
select '${tabu}','geom_cen',diminfo,srid
from all_sdo_geom_metadata
where lower(owner)='b5mweb_25830'
and lower(table_name)='a_edifind'
and lower(column_name)='polygon';

create index ${tab}1_idx on ${tab}(id_poi);
create index ${tab}2_idx on ${tab}(b5mcode);
create index ${tab}_gdx
on ${tab}(geom_cen)
indextype is mdsys.spatial_index
parameters('layer_gtype=MULTIPOINT');

exit;

EOF

fin="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Final:  $fin"

exit 0
