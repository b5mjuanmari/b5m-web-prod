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

# =========================== #
#                             #
# Zerrenda osoa / Lista total #
#                             #
# =========================== #

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

# 6. v_streets_axis
v_gpk="v_streets_axis"
v_des=("Kalea (ardatza)" "Calle (eje)" "Street (axis)")
v_abs=("B5m V kodea" "B5m código V" "B5m Code V")

# 7. c_basins
c_gpk="c_basins"
c_des=("Arroa" "Cuenca" "Basin")
c_abs=("B5m C kodea" "B5m código C" "B5m Code C")

# 8. i_hydrography
i_gpk="i_hydrography"
i_des=("Hidrografia" "Hidrografía" "Hydrography")
i_abs=("B5m I kodea" "B5m código I" "B5m Code I")

# 9. z_districts
z_gpk="z_districts"
z_des=("Auzo eta/edo hiri izena" "Barrio y/o nombre urbano" "District and/or urban name")
z_abs=("B5m Z kodea" "B5m código Z" "B5m Code Z")

# 10. g_orography
g_gpk="g_orography"
g_des=("Orografiaren toponimia" "Toponimia de la orografía" "Toponymy of the orography")
g_abs=("B5m G kodea" "B5m código G" "B5m Code G")

# 11. t_roads_railways
t_gpk="t_roads_railways"
t_des=("Errepidea eta trenbidea" "Carretera y ferrocarril" "Road and Railway")
t_abs=("B5m T kodea" "B5m código T" "B5m Code T")

# 12. q_municipalcartography
q_gpk="q_municipalcartography"
q_des=("Udal kartografiaren inbentarioa" "Inventario de cartografía municipal" "Municipal Cartography Inventory")
q_abs=("B5m Q kodea" "B5m código Q" "B5m Code Q")

# 13. sg_geodeticbenchmarks
sg_gpk="sg_geodeticbenchmarks"
sg_des=("Seinale geodesikoa" "Señal geodésica" "Geodetic Benchmark")
sg_abs=("B5m SG kodea" "B5m código SG" "B5m Code SG")

# 14. em_megalithicsites
em_gpk="em_megalithicsites"
em_des=("Estazio megalitikoa" "Estación megalítica" "Megalith Site")
em_abs=("B5m EM kodea" "B5m código EM" "B5m Code EM")

# 15. gk_megaliths
gk_gpk="gk_megaliths"
gk_des=("Megalitoa" "Megalito" "Megalith")
gk_abs=("B5m GK kodea" "B5m código GK" "B5m Code GK")

# 16. cv_speleology
cv_gpk="cv_speleology"
cv_des=("Leizea eta espeleologia" "Cueva y espeleología" "Cave and speleology")
cv_abs=("B5m CV kodea" "B5m código CV" "B5m Code CV")

# 17. bi_biotopes
bi_gpk="bi_biotopes"
bi_des=("Biotopo" "Biotopo" "Biotope")
bi_abs=("B5m BI kodea" "B5m código BI" "B5m Code BI")

# 18. poi_pointsofinterest
poi_gpk="poi_pointsofinterest"
poi_des=("Interesgunea" "Punto de interés" "Point of Interest")
poi_abs=("B5m POI kodea" "B5m código POI" "B5m Code POI")

# 19. dm_distancemunicipalities
dm_gpk="dm_distancemunicipalities"
dm_des=("Udalerrien arteko distantzia" "Distancia entre municipios" "Distance Between Municipalities")
dm_abs=("B5m DM kodea" "B5m código DM" "B5m Code DM")

# 20. r_grid
r_gpk="r_grid"
r_des=("Lauki-sarea" "Cuadrícula" "Grid")
r_abs=("B5m R kodea" "B5m código R" "B5m Code R")

# 21. dw_download
dw_gpk="dw_download"
dw_des=("Deskargak" "Descargas" "Downloads")
dw_abs=("B5m DW kodea" "B5m código DW" "B5m Code DW")

