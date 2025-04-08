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

# 1. h_historicalterritories
h_gpk="h_historicalterritories"
h_des=("Lurralde Historikoa" "Territorio Histórico" "Historical Territory")
h_abs=("B5m H kodea" "B5m código H" "B5m Code H")

# 2. m_municipalities
m_gpk="m_municipalities"
m_des=("Udalerria" "Municipio" "Municipality")
m_des2=("Igarotzen diren udalerriak" "Municipios por los que discurre" "Municipalities through which it flows")
m_des3=("Zein udalerritatik igarotzen den" "Municipios por los que pasa" "Municipalities through which it passes")
m_abs=("B5m M kodea" "B5m código M" "B5m Code M")

# 3. s_regions
s_gpk="s_regions"
s_des=("Eskualdea" "Comarca" "Region")
s_abs=("B5m S kodea" "B5m código S" "B5m Code S")

# 4. d_postaladdresses
d_gpk="d_postaladdresses"
d_des=("Posta helbidea" "Dirección postal" "Postal Address")
d_abs=("B5m D kodea" "B5m código D" "B5m Code D")

# 5. e_buildings
e_gpk="e_buildings"
e_des=("Eraikina" "Edificio" "Building")
e_abs=("B5m E kodea" "B5m código E" "B5m Code E")

# 6. k_streets_buildings
k_gpk="k_streets_buildings"
k_des=("Kalea (eraikin multzoa)" "Calle (conjunto de edificios)" "Street (building set)")
k_abs=("B5m K kodea" "B5m código K" "B5m Code K")

# 7. v_streets_axis
v_gpk="v_streets_axis"
v_des=("Kalea (ardatza)" "Calle (eje)" "Street (axis)")
v_abs=("B5m V kodea" "B5m código V" "B5m Code V")

# 8. c_basins
c_gpk="c_basins"
c_des=("Arro hidrografikoa" "Cuenca hidrográfica" "Hydrographic Basin")
c_abs=("B5m C kodea" "B5m código C" "B5m Code C")

# 9. i_hydrography
i_gpk="i_hydrography"
i_des=("Hidrografia" "Hidrografía" "Hydrography")
i_abs=("B5m I kodea" "B5m código I" "B5m Code I")

# 10. z_districts
z_gpk="z_districts"
z_des=("Auzo eta/edo hiri izena" "Barrio y/o nombre urbano" "District and/or urban name")
z_abs=("B5m Z kodea" "B5m código Z" "B5m Code Z")

# 11. g_orography
g_gpk="g_orography"
g_des=("Orografiaren toponimia" "Toponimia de la orografía" "Toponymy of the orography")
g_abs=("B5m G kodea" "B5m código G" "B5m Code G")

# 12. t_roads_railways
t_gpk="t_roads_railways"
kp_gpk="kp_kilometre_points"
t_des=("Errepidea eta trenbidea" "Carretera y ferrocarril" "Road and Railway")
kp_des=("(kilometro puntua)" "(punto kilométrico)" "(Kilometre Point")
t_abs=("B5m T kodea" "B5m código T" "B5m Code T")

# 13. q_municipalcartography
q_gpk="q_municipalcartography"
q_des=("Udal kartografiaren inbentarioa" "Inventario de cartografía municipal" "Municipal Cartography Inventory")
q_abs=("B5m Q kodea" "B5m código Q" "B5m Code Q")

# 14. sg_geodeticbenchmarks
sg_gpk="sg_geodeticbenchmarks"
sg_des=("Seinale geodesikoa" "Señal geodésica" "Geodetic Benchmark")
sg_abs=("B5m SG kodea" "B5m código SG" "B5m Code SG")

# 15. em_megalithicsites
em_gpk="em_megalithicsites"
em_des=("Estazio megalitikoa" "Estación megalítica" "Megalith Site")
em_abs=("B5m EM kodea" "B5m código EM" "B5m Code EM")

# 16. gk_megaliths
gk_gpk="gk_megaliths"
gk_des=("Megalitoa" "Megalito" "Megalith")
gk_abs=("B5m GK kodea" "B5m código GK" "B5m Code GK")

# 17. cv_speleology
cv_gpk="cv_speleology"
cv_des=("Leizea eta espeleologia" "Cueva y espeleología" "Cave and speleology")
cv_abs=("B5m CV kodea" "B5m código CV" "B5m Code CV")

# 18. bi_biotopes
bi_gpk="bi_biotopes"
bi_des=("Biotopoa" "Biotopo" "Biotope")
bi_abs=("B5m BI kodea" "B5m código BI" "B5m Code BI")

# 19. poi_pointsofinterest
poi_gpk="poi_pointsofinterest"
poi_des=("Interesgunea" "Punto de interés" "Point of Interest")
poi_abs=("B5m POI kodea" "B5m código POI" "B5m Code POI")

# 20. dm_distancemunicipalities
dm_gpk="dm_distancemunicipalities"
dm_des=("Udalerrien arteko distantzia" "Distancia entre municipios" "Distance Between Municipalities")
dm_abs=("B5m DM kodea" "B5m código DM" "B5m Code DM")

# 21. r_grid
r_gpk="r_grid"
r_des=("Lauki-sarea" "Cuadrícula" "Grid")
r_abs=("B5m R kodea" "B5m código R" "B5m Code R")

# 22. dw_download
dw_gpk="dw_download"
dw_des=("Deskargak" "Descargas" "Downloads")
dw_abs=("B5m DW kodea" "B5m código DW" "B5m Code DW")

# 23. ac_municipal_boundaries
ac_gpk="ac_municipal_boundaries"
ac_des=("Udal muga" "Límite municipal" "Municipal Boundary")
ac_abs=("B5m AC kodea" "B5m código AC" "B5m Code AC")

# 24. ac_municipal_boundaries
mg_gpk="mg_landmarks"
mg_des=("Udal mugarria" "Mojón de límite municipal" "Municipal Boundary Landmark")
mg_abs=("B5m MG kodea" "B5m código MG" "B5m Code MG")

# 25. mu_public_utility_woodlands
mu_gpk="mu_public_utility_woodlands"
mu_des=("Onura publikoko mendiak" "Montes de utilidad pública" "Public Utility Woodlands")
mu_abs=("B5m MU kodea" "B5m código MU" "B5m Code MU")

# ========= #
#           #
# Aldagaiak #
#           #
# ========= #

url_cat="https://www.aranzadi.eus"
url_cat_eu="${url_cat}/eu/espelelogia-katalogoa/ficha/"
url_cat_es="${url_cat}/es/catalogo-espeleologico/ficha/"
ora_sch_01="b5mweb_nombres"
dw_fs="dw_file_sizes"
dw_geoc="dw_geocassini"
dw_id_fs="id_fs"

# ======== #
#          #
# Official #
#          #
# ======== #

oft0eu="Elementu honen muga ez dago legez araututa."
oft0es="El límite de este elemento no está regulado de forma legal."
oft0en="The limit of this element is not regulated by law."
oft1eu=""
oft1es=""
oft1en=""

