#!/bin/bash
#
# ====================================================== #
#  +--------------------------------------------------+  #
#  | gpkg2_sql.sh                                     |  #
#  | SQL sententziak Geopackageak sortzeko            |  #
#  | Sentencias SQL para la generación de Geopackages |  #
#  +--------------------------------------------------+  #
# ====================================================== #
#

# ===========================
#
# Zerrenda osoa / Lista total
#
# ===========================

# 1. m_municipalities
m_gpk="m_municipalities"
m_des=("Udalerria" "Municipio" "Municipality")
m_abs=("B5m M kodea" "B5m código M" "B5m Code M")

# 2. s_regions
s_gpk="s_regions"
s_des=("Eskualdea" "Comarca" "Region")
s_abs=("B5m S kodea" "B5m código S" "B5m Code S")

# 3. d_postaladdresses
d_gpk="d_postaladdresses"
d_des=("Posta helbidea" "Dirección postal" "Postal Address")
d_abs=("B5m D kodea" "B5m código D" "B5m Code D")

# 4. e_buildings
e_gpk="e_buildings"
e_des=("Eraikina" "Edificio" "Building")
e_abs=("B5m E kodea" "B5m código E" "B5m Code E")

# 5. k_streets_buildings
k_gpk="k_streets_buildings"
k_des=("Kalea (eraikin multzoa)" "Calle (conjunto de edificios)" "Street (building set)")
k_abs=("B5m K kodea" "B5m código K" "B5m Code K")

# 6. c_basins
c_gpk="c_basins"
c_des=("Arroa" "Cuenca" "Basin")
c_abs=("B5m C kodea" "B5m código C" "B5m Code C")

# 7. i_hydrography
i_gpk="i_hydrography"
i_des=("Hidrografia" "Hidrografía" "Hydrography")
i_abs=("B5m I kodea" "B5m código I" "B5m Code I")

# 8. z_districts
z_gpk="z_districts"
z_des=("Auzo eta/edo hiri izena" "Barrio y/o nombre urbano" "District and/or urban name")
z_abs=("B5m Z kodea" "B5m código Z" "B5m Code Z")

# 9. g_orography
g_gpk="g_orography"
g_des=("Orografiaren toponimia" "Toponimia de la orografía" "Toponymy of the orography")
g_abs=("B5m G kodea" "B5m código G" "B5m Code G")

# 10. r_grid
r_gpk="r_grid"
r_des=("Lauki-sarea" "Cuadrícula" "Grid")
r_abs=("B5m R kodea" "B5m código R" "B5m Code R")

# 11. dw_download
dw_gpk="dw_download"
dw_des=("Deskargak" "Descargas" "Downloads")
dw_abs=("B5m DW kodea" "B5m código DW" "B5m Code DW")

# 12. sg_geodeticbenchmarks
sg_gpk="sg_geodeticbenchmarks"
sg_des=("Seinale geodesikoa" "Señal geodésica" "Geodetic Benchmark")
sg_abs=("B5m SG kodea" "B5m código SG" "B5m Code SG")

# 13. dm_distancemunicipalities
dm_gpk="dm_distancemunicipalities"
dm_des=("Udalerrien arteko distantzia" "Distancia entre municipios" "Distance Between Municipalities")
dm_abs=("B5m DM kodea" "B5m código DM" "B5m Code DM")

# 14. q_municipalcartography
q_gpk="q_municipalcartography"
q_des=("Udal kartografiaren inbentarioa" "Inventario de cartografía municipal" "Municipal Cartography Inventory")
q_abs=("B5m Q kodea" "B5m código Q" "B5m Code Q")

# 15. poi_pointsofinterest
poi_gpk="poi_pointsofinterest"
poi_des=("Interesgunea" "Punto de interés" "Point of Interest")
poi_abs=("B5m POI kodea" "B5m código POI" "B5m Code POI")

# =================== #
#                     #
# 1. m_municipalities #
#                     #
# =================== #

m_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b
where a.url_2d='M_'||b.codmuni
group by (a.url_2d,a.nombre_e,a.nombre_c,a.tipo_e,a.tipo_c,a.tipo_i)"

m_sql_02="select
a.url_2d b5mcode,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypenamez'':''${s_gpk}'','||
'''description'':''${s_des[0]}'','||
'''abstract'':''${s_abs[0]}'','||
'''numberMatched'':'||
xmlelement(
  e,count(b.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||c.url_2d
    ||'''|''name_eu'':'''||replace(c.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(c.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}]',
chr(38)||'apos;','''')
more_info_eu,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypename'':''${s_gpk}'','||
'''description'':''${s_des[1]}'','||
'''abstract'':''${s_abs[1]}'','||
'''numberMatched'':'||
xmlelement(
  e,count(b.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||c.url_2d
    ||'''|''name_eu'':'''||replace(c.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(c.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}]',
chr(38)||'apos;','''')
more_info_es,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypename'':''${s_gpk}'','||
'''description'':''${s_des[2]}'','||
'''abstract'':''${s_abs[2]}'','||
'''numberMatched'':'||
xmlelement(
  e,count(b.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||c.url_2d
    ||'''|''name_eu'':'''||replace(c.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(c.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}]',
chr(38)||'apos;','''')
more_info_en
from b5mweb_nombres.solr_gen_toponimia_2d a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) b,b5mweb_nombres.solr_gen_toponimia_2d c
where a.url_2d='M_'||b.codmuni
and c.url_2d='S_'||b.idnomcomarca
group by (a.url_2d,b.idnomcomarca)"

m_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${m_gpk} a
left join ${m_gpk}_more_info b
on a.b5mcode = b.b5mcode"

m_idx="b5mcode"

m_fld="b5mcode|B5m kodea|Código b5m|B5m code#\
name_eu|Udalerriaren izen ofiziala euskaraz|Nombre oficial del municipio en euskera|Official name of the municipality in Basque#\
name_es|Udalerriaren izen ofiziala gaztelaniaz|Nombre oficial del municipio en castellano|Official name of the municipality in Spanish#\
b5mcode_region|Eskualdearen b5m kodea|Código b5m de la comarca|Code b5m of the region#\
region_eu|Eskualdearen izena euskaraz|Nombre de la comarca en euskera|Name of the region in Basque#\
region_es|Eskualdearen izena gaztelaniaz|Nombre de la comarca en castellano|Name of the region in Spanish#\
type_eu|Elementu geografikoaren mota euskaraz|Tipo del elemento geográfico en euskera|Type of the geographic feature in Basque#\
type_es|Elementu geografikoaren mota gaztelaniaz|Tipo del elemento geográfico en castellano|Type of the geographic feature in Spanish#\
type_en|Elementu geografikoaren mota ingelesez|Tipo del elemento geográfico en inglés|Type of the geographic feature in English"

# ============ #
#              #
# 2. s_regions #
#              #
# ============ #

s_sql_01="select
a.url_2d b5mcode,
b.idnomcomarca b5mcode_region,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
'Region' type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b
where a.url_2d='S_'||b.idnomcomarca
group by (a.url_2d,b.idnomcomarca,a.tipo_e,a.tipo_c,a.nombre_e,a.nombre_c)"

s_idx="b5mcode"

# ==================== #
#                      #
# 3. d_postaladdresses #
#                      #
# ==================== #

d_sql_01="select"