# ========= #
#           #
# Aldagaiak #
#           #
# ========= #

url_map="https://b5m.gipuzkoa.eus/map-2022"
url_map_eu="${url_map}/eu/"
url_map_es="${url_map}/es/"
url_map_en="${url_map}/en/"

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
group by (a.url_2d,a.nombre_e,a.nombre_c,a.tipo_e,a.tipo_c,a.tipo_i)
order by a.url_2d"

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
    ,'#') order by c.nombre_e
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
group by (a.url_2d,b.idnomcomarca)
order by a.url_2d"

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
group by (a.url_2d,b.idnomcomarca,a.tipo_e,a.tipo_c,a.nombre_e,a.nombre_c)
order by a.url_2d"

# ==================== #
#                      #
# 3. d_postaladdresses #
#                      #
# ==================== #

d_sql_01="select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
'Posta helbidea' type_eu,
'Dirección postal' type_es,
'Postal Address' type_en,
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
'Posta helbidea' type_eu,
'Dirección postal' type_es,
'Postal Address' type_en,
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
'Posta helbidea' type_eu,
'Dirección postal' type_es,
'Postal Address' type_en,
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
    ,'#') order by a.calle_e
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
    ,'#') order by a.muni_e
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
    ,'#') order by d.nombre_e
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
from (select distinct idpostal,codcalle,calle_e,calle_c,codmuni,muni_e,muni_c from b5mweb_nombres.n_edifgen) a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
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
group by (b5mcode_d)
order by b5mcode_d"

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
'D_A'||a.idpostal b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
'D_A'||a.idpostal b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
'D_A'||a.idpostal b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)"

e_sql_02="select
'E_A'||a.idut b5mcode,
null b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
and a.idpostal=0
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
null b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
and a.idpostal=0
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||a.idut b5mcode,
null b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
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
and a.idpostal=0
group by (a.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_e,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)"

e_sql_03="$d_sql_02"

