#!/bin/bash
#
# gpkg_sql.sh
#
# Sentencias SQL para la generación de geopakages
#

declare -A des_a
declare -A sql_a
declare -A idx_a

# 1. m_municipalities (municipios) (carga: 1')
des_a["m_municipalities"]="Udalerriak / Municipios / Municipalities"
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
idx_a["m_municipalities"]="b5mcode"

# 2. d_postaladdresses (direcciones postales) (carga: 4')
des_a["d_postaladdresses"]="Posta helbideak / Direcciones postales / Postal Addresses"
sql_a["d_postaladdresses"]="select \
b.idut idut, \
a.idnombre idname, \
'D_A'||idnombre b5mcode, \
a.codmuni codmuni, \
a.muni_e muni_eu, \
a.muni_c muni_es, \
a.codcalle codstreet, \
a.calle_e street_eu, \
a.calle_c street_es, \
a.noportal door_number, \
a.bis bis, \
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code, \
a.distrito coddistr, \
a.seccion codsec, \
a.nomedif_e name_eu, \
a.nomedif_c name_es, \
'ERAIKINA' type_eu, \
'EDIFICIO' type_es, \
'BUILDING' type_en, \
b.polygon geom \
from b5mweb_nombres.solr_edifdirpos a,b5mweb_25830.a_edifind b,b5mweb_nombres.n_rel_area_dirpos c \
where a.idnombre=c.idpostal \
and c.idut=b.idut \
order by a.idnombre"
idx_a["d_postaladdresses"]="b5mcode"

# 3. i_hydrography (hidrografía) (carga: 3')
des_a["i_hydrography"]="Hidrografia / Hidrografía / Hydrography"
sql_a["i_hydrography"]="select \
a.idut idut, \
a.idnombre idname, \
'I_A'||a.idnombre b5mcode, \
a.nom_e name_eu, \
a.nom_c name_es, \
a.idnomcuenca idbasinname, \
a.cuenca_e basinname_eu, \
a.cuenca_c basinname_es, \
b.oculto hidden, \
b.nivel \"LEVEL\", \
b.polyline geom \
from b5mweb_nombres.r_riotramo a,b5mweb_25830.ibai_plus b \
where a.idut=b.idut"
idx_a["i_hydrography"]="b5mcode"

# 4. sg_geodeticbenchmarks (señales geodésicas) (carga: 30")
sg_aju_eu="Doikuntza geodesikoa"
sg_sen_eu="Seinale geodesikoa"
sg_aju_es="Ajuste geodésico"
sg_sen_es="Señal geodésica"
sg_aju_en="Geodetic Adjustment"
sg_sen_en="Geodetic Benchmark"
sg_url="https://b5m.gipuzkoa.eus/geodesia/pdf"
des_a["sg_geodeticbenchmarks"]="Seinale geodesikoak / Señales geodésicas / Geodetic Benchmarks"
sql_a["sg_geodeticbenchmarks"]="select \
a.pgeod_id idgeodb, \
'SG_'||a.pgeod_id b5mcode, \
a.nombre display_name, \
decode(a.ajuste,1,'${sg_aju_eu}','${sg_sen_eu}') type_eu, \
decode(a.ajuste,1,'${sg_aju_es}','${sg_sen_es}') type_es, \
decode(a.ajuste,1,'${sg_aju_en}','${sg_sen_en}') type_en, \
a.codmuni codmuni, \
trim(regexp_substr(b.municipio,'[^/]+',1,1)) muni_eu, \
decode(trim(regexp_substr(b.municipio,'[^/]+',1,2)),null,b.municipio,trim(regexp_substr(b.municipio,'[^/]+',1,2))) muni_es, \
'${sg_url}/'||a.archivo link, \
a.file_type, \
a.size_kb, \
a.geom \
from o_mw_bta.puntogeodesicobta a,b5mweb_nombres.n_municipios b \
where a.codmuni=b.codmuni \
and a.visible_web=1 \
order by a.pgeod_id"
idx_a["sg_geodeticbenchmarks"]="b5mcode"

# 5. dm_distancemunicipalities (distancia entre municipios) (carga: 14h)
des_a["dm_distancemunicipalities"]="Udalerrien arteko distantzia / Distancia entre municipios / Distance Between Municipalities"
sql_a["dm_distancemunicipalities"]="select \
c.idut iddm, \
'DM_'||a.codmuni||'_'||b.codmuni b5mcode, \
a.codmuni codmuni1, \
a.muni_eu muni1_eu, \
a.muni_es muni1_es, \
a.muni_fr muni1_fr, \
decode(a.ter_eu,'Gipuzkoa','001','Araba','002','Bizkaia','003','Nafarroa','004','005') codterm1, \
a.ter_eu term1_eu, \
a.ter_es term1_es, \
a.ter_fr term1_fr, \
a.id_area id_area1, \
b.codmuni codmuni2, \
b.muni_eu muni2_eu, \
b.muni_es muni2_es, \
b.muni_fr muni2_fr, \
decode(b.ter_eu,'Gipuzkoa','001','Araba','002','Bizkaia','003','Nafarroa','004','005') codterm2, \
b.ter_eu term2_eu, \
b.ter_es term2_es, \
b.ter_fr term2_fr, \
b.id_area id_area2, \
c.dist_r, \
c.dist_c, \
c.fecha dm_date, \
c.geom \
from mapas_otros.dist_ayunta2_muni a,mapas_otros.dist_ayunta2_muni b,mapas_otros.dist_ayunta2 c \
where a.codmuni=c.codmuni1 \
and b.codmuni=c.codmuni2"
idx_a["dm_distancemunicipalities"]="b5mcode"

# 6. q_municipalcartography (cartografía municipal) (carga: 1'50")
des_a["q_municipalcartography"]="Udal kartografiaren inbentarioa / Inventario de cartografía municipal / Municipal Cartography Inventory"
sql_a["q_municipalcartography"]="select \
a.id_levan, \
'Q_' || a.id_levan b5mcode, \
b.codmuni, \
trim(regexp_substr(c.municipio,'[^/]+',1,1)) muni_eu, \
decode(trim(regexp_substr(c.municipio,'[^/]+',1,2)),null,c.municipio,trim(regexp_substr(c.municipio,'[^/]+',1,2))) muni_es, \
replace(a.nombre,'&#34;','') nombre_eu, \
replace(a.nombre,'&#34;','') nombre_es, \
a.propietario propietario_eu, \
a.propietario propietario_es, \
a.escala escala, \
to_char(a.f_digitalizacion,'YYYY-MM-DD') f_digitalizacion, \
to_char(a.f_levanoriginal,'YYYY-MM-DD') f_levanoriginal, \
to_char(a.f_ultactua,'YYYY-MM-DD') f_ultactua, \
a.empresa empresa, \
'https://b5m.gipuzkoa.eus/map-2022/eu/Q_' || a.id_levan map_link_eu, \
'https://b5m.gipuzkoa.eus/map-2022/es/Q_' || a.id_levan map_link_es, \
d.polygon geom \
from b5mweb_nombres.g_levancarto a,b5mweb_nombres.g_rel_muni_levan b,b5mweb_nombres.n_municipios c,b5mweb_25830.cardigind d \
where a.tag=b.tag \
and b.codmuni=c.codmuni \
and a.tag=d.tag"
idx_a["q_municipalcartography"]="b5mcode"