# ========================== #
#                            #
# 1. h_historicalterritories #
#                            #
# ========================== #

h_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.lurralint b
where a.url_2d like 'H_%'
group by (a.url_2d,a.nombre_e,a.nombre_c,a.tipo_e,a.tipo_c,a.tipo_i)
order by a.url_2d"

# =================== #
#                     #
# 2. m_municipalities #
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b
where a.url_2d='M_'||b.codmuni
group by (a.url_2d,a.nombre_e,a.nombre_c,a.tipo_e,a.tipo_c,a.tipo_i)
union all
select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipu_a b
where a.idnombre=b.idnombre
and a.tipo_e='enklabea'
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
# 3. s_regions #
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b
where a.url_2d='S_'||b.idnomcomarca
group by (a.url_2d,b.idnomcomarca,a.tipo_e,a.tipo_c,a.nombre_e,a.nombre_c)
order by a.url_2d"

# ==================== #
#                      #
# 4. d_postaladdresses #
#                      #
# ==================== #

d_sql_01="select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
'Posta helbidea' type_eu,
'Dirección postal' type_es,
'Postal Address' type_en,
replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),'  ',' ') name_eu,
replace(replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),'  ',' ') name_es,
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),'  ',' ') name_eu,
replace(replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),'  ',' ') name_es,
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),'  ',' ') name_eu,
replace(replace(decode(a.nomedif_e,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_e||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),'  ',' ') name_es,
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''type'':'''||replace(type_eu,',','|')||'''|''class'':'''||replace(class_eu,',','|')||'''|''class_description'':'''||replace(class_description_eu,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_eu,',','|')||'''|''category_description'':'''||replace(category_description_eu,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_eu,class_eu,name_eu,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','json_null') poi_eu,
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''type'':'''||replace(type_es,',','|')||'''|''class'':'''||replace(class_es,',','|')||'''|''class_description'':'''||replace(class_description_es,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_es,',','|')||'''|''category_description'':'''||replace(category_description_es,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_es,class_es,name_es,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','json_null') poi_es,
replace('['||rtrim(replace(replace(replace(replace(replace(rtrim(xmlagg(xmlelement(e,'{''b5mcode_poi'':'''||b5mcode||'''|''name_eu'':'''||replace(name_eu,',','|')||'''|''name_es'':'''||replace(name_es,',','|')||'''|''type'':'''||replace(type_en,',','|')||'''|''class'':'''||replace(class_en,',','|')||'''|''class_description'':'''||replace(class_description_en,',','|')||'''|''class_icon'':'''||replace(class_icon,',','|')||'''|''category'':'''||replace(category_en,',','|')||'''|''category_description'':'''||replace(category_description_en,',','|')||'''|''category_icon'':'''||replace(category_icon,',','|')||'''}','#').extract('//text()') order by category_en,class_en,name_eu,b5mcode).getclobval(),','),chr(38)||'apos;',''''),'{''b5mcode_poi'':''''|''name_eu'':''''|''name_es'':''''|''class'':''''|''class_description'':''''|''class_icon'':''''|''category'':''''|''category_description'':''''|''category_icon'':''''}#',''),',',''),'|',','),'#',','),',')||']','[]','json_null') poi_en
from b5mweb_nombres.solr_poi_2d
group by (b5mcode_d)
order by b5mcode_d"

d_sql_04="select
decode(a.idpostal, 0, null, 'D_A'||a.idpostal) b5mcode,
replace(replace('['||replace(xmlagg(xmlelement(e,'{''codphoto'':''PH_'||replace(b.nombre,'.jpg','')||''',''url_photo'':''https://b5m.gipuzkoa.eus/web5000/img/build/'||b.nombre||''',''year'':'''||b.f_foto||'''},').extract('//text()') order by b.nombre).getclobval(),chr(38)||'apos;','''')||']',',]',']'),'[]','json_null') photographs
from b5mweb_nombres.n_edifgen a,b5mweb_nombres.n_edifoto2 b
where a.idut=b.idut
and a.idpostal<>0
group by (a.idpostal)
order by a.idpostal"

d_sql_05="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${d_gpk} a
left join ${d_gpk}_more_info b
on a.b5mcode = b.b5mcode"

d_sql_06="select
a.*,
b.poi_eu,
b.poi_es,
b.poi_en
from ${d_gpk}_2 a
left join ${d_gpk}_poi b
on a.b5mcode = b.b5mcode"

d_sql_07="select
a.*,
b.photographs
from ${d_gpk}_3 a
left join ${d_gpk}_photo b
on a.b5mcode = b.b5mcode"

# ============== #
#                #
# 5. e_buildings #
#                #
# ============== #

e_sql_01="select
'E_A'||b.idut b5mcode,
decode(a.idpostal,null,null,0,null,'D_A'||a.idpostal) b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
replace(replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),',  ',''),'  ',' ') name_eu,
replace(replace(replace(decode(a.nomedif_c,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_c||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),',  ',''),'  ',' ') name_es,
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
a.nomedif_c name_building_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.a_edifind b
where a.idut(+)=b.idut
group by (b.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_c,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||b.idut b5mcode,
decode(a.idpostal,null,null,0,null,'D_A'||a.idpostal) b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
replace(replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),',  ',''),'  ',' ') name_eu,
replace(replace(replace(decode(a.nomedif_c,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_c||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),',  ',''),'  ',' ') name_es,
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
a.nomedif_c name_building_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.o_edifind b
where a.idut(+)=b.idut
group by (b.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_c,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)
union all
select
'E_A'||b.idut b5mcode,
decode(a.idpostal,null,null,0,null,'D_A'||a.idpostal) b5mcode2,
upper(substr(b.tipo_eu,1,1))||substr(b.tipo_eu,2,length(b.tipo_eu)-1) type_eu,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_es,
upper(substr(b.tipo_es,1,1))||substr(b.tipo_es,2,length(b.tipo_es)-1) type_en,
replace(replace(replace(decode(a.nomedif_e,null,a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e,a.nomedif_e||' - '||a.calle_e||', '||a.noportal||a.bis||' '||a.muni_e),' - , ',','),',  ',''),'  ',' ') name_eu,
replace(replace(replace(decode(a.nomedif_c,null,decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c,a.nomedif_c||' - '||decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c)||', '||a.noportal||a.bis||' '||a.muni_c),' - , ',','),',  ',''),'  ',' ') name_es,
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
a.nomedif_c name_building_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.s_edifind b
where a.idut(+)=b.idut
group by (b.idut,b.tipo_eu,b.tipo_es,b.tipo_es,a.idpostal,a.nomedif_e,a.nomedif_c,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.accesorio,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c)"

e_sql_02="$d_sql_02"

e_sql_03="select
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

e_sql_04="$d_sql_03"

e_sql_05="select
'E_A'||a.idut b5mcode,
replace(replace('['||replace(xmlagg(xmlelement(e,'{''codphoto'':''PH_'||replace(b.nombre,'.jpg','')||''',''url_photo'':''${photob}'||b.nombre||''',''year'':'''||b.f_foto||'''},').extract('//text()') order by b.nombre).getclobval(),chr(38)||'apos;','''')||']',',]',']'),'[]','json_null') photographs
from (select distinct idut from b5mweb_25830.a_edifind) a,b5mweb_nombres.n_edifoto2 b
where a.idut=b.idut
group by (a.idut)
union all
select
'E_A'||a.idut b5mcode,
replace(replace('['||replace(xmlagg(xmlelement(e,'{''codphoto'':''PH_'||replace(b.nombre,'.jpg','')||''',''url_photo'':''${photob}'||b.nombre||''',''year'':'''||b.f_foto||'''},').extract('//text()') order by b.nombre).getclobval(),chr(38)||'apos;','''')||']',',]',']'),'[]','json_null') photographs
from (select distinct idut from b5mweb_25830.o_edifind) a,b5mweb_nombres.n_edifoto2 b
where a.idut=b.idut
group by (a.idut)
union all
select
'E_A'||a.idut b5mcode,
replace(replace('['||replace(xmlagg(xmlelement(e,'{''codphoto'':''PH_'||replace(b.nombre,'.jpg','')||''',''url_photo'':''${photob}'||b.nombre||''',''year'':'''||b.f_foto||'''},').extract('//text()') order by b.nombre).getclobval(),chr(38)||'apos;','''')||']',',]',']'),'[]','json_null') photographs
from (select distinct idut from b5mweb_25830.s_edifind) a,b5mweb_nombres.n_edifoto2 b
where a.idut=b.idut
group by (a.idut)"

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
b.poi_eu,
b.poi_es,
b.poi_en
from ${e_gpk}_2 a
left join ${e_gpk}_poi b
on a.b5mcode2 = b.b5mcode"

e_sql_08="select
a.*,
b.photographs
from ${e_gpk}_3 a
left join ${e_gpk}_photo b
on a.b5mcode = b.b5mcode"

# ====================== #
#                        #
# 6. k_streets_buildings #
#                        #
# ====================== #

k_sql_01="select
a.url_2d b5mcode,
'Kalea' type_eu,
'Calle' type_es,
'Street' type_en,
a.nombre_e name_eu,
decode(regexp_replace(a.nombre_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.nombre_c,'[^,]+',1,1),a.nombre_c) name_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 7. v_streets_axis #
#                   #
# ================= #

v_sql_01="select
replace(a.url_2d,'K_','V_') b5mcode,
'Kalea' type_eu,
'Calle' type_es,
'Street' type_en,
a.nombre_e name_eu,
decode(regexp_replace(a.nombre_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.nombre_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.nombre_c,'[^,]+',1,1),a.nombre_c) name_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 8. c_basins #
#             #
# =========== #

c_des=("Arro hidrografikoa" "Cuenca hidrográfica" "Hydrographic Basin")
c_sql_01="select
a.url_2d b5mcode,
--upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
--upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
--upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
'Arro hidrografikoa' type_eu,
'Cuenca hidrográfica' type_es,
'Hydrographic Basin' type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 9. i_hydrography #
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
'"$m_gpk"|"${m_des2[0]}"|"${m_des2[1]}"|"${m_des2[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
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

# =============== #
#                 #
# 10. z_districts #
#                 #
# =============== #

z_sql_01="select
a.url_2d b5mcode,
upper(substr(a.tipo_e,1,1))||substr(a.tipo_e,2,length(a.tipo_e)-1) type_eu,
upper(substr(a.tipo_c,1,1))||substr(a.tipo_c,2,length(a.tipo_c)-1) type_es,
upper(substr(a.tipo_i,1,1))||substr(a.tipo_i,2,length(a.tipo_i)-1) type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'{\"official_id\":\"0\",\"official_text_eu\":\"${oft0eu}\",\"official_text_es\":\"${oft0es}\",\"official_text_en\":\"${oft0en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.barrioind b,b5mweb_nombres.b_barrios c
where a.id_nombre1=c.idnombre
and b.idut=c.idut
and a.url_2d like 'Z_A%'
group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,a.idnombre)
union all
select
a.url_2d b5mcode,
'Auzo eta/edo hiri izena' type_eu,
'Barrio y/o nombre urbano' type_es,
'District and/or urban name' type_en,
a.nombre_e name_eu,
a.nombre_c name_es,
'"$updd"' update_date,
'{\"official_id\":\"0\",\"official_text_eu\":\"${oft0eu}\",\"official_text_es\":\"${oft0es}\",\"official_text_en\":\"${oft0en}\"}' official,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.barrioind b,b5mweb_nombres.b_barrios c
where a.idnombre=c.idnombre
and b.idut=c.idut
and a.url_2d like 'K_%'
group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,a.idnombre)
order by b5mcode"

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
# 11. g_orography #
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
'{\"official_id\":\"0\",\"official_text_eu\":\"${oft0eu}\",\"official_text_es\":\"${oft0es}\",\"official_text_en\":\"${oft0en}\"}' official,
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
# 12. t_roads_railways #
#                      #
# ==================== #

t_sql_01="select
b5mcode,
type_eu,
type_es,
type_en,
name_eu,
name_es,
update_date,
official,
sdo_aggr_union(sdoaggrtype(geom,0.005)) geom
from
(
  select
  b5mcode,
  type_eu,
  type_es,
  type_en,
  name_eu,
  name_es,
  update_date,
  official,
  sdo_aggr_union(sdoaggrtype(geom,0.005)) geom
  from
  (
    select
    b5mcode,
    type_eu,
    type_es,
    type_en,
    name_eu,
    name_es,
    update_date,
    official,
    sdo_aggr_union(sdoaggrtype(geom,0.005)) geom
    from
    (
      select
      a.url_2d b5mcode,
      tipo_e type_eu,
      tipo_c type_es,
      tipo_i type_en,
      a.nombre_e name_eu,
      a.nombre_c name_es,
      '"$updd"' update_date,
      '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
      sdo_aggr_union(sdoaggrtype(b.polyline,0.005)) geom
      from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.vialesind b,b5mweb_nombres.v_rel_vial_tramo c
      where a.id_nombre1=to_char(c.idnombre)
      and b.idut=c.idut
      and a.id_nombre2 in ('0990','9000')
      group by (a.url_2d,a.tipo_e,a.tipo_c,a.tipo_i,a.nombre_e,a.nombre_c,mod(rownum,1000))
    )
    group by (b5mcode,type_eu,type_es,type_en,name_eu,name_es,update_date,official,mod(rownum,100))
  )
  group by (b5mcode,type_eu,type_es,type_en,name_eu,name_es,update_date,official,mod(rownum,10))
)
group by (b5mcode,type_eu,type_es,type_en,name_eu,name_es,update_date,official)
order by b5mcode"

t_sql_02="select
a.url_2d||'_'||decode(a.sentido_eu,'joan',1,2) kpcode,
a.url_2d b5mcode,
'kilometro puntua' type_eu,
'punto kilométrico' type_es,
'kilometre point' type_en,
a.nombre||' '||a.sentido_eu name_eu,
a.nombre||' '||a.sentido_es name_es,
a.pk kp,
a.carre road_name_eu,
a.carre road_name_es,
a.sentido_eu way_eu,
a.sentido_es way_es,
a.sentido_en way_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.point geom
from b5mweb_nombres.solr_pkil_2d a,b5mweb_25830.pkil b
where a.idnombre=b.idnombre
order by a.url_2d"

t_sql_03="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des3[0]}"|"${m_des3[1]}"|"${m_des3[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'T_A%'
order by to_number(replace(url_2d,'T_A',''))"

t_sql_04="select
url_2d||'_'||decode(sentido_eu,'joan',1,2) kpcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,'ZZKP','M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
decode(muni_e,null,'ZZKP',replace(muni_e,',','|')) b5mcode_others_m_name_eu,
decode(muni_c,null,'ZZKP',replace(muni_c,',','|')) b5mcode_others_m_name_es
from b5mweb_nombres.solr_pkil_2d
--where url_2d in('T_A108003_0','T_A107998_3')
order by url_2d"

t_sql_05="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${t_gpk} a
left join ${t_gpk}_more_info b
on a.b5mcode = b.b5mcode"

t_sql_06="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${kp_gpk} a
left join ${kp_gpk}_more_info b
on a.kpcode = b.kpcode"

# ========================== #
#                            #
# 13. q_municipalcartography #
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
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 14. sg_geodeticbenchmarks #
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
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 15. em_megalithicsites #
#                        #
# ====================== #

em_sql_01="select
'EM_A'||idnombre b5mcode,
izena name_eu,
nombre name_es,
tipo_e type_eu,
tipo_c type_es,
tipo_c type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
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
# 16. gk_megaliths #
#                  #
# ================ #

gk_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
b.bopv official_gazette_link,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
'"$updd"' update_date,
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
# 17. cv_speleology #
#                   #
# ================= #

cv_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$url_cat_eu"'||replace(a.id_nombre1,'CE','') catalog_link_eu,
'"$url_cat_es"'||replace(a.id_nombre1,'CE','') catalog_link_es,
b.origen_e source_eu,
b.origen_c source_es,
b.origen_c source_en,
b.desnivel gradient_metres,
b.desarrollo growth_metres,
b.macizo mountain_range,
b.zona zone,
b.z altitude_metres,
decode(b.sima,null,0,1) chasm,
decode(b.cueva,null,0,1) cave,
decode(b.sumidero,null,0,1) drain,
decode(b.surgencia,null,0,1) spring,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.cuevas b
where a.id_nombre1=b.tag
order by a.id_nombre1"

cv_sql_02="select
distinct a.url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(a.codmunis,null,null,'M_'||replace(a.codmunis,',','|M_')) b5mcode_others_m,
replace(a.muni_e,',','|') b5mcode_others_m_name_eu,
replace(a.muni_c,',','|') b5mcode_others_m_name_es,
'"$s_gpk"|"${s_des[0]}"|"${s_des[1]}"|"${s_des[2]}"|"${s_abs[0]}"|"${s_abs[1]}"|"${s_abs[2]}"' b5mcode_others_s_type,
decode(b.idnomcomarca,null,null,'S_'||b.idnomcomarca) b5mcode_others_s,
c.nombre_e b5mcode_others_s_name_eu,
c.nombre_c b5mcode_others_s_name_es
from b5mweb_nombres.solr_gen_toponimia_2d a,(select distinct codmuni,idnomcomarca from b5mweb_25830.giputz) b,b5mweb_nombres.solr_gen_toponimia_2d c
where a.url_2d like 'CV_%'
and a.codmunis=b.codmuni(+)
and 'S_'||b.idnomcomarca=c.url_2d(+)
order by to_number(replace(a.url_2d,'CV_CE',''))"

cv_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${cv_gpk} a
left join ${cv_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# =============== #
#                 #
# 18. bi_biotopes #
#                 #
# =============== #

bi_sql_01="select
  a.url_2d as b5mcode,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  upper(substr(a.tipo_e,1,1))||lower(substr(a.tipo_e,2)) as type_eu,
  upper(substr(a.tipo_c,1,1))||lower(substr(a.tipo_c,2)) as type_es,
  initcap(a.tipo_i) as type_en,
  '"$updd"' as update_date,
  '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' as official,
  geom
from b5mweb_nombres.solr_gen_toponimia_2d a
join b5mweb_25830.bi_biotopos b on a.id_nombre1 = b.idnombre
where a.tipo_e = 'biotopoa'
order by to_number(a.id_nombre1)"

bi_sql_02="select
  a.url_2d as b5mcode,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  upper(substr(a.tipo_e,1,1))||lower(substr(a.tipo_e,2)) as type_eu,
  upper(substr(a.tipo_c,1,1))||lower(substr(a.tipo_c,2)) as type_es,
  initcap(a.tipo_i) as type_en,
  '"$updd"' as update_date,
  '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' as official,
  sdo_geom.sdo_centroid(b.geom, 0.005) as geom
from b5mweb_nombres.solr_gen_toponimia_2d a
join b5mweb_25830.bi_biotopos b on a.id_nombre1 = b.idnombre
where a.tipo_e = 'zuhaitz apartekoa'
order by to_number(a.id_nombre1)"

bi_sql_03="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'BI_%'
and tipo_e = 'biotopoa'
order by to_number(replace(url_2d,'BI_',''))"

bi_sql_04="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'BI_%'
and tipo_e = 'zuhaitz apartekoa'
order by to_number(replace(url_2d,'BI_',''))"

bi_sql_05="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${bi_gpk}_poly a
left join ${bi_gpk}_poly_more_info b
on a.b5mcode = b.b5mcode"

bi_sql_06="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${bi_gpk}_point a
left join ${bi_gpk}_point_more_info b
on a.b5mcode = b.b5mcode"

# ======================== #
#                          #
# 19. poi_pointsofinterest #
#                          #
# ======================== #

poi_sql_01="select
    'POI_' || a.id_actividad as b5mcode,
    a.cla_santi as id_type_poi,
    coalesce(a.nombre_comercial_e, a.nombre_comercial_c) as name_eu,
    a.nombre_comercial_c as name_es,
    e.name_eu as type_eu,
    e.name_es as type_es,
    e.name_en as type_en,
    e.title_eu as class_eu,
    e.title_es as class_es,
    e.title_en as class_en,
    e.description_eu as class_description_eu,
    e.description_es as class_description_es,
    e.description_en as class_description_en,
    i.url || '/' || g.icon as class_icon,
    d.title_eu as category_eu,
    d.title_es as category_es,
    d.title_en as category_en,
    d.description_eu as category_description_eu,
    d.description_es as category_description_es,
    d.description_en as category_description_en,
    i.url || '/' || h.icon as category_icon,
    'D_A' || a.id_postal as b5mcode_d,
    b.codmuni as codmuni,
    b.muni_e as muni_eu,
    b.muni_c as muni_es,
    b.codcalle as codstreet,
    b.calle_e as street_eu,
    b.calle_c as street_es,
    b.noportal as door_number,
    b.bis as bis,
    to_char(b.accesorio) as accessory,
    b.codpostal as postal_code,
    '"$updd"' update_date,
    '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
    c.point as geom
from b5mweb_nombres.n_actipuerta a
join b5mweb_nombres.n_dir_postal b on a.id_postal = b.idnombre
join b5mweb_25830.puertas c on a.id_puerta = c.id_puerta
join b5mweb_nombres.poi_classes e on a.cla_santi = e.code
join b5mweb_nombres.poi_cat_class f on e.id = f.poi_class_id
join b5mweb_nombres.poi_categories d on d.id = f.poi_category_id
join b5mweb_nombres.poi_icons g on e.icon_id = g.id
join b5mweb_nombres.poi_icons h on d.icon_id = h.id
join b5mweb_nombres.poi_icons_url i on i.id = 1
where a.id_postal <> 0
  and d.enabled = 1
  and a.cla_santi <> 'F.1.1'
union all
select b5mcode, id_type_poi, name_eu, name_es, type_eu, type_es, type_en, class_eu, class_es, class_en,
       class_description_eu, class_description_es, class_description_en,
       class_icon, category_eu, category_es, category_en,
       category_description_eu, category_description_es, category_description_en,
       category_icon, b5mcode_d, codmuni, muni_eu, muni_es,
       codstreet, street_eu, street_es, door_number, bis, accessory, postal_code, update_date, official, geom
from (
    select
        'POI_' || b.idnombre as b5mcode,
        f.code as id_type_poi,
        b.izena as name_eu,
        b.nombre as name_es,
        f.name_eu as type_eu,
        f.name_es as type_es,
        f.name_en as type_en,
        f.title_eu as class_eu,
        f.title_es as class_es,
        f.title_en as class_en,
        f.description_eu as class_description_eu,
        f.description_es as class_description_es,
        f.description_en as class_description_en,
        j.url || '/' || h.icon as class_icon,
        e.title_eu as category_eu,
        e.title_es as category_es,
        e.title_en as category_en,
        e.description_eu as category_description_eu,
        e.description_es as category_description_es,
        e.description_en as category_description_en,
        j.url || '/' || i.icon as category_icon,
        case
            when c.idpostal is null or c.idpostal = 0 then null
            else 'D_A' || c.idpostal
        end as b5mcode_d,
        c.codmuni as codmuni,
        d.nombre_e as muni_eu,
        d.nombre_c as muni_es,
        c.codcalle as codstreet,
        c.calle as street_eu,
        c.calle as street_es,
        c.noportal as door_number,
        c.bis as bis,
        c.acc as accessory,
        c.cp as postal_code,
        '"$updd"' update_date,
        '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
        a.point as geom,
        row_number() over (partition by
            b.idnombre, f.code, b.izena, b.nombre,
            f.title_eu, f.title_es, f.title_en,
            f.description_eu, f.description_es, f.description_en,
            j.url, h.icon,
            e.title_eu, e.title_es, e.title_en,
            e.description_eu, e.description_es, e.description_en,
            i.icon, c.idpostal, c.codmuni,
            d.nombre_e, d.nombre_c, c.codcalle,
            c.calle, c.noportal, c.bis, c.acc, c.cp
        order by b.idnombre) as rn
    from b5mweb_25830.monu1p a
    join b5mweb_25830.monu1 b on a.idut = b.idut
    left join b5mweb_nombres.n_edifacti2 c
        on c.idut = b.idut
        and c.cla_santi = 'F.1.1'
    left join b5mweb_nombres.solr_gen_toponimia_2d d
        on c.codmuni = d.id_nombre1
        and d.tabla = 'n_municipios'
    join b5mweb_nombres.poi_classes f
        on f.code = 'F.1.1'
    join b5mweb_nombres.poi_cat_class g
        on f.id = g.poi_class_id
    join b5mweb_nombres.poi_categories e
        on e.id = g.poi_category_id
    join b5mweb_nombres.poi_icons h
        on f.icon_id = h.id
    join b5mweb_nombres.poi_icons i
        on e.icon_id = i.id
    join b5mweb_nombres.poi_icons_url j
        on j.id = 1
)
where rn = 1
union all
select
      'POI_' || a.idnombre as b5mcode,
      f.code as id_type_poi,
      a.izena as name_eu,
      a.nombre as name_es,
      f.name_eu as type_eu,
      f.name_es as type_es,
      f.name_en as type_en,
      f.title_eu as class_eu,
      f.title_es as class_es,
      f.title_en as class_en,
      f.description_eu as class_description_eu,
      f.description_es as class_description_es,
      f.description_en as class_description_en,
      j.url || '/' || h.icon as class_icon,
      e.title_eu as category_eu,
      e.title_es as category_es,
      e.title_en as category_en,
      e.description_eu as category_description_eu,
      e.description_es as category_description_es,
      e.description_en as category_description_en,
      j.url || '/' || i.icon as category_icon,
      case
          when c.idpostal is null or c.idpostal = 0 then null
          else 'D_A' || c.idpostal
      end as b5mcode_d,
      c.codmuni as codmuni,
      d.nombre_e as muni_eu,
      d.nombre_c as muni_es,
      c.codcalle as codstreet,
      c.calle as street_eu,
      c.calle as street_es,
      c.noportal as door_number,
      c.bis as bis,
      c.acc as accessory,
      c.cp as postal_code,
      '"$updd"' update_date,
      '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
      a.geom as geom
  from b5mweb_25830.monu3 a
  left join b5mweb_nombres.n_edifacti2 c
      on c.idut = a.idut
      and c.cla_santi = 'F.1.1'
  left join b5mweb_nombres.solr_gen_toponimia_2d d
      on c.codmuni = d.id_nombre1
      and d.tabla = 'n_municipios'
  join b5mweb_nombres.poi_classes f
      on f.code = 'F.1.1'
  join b5mweb_nombres.poi_cat_class g
      on f.id = g.poi_class_id
  join b5mweb_nombres.poi_categories e
      on e.id = g.poi_category_id
  join b5mweb_nombres.poi_icons h
      on f.icon_id = h.id
  join b5mweb_nombres.poi_icons i
      on e.icon_id = i.id
  join b5mweb_nombres.poi_icons_url j
      on j.id = 1
union all
select
      'POI_' || a.idnombre as b5mcode,
      f.code as id_type_poi,
      a.izena as name_eu,
      a.nombre as name_es,
      f.name_eu as type_eu,
      f.name_es as type_es,
      f.name_en as type_en,
      f.title_eu as class_eu,
      f.title_es as class_es,
      f.title_en as class_en,
      f.description_eu as class_description_eu,
      f.description_es as class_description_es,
      f.description_en as class_description_en,
      j.url || '/' || h.icon as class_icon,
      e.title_eu as category_eu,
      e.title_es as category_es,
      e.title_en as category_en,
      e.description_eu as category_description_eu,
      e.description_es as category_description_es,
      e.description_en as category_description_en,
      j.url || '/' || i.icon as category_icon,
      case
          when c.idpostal is null or c.idpostal = 0 then null
          else 'D_A' || c.idpostal
      end as b5mcode_d,
      c.codmuni as codmuni,
      d.nombre_e as muni_eu,
      d.nombre_c as muni_es,
      c.codcalle as codstreet,
      c.calle as street_eu,
      c.calle as street_es,
      c.noportal as door_number,
      c.bis as bis,
      c.acc as accessory,
      c.cp as postal_code,
      '"$updd"' update_date,
      '{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
      a.point as geom
  from b5mweb_25830.monu5 a
  left join b5mweb_nombres.n_edifacti2 c
      on c.idut = a.idut
      and c.cla_santi = 'F.1.1'
  left join b5mweb_nombres.solr_gen_toponimia_2d d
      on c.codmuni = d.id_nombre1
      and d.tabla = 'n_municipios'
  join b5mweb_nombres.poi_classes f
      on f.code = 'F.1.1'
  join b5mweb_nombres.poi_cat_class g
      on f.id = g.poi_class_id
  join b5mweb_nombres.poi_categories e
      on e.id = g.poi_category_id
  join b5mweb_nombres.poi_icons h
      on f.icon_id = h.id
  join b5mweb_nombres.poi_icons i
      on e.icon_id = i.id
  join b5mweb_nombres.poi_icons_url j
      on j.id = 1"

poi_sql_02="select
distinct 'D_A'||a.idnombre b5mcode_d,
'"$k_gpk"|"${k_des[0]}"|"${k_des[1]}"|"${k_des[2]}"|"${k_abs[0]}"|"${k_abs[1]}"|"${k_abs[2]}"' b5mcode_others_k_type,
'K_'||a.codmuni||'_'||substr(a.codcalle,2) b5mcode_others_k,
a.calle_e b5mcode_others_k_name_eu,
decode(regexp_replace(a.calle_c,'[^,]+'),',',upper(substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),1,1))||''||substr(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' '),2,length(ltrim(regexp_substr(a.calle_c,'[^,]+',1,2),' ')))||' '||regexp_substr(a.calle_c,'[^,]+',1,1),a.calle_c) b5mcode_others_k_name_es,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
'M_'||a.codmuni b5mcode_others_m,
a.muni_e b5mcode_others_m_name_eu,
a.muni_c b5mcode_others_m_name_es,
'"$s_gpk"|"${s_des[0]}"|"${s_des[1]}"|"${s_des[2]}"|"${s_abs[0]}"|"${s_abs[1]}"|"${s_abs[2]}"' b5mcode_others_s_type,
'S_'||f.idnomcomarca b5mcode_others_s,
g.nombre_e b5mcode_others_s_name_eu,
g.nombre_c b5mcode_others_s_name_es
from b5mweb_nombres.n_edifdirpos a,b5mweb_nombres.n_actipuerta b,b5mweb_nombres.poi_classes c,b5mweb_nombres.poi_categories d,b5mweb_nombres.poi_cat_class e,b5mweb_25830.giputz f,b5mweb_nombres.solr_gen_toponimia_2d g
where a.idnombre=b.id_postal
and b.cla_santi=c.code
and c.id=e.poi_class_id
and d.id=e.poi_category_id
and a.codmuni=f.codmuni
and g.url_2d='S_'||f.idnomcomarca
and d.enabled=1"

poi_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${poi_gpk} a
left join ${poi_gpk}_more_info b
on a.b5mcode_d = b.b5mcode"

# ============================= #
#                               #
# 20. dm_distancemunicipalities #
#                               #
# ============================= #

dm_sql_01="select
'DM_'||a.codmuni||'_'||b.codmuni b5mcode,
a.muni_eu muni1_eu,
a.muni_es muni1_es,
decode(a.muni_fr,null,a.muni_eu,a.muni_fr) muni1_fr,
a.ter_eu term1_eu,
a.ter_es term1_es,
decode(a.ter_fr,null,a.ter_eu,a.ter_fr) term1_fr,
b.muni_eu muni2_eu,
b.muni_es muni2_es,
decode(b.muni_fr,null,b.muni_eu,b.muni_fr) muni2_fr,
b.ter_eu term2_eu,
b.ter_es term2_es,
decode(b.ter_fr,null,b.ter_eu,b.ter_fr) term2_fr,
c.dist distance_km,
c.fecha dm_date,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
c.geom
from mapas_otros.dist_ayunta3_muni a,mapas_otros.dist_ayunta3_muni b,b5mweb_25830.gi_wfs_dm c
where a.codmuni=c.codmuni1
and b.codmuni=c.codmuni2"

# ========== #
#            #
# 21. r_grid #
#            #
# ========== #

r_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec1 b
where a.nombre_e=b.tag
and a.tipo_e='1x1 km'
and a.url_2d like 'R_%'
union all
select
substr(a.url_2d,1,4)||lower(substr(a.url_2d,5,1)) b5mcode,
substr(a.nombre_e,1,2)||lower(substr(a.nombre_e,3,1)) name_eu,
substr(a.nombre_c,1,2)||lower(substr(a.nombre_c,3,1)) name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec2 b
where a.nombre_e=b.tag
and a.tipo_e='2x2 km'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec5 b
where a.nombre_e=b.tag
and a.tipo_e='5x5 km'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec b
where a.nombre_e=b.tag
and a.tipo_e='10x10 km'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.pauta5 b
where a.nombre_e=b.tag
and a.tipo_e='1:5000'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.pauta10 b
where a.nombre_e=b.tag
and a.tipo_e='1:10000'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.pauta25 b
where a.nombre_e=b.tag
and a.tipo_e='1:25000'
and a.url_2d like 'R_%'
union all
select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.pauta50 b
where a.nombre_e=b.tag
and a.tipo_e='1:50000'
and a.url_2d like 'R_%'"

# =============== #
#                 #
# 22. dw_download #
#                 #
# =============== #

dw_sql_01_01="select
replace(a.url_2d,'R_','DW_') b5mcode,
a.nombre_e name_grid_eu,
a.nombre_c name_grid_es,
a.tipo_e type_grid_eu,
a.tipo_c type_grid_es,
a.tipo_i type_grid_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec1 b
where a.nombre_e=b.tag
and a.tipo_e='1x1 km'
and a.url_2d like 'R_%'"

dw_sql_01_02="select
replace(a.url_2d,'R_','DW_') b5mcode,
a.nombre_e name_grid_eu,
a.nombre_c name_grid_es,
a.tipo_e type_grid_eu,
a.tipo_c type_grid_es,
a.tipo_i type_grid_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.gipurec5 b
where a.nombre_e=b.tag
and a.tipo_e='5x5 km'
and a.url_2d like 'R_%'"

dw_sql_01_03="select
'DW_'||substr(flight,6,length(flight)-5)||'_'||frame b5mcode,
substr(flight,6,length(flight)-5)||'_'||frame name_grid_eu,
substr(flight,6,length(flight)-5)||'_'||frame name_grid_es,
'argazkia' type_grid_eu,
'foto' type_grid_es,
'photo' type_grid_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
polygon geom
from b5mweb_25830.fotosaereas"

dw_sql_01_04="select
replace(a.url_2d,'R_','DW_') b5mcode,
a.nombre_e name_grid_eu,
a.nombre_c name_grid_es,
'1:5.000' type_grid_eu,
'1:5.000' type_grid_es,
'1:5,000' type_grid_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.pauta5 b
where a.nombre_e=b.tag
and a.tipo_e='1:5000'
and a.url_2d like 'R_%'"

dw_sql_01_05="select id_type dw_type_id,
name_eu dw_name_eu,
name_es dw_name_es,
name_en dw_name_en,
decode(grid_dw,'photo',0,1) dw_grid
from b5mweb_nombres.dw_types
where active=1
order by id_type"

dw_sql_02="select
a.id_dw,
b.id_type,
b.order_dw,
b.code_dw,
b.grid_dw,
a.year,
decode(instr(listagg(d.format_dir,';') within group (order by d.format_dir),'year'),0,a.path_dw,replace(replace(listagg(a.path_dw||'/'||d.format_dir,';') within group (order by d.format_dir),'year2',substr(a.year,3,2)),'year',a.year||a.subcode)) path_dw,
listagg(d.template_dir,';') within group (order by d.id_format_dir) template_dw,
replace(replace(listagg(d.format_dir,';') within group (order by d.format_dir),'year2',substr(a.year,3,2)),'year',a.year) url_dw,
listagg(c.format_dw,';') within group (order by c.format_dw) format_dw,
listagg(d.format_code,';') within group (order by c.format_dw) format_code,
e.file_type_dw,
a.url_metadata_eu,
a.url_metadata_es,
a.url_metadata_en,
a.owner_eu,
a.owner_es,
a.owner_en,
a.subcode
from b5mweb_nombres.dw_list a,b5mweb_nombres.dw_types b,b5mweb_nombres.dw_formats c,b5mweb_nombres.dw_formats_dir d,b5mweb_nombres.dw_file_types e,b5mweb_nombres.dw_rel_formats f
where a.id_type=b.id_type
and a.id_file_type=e.id_file_type
and a.id_dw=f.id_dw
and c.id_format=d.id_format
and d.id_format_dir=f.id_format_dir
and a.active=1
group by a.id_dw,b.id_type,b.order_dw,b.code_dw,b.grid_dw,b.name_eu,b.name_es,b.name_en,a.year,a.path_dw,e.file_type_dw,a.url_metadata_eu,a.url_metadata_es,a.url_metadata_en,a.owner_eu,a.owner_es,a.owner_en,a.subcode
order by b.grid_dw desc,b.order_dw,a.year desc,b.code_dw desc,a.subcode nulls first"

dw_sql_03="drop table ${ora_sch_01}.${dw_fs};
create table ${ora_sch_01}.${dw_fs}(
id_fs number primary key,
id_dw number,
id_type number,
name_grid varchar2(64),
format_dw varchar2(16),
size_by number
)"

dw_sql_04="select column_name
from all_tab_columns
where lower(table_name)='${dw_fs}'
order by column_id"

dw_sql_05="create index ${dw_fs}_1_idx
on ${ora_sch_01}.${dw_fs}(id_dw);
create index ${dw_fs}_2_idx
on ${ora_sch_01}.${dw_fs}(name_grid);
create index ${dw_fs}_3_idx
on ${ora_sch_01}.${dw_fs}(format_dw)"

dw_sql_06="select
unique grid_dw
from b5mweb_nombres.dw_types
order by nlssort(grid_dw,'nls_sort=binary_ai')"

dw_sql_07="select
'DW_' || a.name_grid name_grid,
b.order_dw,
b.name_eu,
b.name_es,
b.name_en,
c.year,
decode(b.grid_dw,'photo','DW_'||a.name_grid||'_photo',decode(c.subcode,null,'DW_'||a.name_grid||'_'||b.code_dw||'_'||c.year,'DW_'||a.name_grid||'_'||b.code_dw||'_'||c.year||'_'||c.subcode)) b5mcode_dw,
a.format_dw,
decode(b.grid_dw,'photo',replace(replace(replace(replace('https://b5m.gipuzkoa.eus/'||e.format_dir2||e.format_dir||c.subcode||'/'||decode(b.grid_dw,'photo',replace(a.name_grid,c.year||c.subcode||'_',''),a.name_grid)||e.template_dir,'*',''),a.name_grid,e.format_file1||a.name_grid||e.format_file2),'year2',substr(c.year,3,2)),'year',c.year),replace(replace(replace(replace('https://b5m.gipuzkoa.eus/'||e.format_dir2||e.format_dir||'/'||decode(b.grid_dw,'photo',replace(a.name_grid,c.year||c.subcode||'_',''),a.name_grid)||e.template_dir,'*',''),a.name_grid,e.format_file1||a.name_grid||e.format_file2),'year2',substr(c.year,3,2)),'year',c.year)) url_dw,
g.file_type_dw,
a.size_by file_size,
decode(c.owner_eu,'Gipuzkoako Foru Aldundia',c.url_metadata_eu||'.'||decode(b.grid_dw,'photo',replace(a.name_grid,c.year||c.subcode||'_',''),a.name_grid),c.url_metadata_eu) url_metadata_eu,
decode(c.owner_eu,'Gipuzkoako Foru Aldundia',c.url_metadata_es||'.'||decode(b.grid_dw,'photo',replace(a.name_grid,c.year||c.subcode||'_',''),a.name_grid),c.url_metadata_es) url_metadata_es,
decode(c.owner_eu,'Gipuzkoako Foru Aldundia',c.url_metadata_en||'.'||decode(b.grid_dw,'photo',replace(a.name_grid,c.year||c.subcode||'_',''),a.name_grid),c.url_metadata_en) url_metadata_en,
c.owner_eu,
c.owner_es,
c.owner_en,
b.id_type,
h.code_mt lidar_model_type_code,
h.model_type_eu lidar_model_type_eu,
h.model_type_es lidar_model_type_es,
h.model_type_en lidar_model_type_en,
h.url_ref_eu lidar_model_type_url_ref_eu,
h.url_ref_es lidar_model_type_url_ref_es,
h.url_ref_en lidar_model_type_url_ref_en,
i.code_ht lidar_height_type_code,
i.height_type_eu lidar_height_type_eu,
i.height_type_es lidar_height_type_es,
i.height_type_en lidar_height_type_en,
i.url_ref1_eu lidar_height_type_url_ref1_eu,
i.url_ref1_es lidar_height_type_url_ref1_es,
i.url_ref1_en lidar_height_type_url_ref1_en,
i.url_ref2_eu lidar_height_type_url_ref2_eu,
i.url_ref2_es lidar_height_type_url_ref2_es,
i.url_ref2_en lidar_height_type_url_ref2_en,
j.code_dp lidar_data_processing_code,
j.data_processing_eu lidar_data_processing_eu,
j.data_processing_es lidar_data_processing_es,
j.data_processing_en lidar_data_processing_en,
k.url_geocassini url_geocassini_eu,
k.url_geocassini url_geocassini_es,
k.url_geocassini url_geocassini_en,
l.description_eu geocassini_description_eu,
l.description_es geocassini_description_es,
l.description_en geocassini_description_en,
l.url_doc_eu geocassini_documentation_eu,
l.url_doc_es  geocassini_documentation_es,
l.url_doc_en  geocassini_documentation_en
from b5mweb_nombres.dw_file_sizes a,b5mweb_nombres.dw_types b,b5mweb_nombres.dw_list c,b5mweb_nombres.dw_formats d,b5mweb_nombres.dw_formats_dir e,b5mweb_nombres.dw_rel_formats f,b5mweb_nombres.dw_file_types g,b5mweb_nombres.dw_lidar_model_type h,b5mweb_nombres.dw_lidar_height_type i,b5mweb_nombres.dw_lidar_data_processing j,b5mweb_nombres.dw_geocassini k,b5mweb_nombres.geocassini_doc l
where a.id_dw=c.id_dw
and b.id_type=c.id_type
and a.id_dw=f.id_dw
and e.id_format_dir=f.id_format_dir
and d.id_format=e.id_format
and c.id_file_type=g.id_file_type
and a.format_dw=d.format_dw
and c.id_lidar_mt=h.id_lidar_mt(+)
and c.id_lidar_ht=i.id_lidar_ht(+)
and c.id_lidar_dp=j.id_lidar_dp(+)
and a.id_fs=k.id_fs(+)
and k.id_doc_geocassini=l.id_doc_geocassini(+)
and c.active=1
and b.grid_dw='ZZ_GRID_DW'
order by
  a.name_grid,
  b.order_dw,
  c.year desc,
  regexp_substr(c.subcode, '^[^_]+') nulls first,
    case
        when regexp_substr(c.subcode, '_([^_]+)', 1, 1) = '_RedNAP08' then 0
        else 1
    end,
    regexp_substr(c.subcode, '[^_]+$', 1, 1),
  a.format_dw"

dw_sql_08="select
a.${dw_id_fs},
c.viewer url_geocassini,
1 id_doc_geocassini
from b5mweb_nombres.dw_file_sizes a
join b5mweb_nombres.dw_list b on a.id_dw = b.id_dw
join b5mweb_nombres.geocassini c on a.name_grid = substr(c.name, 1, 4)
and b.year = substr(c.parent, -4)
and c.name like '%' || b.subcode || '%'
where b.subcode like '%RedNAP08%'
order by id_fs"

# =========================== #
#                             #
# 23. ac_municipal_boundaries #
#                             #
# =========================== #

ac_sql_01="select
'AC_'||a.idut b5mcode,
'${ac_des[0]}' type_eu,
'${ac_des[1]}' type_es,
'${ac_des[2]}' type_en,
a.linea_e name_eu,
a.linea_c name_es,
to_char(a.f_validacion,'YYYY-MM-DD') validation_date,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.polyline geom
from b5mweb_nombres.a_v_actas a,b5mweb_25830.gipu_l b
where a.idut=substr(b.tag,1,6)
and length(b.tag)<=13
order by a.idut"

# ================ #
#                  #
# 24. mg_landmarks #
#                  #
# ================ #

mg_sql_01="select
'MG_'||a.id_mojon b5mcode,
'${mg_des[0]}' type_eu,
'${mg_des[1]}' type_es,
'${mg_des[2]}' type_en,
a.localizacion name_eu,
a.localizacion name_es,
a.observacion_e comment_eu,
a.observacion_c comment_es,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.point geom
from b5mweb_nombres.a_mojon a,b5mweb_25830.muga b
where a.id_mojon=b.idut
order by b.idut"

mg_sql_02="select
'MG_'||a.id_mojon b5mcode,
'"$ac_gpk"|"${ac_des[0]}"|"${ac_des[1]}"|"${ac_des[2]}"|"${ac_abs[0]}"|"${ac_abs[1]}"|"${ac_abs[2]}"' b5mcode_others_ac_type,
rtrim(xmlagg(xmlelement(e,'AC_'||b.idut,'|').extract('//text()') order by b.linea_e).getclobval(),'|') b5mcode_others_ac,
rtrim(xmlagg(xmlelement(e,b.linea_e,'|').extract('//text()') order by b.linea_e).getclobval(),'|') b5mcode_others_ac_name_eu,
rtrim(xmlagg(xmlelement(e,b.linea_c,'|').extract('//text()') order by b.linea_e).getclobval(),'|') b5mcode_others_ac_name_es
from b5mweb_nombres.a_mojon a,b5mweb_nombres.a_v_actas b,b5mweb_nombres.a_mojacta c
where a.id_mojon=c.id_mojon
and b.id_acta=c.id_acta
group by (a.id_mojon)
order by a.id_mojon"

mg_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${mg_gpk} a
left join ${mg_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# =============================== #
#                                 #
# 25. mu_public_utility_woodlands #
#                                 #
# =============================== #

mu_sql_01="select
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
upper(substr(a.tipo_e,1,1))||lower(substr(a.tipo_e,2)) type_eu,
upper(substr(a.tipo_c,1,1))||lower(substr(a.tipo_c,2)) type_es,
initcap(a.tipo_i) type_en,
'"$updd"' update_date,
'{\"official_id\":\"1\",\"official_text_eu\":\"${oft1eu}\",\"official_text_es\":\"${oft1es}\",\"official_text_en\":\"${oft1en}\"}' official,
b.geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.mu_mup b
where a.id_nombre1=b.tag
order by a.id_nombre1"

mu_sql_02="select
distinct url_2d b5mcode,
'"$m_gpk"|"${m_des[0]}"|"${m_des[1]}"|"${m_des[2]}"|"${m_abs[0]}"|"${m_abs[1]}"|"${m_abs[2]}"' b5mcode_others_m_type,
decode(codmunis,null,null,'M_'||replace(codmunis,',','|M_')) b5mcode_others_m,
replace(muni_e,',','|') b5mcode_others_m_name_eu,
replace(muni_c,',','|') b5mcode_others_m_name_es
from b5mweb_nombres.solr_gen_toponimia_2d
where url_2d like 'MU_%'
order by to_number(replace(url_2d,'MU_',''))"

mu_sql_03="select
a.*,
b.more_info_eu,
b.more_info_es,
b.more_info_en
from ${mu_gpk} a
left join ${mu_gpk}_more_info b
on a.b5mcode = b.b5mcode"

# ======= #
#         #
# 99. end #
#         #
# ======= #