e_sql_04="select
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
    ,'#') order by a.muni_e
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
  e,count(b.idnomcomarca)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||decode(b.idnomcomarca,null,null,'S_'||b.idnomcomarca)
    ||'''|''name_eu'':'''||replace(c.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(c.nombre_c,',','|')
    ||'''}'
    ,'#') order by c.nombre_e
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
from b5mweb_nombres.n_edifgen a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) b,b5mweb_nombres.solr_gen_toponimia_2d c
where a.codmuni=b.codmuni
and c.url_2d='S_'||b.idnomcomarca
and a.idpostal=0
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
    ,'#') order by a.muni_e
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
from b5mweb_nombres.n_edifgen a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) b
where a.codmuni=b.codmuni
and a.idpostal=0
and b.idnomcomarca is null
group by (a.idut)"

e_sql_05="$d_sql_03"

e_sql_06="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${e_gpk}_1 a
left join ${e_gpk}_more_info_1 b
on a.b5mcode2 = b.b5mcode"

e_sql_07="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${e_gpk}_2 a
left join ${e_gpk}_more_info_2 b
on a.b5mcode = b.b5mcode"

e_sql_08="select
*
from ${e_gpk}_3
union
select
*
from ${e_gpk}_4"

e_sql_09="select
a.*,
b.poi_eu,
b.poi_es,
b.poi_en
from ${e_gpk}_5 a
left join ${e_gpk}_poi b
on a.b5mcode2 = b.b5mcode"

# ====================== #
#                        #
# 5. k_streets_buildings #
#                        #
# ====================== #

k_sql_01="select
a.url_2d b5mcode,
'Kalea' type_eu,
'Calle' type_es,
'Street' type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.a_edifind b,b5mweb_nombres.n_edifgen c
where a.id_nombre1=c.codmuni
and '0'||a.id_nombre2=c.codcalle
and b.idut=c.idut
group by (a.url_2d,a.nombre_e,a.nombre_c)
order by a.url_2d"

k_sql_02="select
a.url_2d b5mcode,
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
  e,count(b.url_2d)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||b.url_2d
    ||'''|''name_eu'':'''||replace(b.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(b.nombre_e,',','|')
    ||'''}'
    ,'#') order by b.nombre_e
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
  e,count(d.url_2d)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||d.url_2d
    ||'''|''name_eu'':'''||replace(d.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(d.nombre_c,',','|')
    ||'''}'
    ,'#') order by d.nombre_e
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
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_nombres.solr_gen_toponimia_2d b,(select codmuni,idnomcomarca,sdo_aggr_union(sdoaggrtype(polygon,0.005)) polygon from b5mweb_25830.giputz group by codmuni,idnomcomarca) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.id_nombre1=b.id_nombre1
and a.tipo_e='kalea'
and b.tipo_e='udalerria'
and a.id_nombre1=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
group by (a.url_2d)
order by a.url_2d"

k_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${k_gpk} a
left join ${k_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ================= #
#                   #
# 6. v_streets_axis #
#                   #
# ================= #

v_sql_01="select
replace(a.url_2d,'K_','V_') b5mcode,
'Kalea' type_eu,
'Calle' type_es,
'Street' type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polyline,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.vialesind b,b5mweb_nombres.v_rel_vial_tramo c,b5mweb_nombres.n_calles d
where a.idnombre=d.idnombre
and c.idnombre=d.idnombre
and b.idut=c.idut
group by (a.url_2d,a.nombre_e,a.nombre_c)
order by a.url_2d"

v_sql_02="select
replace(a.url_2d,'K_','V_') b5mcode,
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
  e,count(b.url_2d)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||b.url_2d
    ||'''|''name_eu'':'''||replace(b.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(b.nombre_e,',','|')
    ||'''}'
    ,'#') order by b.nombre_e
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
  e,count(d.url_2d)||',''features'':[',
  xmlagg(xmlelement(e,
    '{''b5mcode'':'''||d.url_2d
    ||'''|''name_eu'':'''||replace(d.nombre_e,',','|')
    ||'''|''name_es'':'''||replace(d.nombre_c,',','|')
    ||'''}'
    ,'#') order by d.nombre_e
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
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_nombres.solr_gen_toponimia_2d b,(select codmuni,idnomcomarca,sdo_aggr_union(sdoaggrtype(polygon,0.005)) polygon from b5mweb_25830.giputz group by codmuni,idnomcomarca) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.id_nombre1=b.id_nombre1
and a.tipo_e='kalea'
and b.tipo_e='udalerria'
and a.id_nombre1=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
group by (a.url_2d)
order by a.url_2d"

v_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${v_gpk} a
left join ${v_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# =========== #
#             #
# 7. c_basins #
#             #
# =========== #

c_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
b.polygon geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.cuencap b
where a.url_2d='C_A'||b.idnombre
order by a.url_2d"

c_sql_02="select
a.url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
rtrim(xmlagg(xmlelement(e,d.url_2d,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m,
rtrim(xmlagg(xmlelement(e,d.nombre_e,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m_name_eu,
rtrim(xmlagg(xmlelement(e,d.nombre_c,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.cuencap b,(select codmuni,sdo_aggr_union(sdoaggrtype(polygon,0.005)) polygon from b5mweb_25830.giputz group by codmuni) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.url_2d='C_A'||b.idnombre
and sdo_relate(b.polygon,c.polygon,'mask=contains+covers+equal+touch+overlapbdyintersect+inside')='TRUE'
and c.codmuni=d.id_nombre1
and d.tipo_e in ('agintekidetza','mankomunitatea','partzuergoa','udalerria')
group by (a.url_2d)
order by a.url_2d"

c_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${c_gpk} a
left join ${c_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ================ #
#                  #
# 8. i_hydrography #
#                  #
# ================ #

i_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_concat_lines(b.polyline) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.ibaiak b
where a.id_nombre1=to_char(b.idnombre)
group by(a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,a.idnombre)
order by a.idnombre"

i_sql_02="select
a.url_2d b5mcode,
'"$c_gpk"|"${c_des[0]}"|"${c_des[1]}"|"${c_des[2]}"|"${c_abs[0]}"|"${c_abs[1]}"|"${c_abs[2]}"' b5mcode_others_c_type,
decode(b.idnomcuenca,null,null,'C_A'||b.idnomcuenca) b5mcode_others_c,
b.cuenca_e b5mcode_others_c_name_eu,
b.cuenca_c b5mcode_others_c_name_es,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(a.codmunis,null,null,'M_'||replace(a.codmunis,',','|M_')) b5mcode_others_m,
replace(a.muni_e,',','|') b5mcode_others_m_name_eu,
replace(a.muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.ibaiak b
where a.id_nombre1=to_char(b.idnombre)
group by(a.url_2d,b.idnomcuenca,b.cuenca_e,b.cuenca_c,a.codmunis,a.muni_e,a.muni_c,a.idnombre)
order by a.idnombre"

i_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${i_gpk} a
left join ${i_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ============== #
#                #
# 9. z_districts #
#                #
# ============== #

z_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'0' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.barrioind b,b5mweb_nombres.b_barrios c
where a.id_nombre1=c.idnombre
and b.idut=c.idut
and a.url_2d like 'Z_A%'
group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,a.idnombre)
order by a.idnombre"

z_sql_02="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'Z_A%'
order by to_number(replace(url_2d,'Z_A',''))"

z_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${z_gpk} a
left join ${z_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# =============== #
#                 #
# 10. g_orography #
#                 #
# =============== #

g_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'0' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.montesind b,b5mweb_nombres.o_orograf c
where a.id_nombre1=c.idnombre
and b.idut=c.idut
and a.url_2d like 'G_A%'
group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,a.idnombre)
order by a.idnombre"

g_sql_02="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'G_A%'
order by to_number(replace(url_2d,'G_A',''))"

g_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${g_gpk} a
left join ${g_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ==================== #
#                      #
# 11. t_roads_railways #
#                      #
# ==================== #

t_sql_01="select
a.url_2d b5mcode,
tipo_e type_eu,
tipo_c type_es,
tipo_i type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'1' official,
sdo_aggr_union(sdoaggrtype(b.polyline,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.vialesind b,b5mweb_nombres.v_rel_vial_tramo c
where a.id_nombre1=to_char(c.idnombre)
and b.idut=c.idut
group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c)
order by a.url_2d"

t_sql_02="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'T_A%'
order by to_number(replace(url_2d,'T_A',''))"

t_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${t_gpk} a
left join ${t_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ========================== #
#                            #
# 12. q_municipalcartography #
#                            #
# ========================== #

q_sql_01="select
'Q_' || a.id_levan b5mcode,
replace(a.nombre,'\"','') name_eu,
replace(a.nombre,'\"','') name_es,
a.propietario owner_eu,
a.propietario owner_es,
b.nombre company,
a.escala scale,
to_char(a.f_digitalizacion,'YYYY-MM-DD') digitalisation_date,
to_char(a.f_levanoriginal,'YYYY-MM-DD') survey_date,
to_char(a.f_ultactua,'YYYY-MM-DD') last_update_date,
'"$url_map_eu"Q_'||a.id_levan map_link_eu,
'"$url_map_es"Q_'||a.id_levan map_link_es,
'"$url_map_en"Q_'||a.id_levan map_link_en,
'"$updd"' update_date,
'1' official,
c.geom
from b5mweb_nombres.g_levantamiento a, b5mweb_nombres.g_empresas b,b5mweb_25830.cartoaggr c
where a.id_levan=c.id_levan
and a.id_empresa=b.id_empresa
order by a.id_levan"

q_sql_02="select
'Q_' || a.id_levan b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
rtrim(xmlagg(xmlelement(e,'M_'||c.codmuni,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m,
rtrim(xmlagg(xmlelement(e,d.nombre_e,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m_name_eu,
rtrim(xmlagg(xmlelement(e,d.nombre_c,'|').extract('//text()') order by d.nombre_e).getclobval(),'|') b5mcode_others_m_name_es
from b5mweb_nombres.g_levancarto a,b5mweb_nombres.g_rel_muni_levan b,b5mweb_nombres.n_municipios c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.tag=b.tag
and b.codmuni=c.codmuni
and c.codmuni=d.id_nombre1
and d.tipo_e in ('agintekidetza','mankomunitatea','partzuergoa','udalerria')
group by a.id_levan
order by a.id_levan"

q_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${q_gpk} a
left join ${q_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ========================= #
#                           #
# 13. sg_geodeticbenchmarks #
#                           #
# ========================= #

sg_aju_eu="Doikuntza geodesikoa"
sg_sen_eu="Seinale geodesikoa"
sg_aju_es="Ajuste geodésico"
sg_sen_es="Señal geodésica"
sg_aju_en="Geodetic Adjustment"
sg_sen_en="Geodetic Benchmark"
sg_url="https://b5m.gipuzkoa.eus/geodesia/pdf"

sg_sql_01="select
'SG_'||pgeod_id b5mcode,
nombre name_eu,
nombre name_es,
decode(ajuste,1,'${sg_aju_eu}','${sg_sen_eu}') type_eu,
decode(ajuste,1,'${sg_aju_es}','${sg_sen_es}') type_es,
decode(ajuste,1,'${sg_aju_en}','${sg_sen_en}') type_en,
'${sg_url}/'||archivo link,
file_type,
size_kb,
'"$updd"' update_date,
'1' official,
geom
from o_mw_bta.puntogeodesicobta
where visible_web=1
order by pgeod_id"

sg_sql_02="select
'SG_'||a.pgeod_id b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
'M_'||a.codmuni b5mcode_others_m,
trim(regexp_substr(b.municipio,'[^/]+',1,1)) b5mcode_others_m_name_eu,
decode(trim(regexp_substr(b.municipio,'[^/]+',1,2)),null,b.municipio,trim(regexp_substr(b.municipio,'[^/]+',1,2))) b5mcode_others_m_name_es,
'"$s_gpk"|"${s_des[0]}"|"${s_des[1]}"|"${s_des[2]}"|"${s_abs[0]}"|"${s_abs[1]}"|"${s_abs[2]}"' b5mcode_others_s_type,
decode(c.idnomcomarca,null,null,'S_'||c.idnomcomarca) b5mcode_others_s,
d.nombre_e b5mcode_others_s_name_eu,
d.nombre_c b5mcode_others_s_name_es
from o_mw_bta.puntogeodesicobta a,b5mweb_nombres.n_municipios b,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.codmuni=b.codmuni
and a.visible_web=1
and a.codmuni=c.codmuni
and d.url_2d='S_'||c.idnomcomarca
order by a.pgeod_id"

sg_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${sg_gpk} a
left join ${sg_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ====================== #
#                        #
# 14. em_megalithicsites #
#                        #
# ====================== #

em_sql_01="select
'EM_A'||idnombre b5mcode,
izena name_eu,
nombre name_es,
tipo_e type_eu,
tipo_c type_es,
tipo_c type_en,
'"$url_map_eu"' || 'EM_A'||idnombre map_link_eu,
'"$url_map_es"' || 'EM_A'||idnombre map_link_es,
'"$url_map_en"' || 'EM_A'||idnombre map_link_en,
'"$updd"' update_date,
'1' official,
polygon
from b5mweb_25830.monuestmegal
order by idnombre"

em_sql_02="select
'EM_A'||a.idnombre b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
rtrim(xmlagg(xmlelement(e,'M_'||b.codmuni,'|').extract('//text()') order by c.nombre_e).getclobval(),'|') b5mcode_others_m,
rtrim(xmlagg(xmlelement(e,c.nombre_e,'|').extract('//text()') order by c.nombre_e).getclobval(),'|') b5mcode_others_m_name_eu,
rtrim(xmlagg(xmlelement(e,c.nombre_c,'|').extract('//text()') order by c.nombre_e).getclobval(),'|') b5mcode_others_m_name_es
from b5mweb_25830.monuestmegal a,(select codmuni,sdo_aggr_union(sdoaggrtype(polygon,0.005)) polygon from b5mweb_25830.giputz group by codmuni) b,b5mweb_nombres.solr_gen_toponimia_2d c
where sdo_relate(a.polygon,b.polygon,'mask=contains+covers+equal+touch+overlapbdyintersect+inside')='TRUE'
and b.codmuni=c.id_nombre1
and c.tipo_e in ('agintekidetza','mankomunitatea','partzuergoa','udalerria')
group by a.idnombre
order by a.idnombre"

em_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${em_gpk} a
left join ${em_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ================ #
#                  #
# 15. gk_megaliths #
#                  #
# ================ #

gk_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$url_map_eu"'||a.url_2d map_link_eu,
'"$url_map_es"'||a.url_2d map_link_es,
'"$url_map_en"'||a.url_2d map_link_en,
b.bopv official_gazette_link,
'"$updd"' update_date,
'1' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.monu3 b
where a.id_nombre1=to_char(b.tag)
order by a.id_nombre1"

gk_sql_02="select
distinct a.url_2d b5mcode,
'"$em_gpk"|"${em_des[0]}"|"${em_des[1]}"|"${em_des[2]}"|"${em_abs[0]}"|"${em_abs[1]}"|"${em_abs[2]}"' b5mcode_others_em_type,
decode(b.idnomestacion,null,null,'EM_A'||b.idnomestacion) b5mcode_others_em,
b.estazio_megal b5mcode_others_em_name_eu,
b.estacion_megal b5mcode_others_em_name_es,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(a.codmunis,null,null,'M_'||replace(a.codmunis,',','|M_')) b5mcode_others_m,
replace(a.muni_e,',','|') b5mcode_others_m_name_eu,
replace(a.muni_c,',','|') b5mcode_others_m_name_es,
'"$s_gpk"|"${s_des[0]}"|"${s_des[1]}"|"${s_des[2]}"|"${s_abs[0]}"|"${s_abs[1]}"|"${s_abs[2]}"' b5mcode_others_s_type,
decode(c.idnomcomarca,null,null,'S_'||c.idnomcomarca) b5mcode_others_s,
d.nombre_e b5mcode_others_s_name_eu,
d.nombre_c b5mcode_others_s_name_es
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.monu3 b,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.url_2d like 'GK_A%'
and a.id_nombre1=to_char(b.tag)
and a.codmunis=c.codmuni(+)
and 'S_'||c.idnomcomarca=d.url_2d(+)
order by to_number(replace(a.url_2d,'GK_A',''))"

gk_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${gk_gpk} a
left join ${gk_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ================= #
#                   #
# 16. cv_speleology #
#                   #
# ================= #

cv_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$url_map_eu"'||a.url_2d map_link_eu,
'"$url_map_es"'||a.url_2d map_link_es,
'"$url_map_en"'||a.url_2d map_link_en,
b.web_e catalog_link,
b.origen_e source_eu,
b.origen_c source_es,
b.origen_c source_en,
'"$updd"' update_date,
'1' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.cuevas b
where a.id_nombre1=b.tag
order by a.id_nombre1"

# ======= #
#         #
# 99. end #
#         #
# ======= #
