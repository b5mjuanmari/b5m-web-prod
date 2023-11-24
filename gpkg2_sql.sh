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

# 4. e_buildings (Edficios) (carga: 1'49")
des_a["e_buildings"]="Eraikina / Edificio / Building"

# 5. k_streets_buildings (calles) (carga: 4'47")
des_a["k_streets_buildings"]="Kalea (eraikin multzoa) / Calle (conjunto de edificios) / Street (building set)"

# 6. c_basins (cuencas) (carga: 28")
des_a["c_basins"]="Arroa / Cuenca / Basin"

# 7. i_hydrography (hidrografía) (carga: 43")
des_a["i_hydrography"]="Hidrografia / Hidrografía / Hydrography"

# 8. z_districts (barrios y/o nombres urbanos) (carga: 22")
des_a["z_districts"]="Auzo eta/edo hiri izena / Barrio y/o nombre urbano / District and/or urban name"

# 9. g_orography (toponimia de la orografía) (carga: 16")
des_a["g_orography"]="Orografiaren toponimia / Toponimia de la orografía / Toponymy of the orography"

# 10. r_grid (cuadrículas, pauta) (carga: 19")
des_a["r_grid"]="Lauki-sarea / Cuadrícula / Grid"

# 11. dw_download (descargas) (carga: 2'25")
des_a["dw_download"]="Deskargak / Descargas / Downloads"

# 12. sg_geodeticbenchmarks (señales geodésicas) (carga: 28")
des_a["sg_geodeticbenchmarks"]="Seinale geodesikoa / Señal geodésica / Geodetic Benchmark"

# 13. dm_distancemunicipalities (distancia entre municipios) (carga: 1h12')
des_a["dm_distancemunicipalities"]="Udalerrien arteko distantzia / Distancia entre municipios / Distance Between Municipalities"

# 14. q_municipalcartography (cartografía municipal) (carga: 25")
des_a["q_municipalcartography"]="Udal kartografiaren inbentarioa / Inventario de cartografía municipal / Municipal Cartography Inventory"

# 15. poi_pointsofinterest (puntos de interés) (carga: 11")
des_a["poi_pointsofinterest"]="Interesgunea / Punto de interés / Point of Interest"

# ===================
#
# 1. m_municipalities
#
# ===================

m_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
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
'''featuretypename'':''${s_gpk}'','||
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

# ============
#
# 2. s_regions
#
# ============

s_sql_01="select"
