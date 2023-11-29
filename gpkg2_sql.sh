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
'''featuretypename'':''ZZ_S_FTN'','||
'''description'':''ZZ_S_DES'','||
'''abstract'':''ZZ_S_ABS'','||
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
more_info
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

d_sql_01="select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.a_edifind b
where a.idut=b.idut
and a.idpostal<>0
group by (a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.o_edifind b
where a.idut=b.idut
and a.idpostal<>0
group by (a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.s_edifind b
where a.idut=b.idut
and a.idpostal<>0
group by (a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)"

d_sql_02="select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_K_FTN'','||
'''description'':''ZZ_K_DES'','||
'''abstract'':''ZZ_K_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(a.codmuni)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||'K_'||a.codmuni||'_'||substr(a.codcalle,2)
    ||'''|''name_eu'':'''||replace(a.calle_e,',','|')
    ||'''|''name_es'':'''||replace(decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c),',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'},{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_M_FTN'','||
'''description'':''ZZ_M_DES'','||
'''abstract'':''ZZ_M_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(a.codmuni)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||'M_'||a.codmuni
    ||'''|''name_eu'':'''||replace(a.muni_e,',','|')
    ||'''|''name_es'':'''||replace(a.muni_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'},{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_S_FTN'','||
'''description'':''ZZ_S_DES'','||
'''abstract'':''ZZ_S_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(c.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||decode(c.idnomcomarca,null,null,'S_'||c.idnomcomarca)
    ||'''|''name_eu'':'''||replace(d.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(d.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}'
||']',
chr(38)||'apos;','''')
more_info
from b5mweb_nombres.n_edifgen a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.codmuni=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
and a.idpostal<>0
group by (a.idpostal)"

d_sql_03="select
b5mcode_d b5mcode,
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''class'':'''||replace(class_eu,',','|')||'''|''class_description'':'''||replace(class_description_eu,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_eu,',','|')||'''|''category_description'':'''||replace(category_description_eu,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_eu,class_eu,name_eu,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','poi_null') poi_eu,
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''class'':'''||replace(class_es,',','|')||'''|''class_description'':'''||replace(class_description_es,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_es,',','|')||'''|''category_description'':'''||replace(category_description_es,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_es,class_es,name_es,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','poi_null') poi_es,
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''class'':'''||replace(class_en,',','|')||'''|''class_description'':'''||replace(class_description_en,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_en,',','|')||'''|''category_description'':'''||replace(category_description_en,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_en,class_en,name_eu,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','poi_null') poi_en
from b5mweb_nombres.solr_poi_2d
group by (b5mcode_d)"

d_sql_04="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${d_gpk} a
left join ${d_gpk}_more_info b
on a.b5mcode = b.b5mcode"

d_sql_05="select
a.*,
b.poi_eu,
b.poi_es,
b.poi_en
from ${d_gpk}_2 a
left join ${d_gpk}_poi b
on a.b5mcode = b.b5mcode"

# ============== #
#                #
# 4. e_buildings #
#                #
# ============== #

e_sql_01="select
'E_A'||a.idut b5mcode,
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode2,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.a_edifind b
where a.idut=b.idut
group by (a.idut,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode2,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.o_edifind b
where a.idut=b.idut
group by (a.idut,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode2,
replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||' '||a.muni_e),' - , ',',') name_eu,
replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||' '||a.muni_c),' - , ',',') name_es,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) street_es,
a.noportal door_number,
decode(a.bis,' ','',a.bis) bis,
a.accesorio accessory,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_building_eu,
a.nomedif_e name_building_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.s_edifind b
where a.idut=b.idut
group by (a.idut,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)"

e_sql_02="select
'E_A'||a.idut b5mcode,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_K_FTN'','||
'''description'':''ZZ_K_DES'','||
'''abstract'':''ZZ_K_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(a.codmuni)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||'K_'||a.codmuni||'_'||substr(a.codcalle,2)
    ||'''|''name_eu'':'''||replace(a.calle_e,',','|')
    ||'''|''name_es'':'''||replace(decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c),',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'},{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_M_FTN'','||
'''description'':''ZZ_M_DES'','||
'''abstract'':''ZZ_M_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(a.codmuni)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||'M_'||a.codmuni
    ||'''|''name_eu'':'''||replace(a.muni_e,',','|')
    ||'''|''name_es'':'''||replace(a.muni_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'},{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_S_FTN'','||
'''description'':''ZZ_S_DES'','||
'''abstract'':''ZZ_S_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(c.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||decode(c.idnomcomarca,null,null,'S_'||c.idnomcomarca)
    ||'''|''name_eu'':'''||replace(d.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(d.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}'
||']',
chr(38)||'apos;','''')
more_info
from b5mweb_nombres.n_edifgen a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.codmuni=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
and a.idpostal<>0
group by (a.idut)
union all
select
'E_A'||a.idut b5mcode,
replace(
'[{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_M_FTN'','||
'''description'':''ZZ_M_DES'','||
'''abstract'':''ZZ_M_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(a.codmuni)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||'M_'||a.codmuni
    ||'''|''name_eu'':'''||replace(a.muni_e,',','|')
    ||'''|''name_es'':'''||replace(a.muni_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'},{'||
rtrim(
replace(
replace(
'''featuretypename'':''ZZ_S_FTN'','||
'''description'':''ZZ_S_DES'','||
'''abstract'':''ZZ_S_ABS'','||
'''numberMatched'':'||
xmlelement(
  e,count(c.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||decode(c.idnomcomarca,null,null,'S_'||c.idnomcomarca)
    ||'''|''name_eu'':'''||replace(d.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(d.nombre_c,',','|')
    ||'''}'
    ,'#')
  )
).extract('//text()').getclobval(),
'|',','),
'#',','),
',')
||']'
||'}'
||']',
chr(38)||'apos;','''')
more_info
from b5mweb_nombres.n_edifgen a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.codmuni=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
and a.idpostal=0
group by (a.idut)"

e_sql_03="$d_sql_03"

e_sql_04="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${e_gpk} a
left join ${e_gpk}_more_info b
on a.b5mcode = b.b5mcode"

e_sql_05="select
a.*,
b.poi_eu,
b.poi_es,
b.poi_en
from ${e_gpk}_2 a
left join ${e_gpk}_poi b
on a.b5mcode2 = b.b5mcode"
