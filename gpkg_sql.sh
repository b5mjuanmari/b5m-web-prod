#!/bin/bash
#
# gpkg_sql.sh
#
# Sentencias SQL para la generación de geopakages
#

declare -A sql_a

sql_a["m_municipalities"]="select \
b.idut idut, \
a.url_2d b5mcode, \
a.nombre_e name_eu, \
a.nombre_c name_es, \
b.codmuni codmuni, \
c.comarca region, \
a.tipo_e type_eu, \
a.tipo_c type_es, \
a.tipo_i type_en, \
b.polygon geom \
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b,b5mweb_nombres.n_municipios c
where a.url_2d='M_'||b.codmuni \
and b.codmuni=c.codmuni \
and a.id_nombre1<>'996'"
