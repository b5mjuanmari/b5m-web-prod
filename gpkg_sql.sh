#!/bin/bash
#
# gpkg_sql.sh
#
# Sentencias SQL para la generación de geopakages
#

declare -A des_a
declare -A sql_a
declare -A idx_a
declare -A or1_a
declare -A or2_a

# 1. m_municipalities (municipios) (carga: 19")
des_a["m_municipalities"]="Udalerriak / Municipios / Municipalities"
sql_a["m_municipalities"]="select
a.url_2d b5mcode,
b.codmuni codmuni,
a.nombre_e name_eu,
a.nombre_c name_es,
decode(b.idnomcomarca,null,null,'S_'||b.idnomcomarca) b5mcode_region,
d.nombre_e region_eu,
d.nombre_c region_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b,b5mweb_nombres.n_municipios c,b5mweb_nombres.solr_gen_toponimia_2d d
where a.url_2d='M_'||b.codmuni
and b.codmuni=c.codmuni
and to_char(b.idnomcomarca)=d.id_nombre1(+)
group by (a.url_2d,b.codmuni,a.nombre_e,a.nombre_c,b.idnomcomarca,d.nombre_e,d.nombre_c,a.tipo_e,a.tipo_c,a.tipo_i)"
idx_a["m_municipalities"]="b5mcode"

# 2. s_regions (comarcas) (carga: 36")
des_a["s_regions"]="Eskualdeak / Comarcas / Regions"
sql_a["s_regions"]="select
a.url_2d b5mcode,
b.idnomcomarca b5mcode_region,
a.nombre_e region_eu,
a.nombre_c region_es,
a.tipo_e type_eu,
a.tipo_c type_es,
'region' type_en,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.giputz b
where a.url_2d='S_'||b.idnomcomarca
group by (a.url_2d,b.idnomcomarca,a.nombre_e,a.nombre_c,a.tipo_e,a.tipo_c)"
idx_a["s_regions"]="b5mcode"

# 3. d_postaladdresses (direcciones postales) (carga: 4')
des_a["d_postaladdresses"]="Posta helbideak / Direcciones postales / Postal Addresses"
or1_a["d_postaladdresses"]="drop table gpkg_$$_d_tmp;
create table gpkg_$$_d_tmp as
select
idnombre,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idnombre idnombre,
decode(e.idnombre,null,null,'Z_A'||e.idnombre) b5mcodes_district,
e.nom_e districts_eu,
e.nom_c districts_es
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.a_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.barrioind d,b5mweb_nombres.b_barrios e
where a.idnombre=c.idpostal
and c.idut=b.idut
and d.idut=e.idut
and sdo_relate(b.polygon,d.polygon,'mask=ANYINTERACT')='TRUE'
and e.tipout_e='auzoa1'
group by (a.idnombre,e.idnombre,e.nom_e,e.nom_c)
order by a.idnombre)
group by(idnombre)
union
select
idnombre,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idnombre idnombre,
decode(e.idnombre,null,null,'Z_A'||e.idnombre) b5mcodes_district,
e.nom_e districts_eu,
e.nom_c districts_es
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.o_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.barrioind d,b5mweb_nombres.b_barrios e
where a.idnombre=c.idpostal
and c.idut=b.idut
and d.idut=e.idut
and sdo_relate(b.polygon,d.polygon,'mask=ANYINTERACT')='TRUE'
and e.tipout_e='auzoa1'
and a.idnombre not in (
select z.idpostal
from b5mweb_25830.a_edifind y,b5mweb_nombres.n_rel_area_dirpos z
where y.idut=z.idut
)
group by (a.idnombre,e.idnombre,e.nom_e,e.nom_c)
order by a.idnombre)
group by(idnombre)
union
select
idnombre,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idnombre idnombre,
decode(e.idnombre,null,null,'Z_A'||e.idnombre) b5mcodes_district,
e.nom_e districts_eu,
e.nom_c districts_es
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.s_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.barrioind d,b5mweb_nombres.b_barrios e
where a.idnombre=c.idpostal
and c.idut=b.idut
and d.idut=e.idut
and sdo_relate(b.polygon,d.polygon,'mask=ANYINTERACT')='TRUE'
and e.tipout_e='auzoa1'
and a.idnombre not in (
select z.idpostal
from b5mweb_25830.a_edifind y,b5mweb_nombres.n_rel_area_dirpos z
where y.idut=z.idut
)
group by (a.idnombre,e.idnombre,e.nom_e,e.nom_c)
order by a.idnombre)
group by(idnombre);
alter table gpkg_$$_d_tmp
add constraint gpkg_$$_d_tmp_pk primary key(idnombre);"
sql_a["d_postaladdresses"]="select
a.idnombre idname,
'D_A'||a.idnombre b5mcode,
a.codmuni codmuni,
a.municipio_e muni_eu,
a.municipio_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.cp,' ',null,to_number(a.cp)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
d.b5mcodes_district,
d.districts_eu,
d.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.a_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.gpkg_$$_d_tmp d
where a.idnombre=c.idpostal
and c.idut=b.idut
and a.idnombre=d.idnombre(+)
group by (a.idnombre,a.idnombre,a.codmuni,a.municipio_e,a.municipio_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.cp,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,d.b5mcodes_district,d.districts_eu,d.districts_es)
union all
select
a.idnombre idname,
'D_A'||a.idnombre b5mcode,
a.codmuni codmuni,
a.municipio_e muni_eu,
a.municipio_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.cp,' ',null,to_number(a.cp)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
d.b5mcodes_district,
d.districts_eu,
d.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.o_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.gpkg_$$_d_tmp d
where a.idnombre=c.idpostal
and c.idut=b.idut
and a.idnombre=d.idnombre(+)
and a.idnombre not in (
select z.idpostal
from b5mweb_25830.a_edifind y,b5mweb_nombres.n_rel_area_dirpos z
where y.idut=z.idut
)
group by (a.idnombre,a.idnombre,a.codmuni,a.municipio_e,a.municipio_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.cp,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,d.b5mcodes_district,d.districts_eu,d.districts_es)
union all
select
a.idnombre idname,
'D_A'||a.idnombre b5mcode,
a.codmuni codmuni,
a.municipio_e muni_eu,
a.municipio_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.cp,' ',null,to_number(a.cp)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
d.b5mcodes_district,
d.districts_eu,
d.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.solr_edifdirpos_2d a,b5mweb_25830.s_edifind b,b5mweb_nombres.n_rel_area_dirpos c,b5mweb_25830.gpkg_$$_d_tmp d
where a.idnombre=c.idpostal
and c.idut=b.idut
and a.idnombre=d.idnombre(+)
and a.idnombre not in (
select z.idpostal
from b5mweb_25830.a_edifind y,b5mweb_nombres.n_rel_area_dirpos z
where y.idut=z.idut
)
group by (a.idnombre,a.idnombre,a.codmuni,a.municipio_e,a.municipio_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.cp,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,d.b5mcodes_district,d.districts_eu,d.districts_es)"
idx_a["d_postaladdresses"]="b5mcode"
or2_a["d_postaladdresses"]="drop table gpkg_$$_d_tmp;"

# 4. e_buildings (Edficios) (carga: 1'35")
des_a["e_buildings"]="Eraikinak / Edficios / Buildings"
or1_a["e_buildings"]="drop table gpkg_$$_e_tmp;
create table gpkg_$$_e_tmp as
select
idut,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idut idut,
decode(d.idnombre,null,null,'Z_A'||d.idnombre) b5mcodes_district,
d.nom_e districts_eu,
d.nom_c districts_es
from b5mweb_nombres.n_edifgen a,b5mweb_25830.a_edifind b,b5mweb_25830.barrioind c,b5mweb_nombres.b_barrios d
where a.idut=b.idut
and c.idut=d.idut
and sdo_relate(b.polygon,c.polygon,'mask=ANYINTERACT')='TRUE'
and d.tipout_e='auzoa1'
group by (a.idut,d.idnombre,d.nom_e,d.nom_c)
order by a.idut)
group by(idut)
union
select
idut,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idut idut,
decode(d.idnombre,null,null,'Z_A'||d.idnombre) b5mcodes_district,
d.nom_e districts_eu,
d.nom_c districts_es
from b5mweb_nombres.n_edifgen a,b5mweb_25830.o_edifind b,b5mweb_25830.barrioind c,b5mweb_nombres.b_barrios d
where a.idut=b.idut
and c.idut=d.idut
and sdo_relate(b.polygon,c.polygon,'mask=ANYINTERACT')='TRUE'
and d.tipout_e='auzoa1'
group by (a.idut,d.idnombre,d.nom_e,d.nom_c)
order by a.idut)
group by(idut)
union
select
idut,
listagg(b5mcodes_district,',') within group (order by districts_eu) b5mcodes_district,
listagg(districts_eu,',') within group (order by districts_eu) districts_eu,
listagg(districts_es,',') within group (order by districts_es) districts_es
from (
select
a.idut idut,
decode(d.idnombre,null,null,'Z_A'||d.idnombre) b5mcodes_district,
d.nom_e districts_eu,
d.nom_c districts_es
from b5mweb_nombres.n_edifgen a,b5mweb_25830.s_edifind b,b5mweb_25830.barrioind c,b5mweb_nombres.b_barrios d
where a.idut=b.idut
and c.idut=d.idut
and sdo_relate(b.polygon,c.polygon,'mask=ANYINTERACT')='TRUE'
and d.tipout_e='auzoa1'
group by (a.idut,d.idnombre,d.nom_e,d.nom_c)
order by a.idut)
group by(idut);
alter table gpkg_$$_e_tmp
add constraint gpkg_$$_e_tmp_pk primary key(idut);"
sql_a["e_buildings"]="select
a.idut idname,
'E_A'||a.idut b5mcode,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
c.b5mcodes_district,
c.districts_eu,
c.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.a_edifind b,b5mweb_25830.gpkg_$$_e_tmp c
where a.idut=b.idut
and a.idut=c.idut(+)
group by (a.idut,a.idut,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,c.b5mcodes_district,c.districts_eu,c.districts_es)
union all
select
a.idut idname,
'E_A'||a.idut b5mcode,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
c.b5mcodes_district,
c.districts_eu,
c.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.o_edifind b,b5mweb_25830.gpkg_$$_e_tmp c
where a.idut=b.idut
and a.idut=c.idut(+)
group by (a.idut,a.idut,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,c.b5mcodes_district,c.districts_eu,c.districts_es)
union all
select
a.idut idname,
'E_A'||a.idut b5mcode,
a.codmuni codmuni,
a.muni_e muni_eu,
a.muni_c muni_es,
a.codcalle codstreet,
a.calle_e street_eu,
a.calle_c street_es,
a.noportal door_number,
a.bis bis,
decode(a.codpostal,' ',null,to_number(a.codpostal)) postal_code,
a.distrito coddistr,
a.seccion codsec,
a.nomedif_e name_eu,
a.nomedif_e name_es,
c.b5mcodes_district,
c.districts_eu,
c.districts_es,
sdo_aggr_union(sdoaggrtype(b.polygon,0.005)) geom
from b5mweb_nombres.n_edifgen a,b5mweb_25830.s_edifind b,b5mweb_25830.gpkg_$$_e_tmp c
where a.idut=b.idut
and a.idut=c.idut(+)
group by (a.idut,a.idut,a.codmuni,a.muni_e,a.muni_c,a.codcalle,a.calle_e,a.calle_c,a.noportal,a.bis,a.codpostal,a.distrito,a.seccion,a.nomedif_e,a.nomedif_c,c.b5mcodes_district,c.districts_eu,c.districts_es)"
idx_a["e_buildings"]="b5mcode"
or2_a["e_buildings"]="drop table gpkg_$$_e_tmp;"

# 5. c_basins (cuencas) (carga: 17")
des_a["c_basins"]="Arroak / Cuencas / Basins"
sql_a["c_basins"]="select
a.url_2d b5mcode,
b.idnombre b5mcode_basin,
a.nombre_e basin_eu,
a.nombre_c basin_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
a.codmunis idmunis,
a.muni_e munis_eu,
a.muni_c munis_es,
b.polygon geom
from b5mweb_nombres.solr_gen_toponimia_2d a,b5mweb_25830.cuencap b
where a.url_2d='C_A'||b.idnombre"
idx_a["c_basins"]="b5mcode"

# 6. i_hydrography (hidrografía) (carga: 48")
des_a["i_hydrography"]="Hidrografia / Hidrografía / Hydrography"
sql_a["i_hydrography"]="select
a.id_topo idtopo,
a.id_nombre1 idname,
a.url_2d b5mcode,
a.nombre_e name_eu,
a.nombre_c name_es,
a.tipo_e type_eu,
a.tipo_c type_es,
a.tipo_i type_en,
'C_A'||b.idnomcuenca b5mcode_basin,
b.cuenca_e basinname_eu,
b.cuenca_c basinname_es,
a.codmunis idmunis,
a.muni_e munis_eu,
a.muni_c munis_es,
sdo_aggr_concat_lines(b.polyline) geom
from b5mweb_nombres.solr_gen_toponimia_2d a, b5mweb_25830.ibaiak b
where a.id_nombre1=to_char(b.idnombre)
group by(a.id_topo,a.id_nombre1,a.url_2d,a.nombre_e,a.nombre_c,b.idnomcuenca,b.cuenca_e,b.cuenca_c,a.tipo_e,a.tipo_c,a.tipo_i,a.codmunis,a.muni_e,a.muni_c)"
idx_a["i_hydrography"]="b5mcode"

# 7. sg_geodeticbenchmarks (señales geodésicas) (carga: 27")
sg_aju_eu="Doikuntza geodesikoa"
sg_sen_eu="Seinale geodesikoa"
sg_aju_es="Ajuste geodésico"
sg_sen_es="Señal geodésica"
sg_aju_en="Geodetic Adjustment"
sg_sen_en="Geodetic Benchmark"
sg_url="https://b5m.gipuzkoa.eus/geodesia/pdf"
des_a["sg_geodeticbenchmarks"]="Seinale geodesikoak / Señales geodésicas / Geodetic Benchmarks"
sql_a["sg_geodeticbenchmarks"]="select
a.pgeod_id idgeodb,
'SG_'||a.pgeod_id b5mcode,
a.nombre display_name,
decode(a.ajuste,1,'${sg_aju_eu}','${sg_sen_eu}') type_eu,
decode(a.ajuste,1,'${sg_aju_es}','${sg_sen_es}') type_es,
decode(a.ajuste,1,'${sg_aju_en}','${sg_sen_en}') type_en,
a.codmuni codmuni,
trim(regexp_substr(b.municipio,'[^/]+',1,1)) muni_eu,
decode(trim(regexp_substr(b.municipio,'[^/]+',1,2)),null,b.municipio,trim(regexp_substr(b.municipio,'[^/]+',1,2))) muni_es,
'${sg_url}/'||a.archivo link,
a.file_type,
a.size_kb,
a.geom
from o_mw_bta.puntogeodesicobta a,b5mweb_nombres.n_municipios b
where a.codmuni=b.codmuni
and a.visible_web=1
order by a.pgeod_id"
idx_a["sg_geodeticbenchmarks"]="b5mcode"

# 8. dm_distancemunicipalities (distancia entre municipios) (carga: 2h5')
des_a["dm_distancemunicipalities"]="Udalerrien arteko distantzia / Distancia entre municipios / Distance Between Municipalities"
sql_a["dm_distancemunicipalities"]="select
c.idut iddm,
'DM_'||a.codmuni||'_'||b.codmuni b5mcode,
a.codmuni codmuni1,
a.muni_eu muni1_eu,
a.muni_es muni1_es,
a.muni_fr muni1_fr,
decode(a.ter_eu,'Gipuzkoa','001','Araba','002','Bizkaia','003','Nafarroa','004','005') codterm1,
a.ter_eu term1_eu,
a.ter_es term1_es,
a.ter_fr term1_fr,
a.id_area id_area1,
b.codmuni codmuni2,
b.muni_eu muni2_eu,
b.muni_es muni2_es,
b.muni_fr muni2_fr,
decode(b.ter_eu,'Gipuzkoa','001','Araba','002','Bizkaia','003','Nafarroa','004','005') codterm2,
b.ter_eu term2_eu,
b.ter_es term2_es,
b.ter_fr term2_fr,
b.id_area id_area2,
c.dist_r,
c.dist_c,
c.fecha dm_date,
c.geom
from mapas_otros.dist_ayunta2_muni a,mapas_otros.dist_ayunta2_muni b,mapas_otros.dist_ayunta2 c
where a.codmuni=c.codmuni1
and b.codmuni=c.codmuni2"
idx_a["dm_distancemunicipalities"]="b5mcode"
tabdm='gi_dm_distancem'
tabDM="$(echo "$tabdm" | gawk '{print toupper($1)}')"
tabdm2="dist_ayunta2"
tabDM2="$(echo "$tabdm2" | gawk '{print toupper($1)}')"
sql_b["dm_distancemunicipalities"]="drop table ${tabdm};
delete from
user_sdo_geom_metadata
where lower(table_name)='${tabdm}'
and column_name='GEOM';
create table ${tabdm}(
iddm number,
b5mcode varchar2(12),
codmuni1 varchar2(4),
muni1_eu varchar2(100),
muni1_es varchar2(100),
muni1_fr varchar2(100),
codterm1 varchar2(3),
term1_eu varchar2(100),
term1_es varchar2(100),
term1_fr varchar2(100),
id_area1 number,
codmuni2 varchar2(4),
muni2_eu varchar2(100),
muni2_es varchar2(100),
muni2_fr varchar2(100),
codterm2 varchar2(3),
term2_eu varchar2(100),
term2_es varchar2(100),
term2_fr varchar2(100),
id_area2 number,
dist_r number,
dist_c number,
dm_date date,
geom sdo_geometry,
constraint ${tabdm}_pk primary key(iddm)
);
insert into user_sdo_geom_metadata
select '${tabDM}',column_name,diminfo,srid
from all_sdo_geom_metadata
where table_name='${tabDM2}'
and column_name='GEOM';
insert into ${tabdm}(iddm,b5mcode,codmuni1,muni1_eu,muni1_es,muni1_fr,codterm1,term1_eu,term1_es,term1_fr,id_area1,codmuni2,muni2_eu,muni2_es,muni2_fr,codterm2,term2_eu,term2_es,term2_fr,id_area2,dist_r,dist_c,dm_date,geom)
"
sql_c["dm_distancemunicipalities"]="
create unique index ${tabdm}_idx on ${tabdm}(b5mcode,codmuni1,muni1_eu,muni1_es,codmuni2,muni2_eu,muni2_es);
create index ${tabdm}2_idx on ${tabdm}(codterm1,term1_eu,term1_es,codterm2,term2_eu,term2_es);
create index ${tabdm}_gidx
on ${tabdm}(geom)
indextype is mdsys.spatial_index
parameters('layer_gtype=MULTILINE');"

# 9. q_municipalcartography (cartografía municipal) (carga: 24")
des_a["q_municipalcartography"]="Udal kartografiaren inbentarioa / Inventario de cartografía municipal / Municipal Cartography Inventory"
sql_a["q_municipalcartography"]="select
a.id_levan,
'Q_' || a.id_levan b5mcode,
b.codmuni,
trim(regexp_substr(c.municipio,'[^/]+',1,1)) muni_eu,
decode(trim(regexp_substr(c.municipio,'[^/]+',1,2)),null,c.municipio,trim(regexp_substr(c.municipio,'[^/]+',1,2))) muni_es,
replace(a.nombre,'&#34;','') nombre_eu,
replace(a.nombre,'&#34;','') nombre_es,
a.propietario propietario_eu,
a.propietario propietario_es,
a.escala escala,
to_char(a.f_digitalizacion,'YYYY-MM-DD') f_digitalizacion,
to_char(a.f_levanoriginal,'YYYY-MM-DD') f_levanoriginal,
to_char(a.f_ultactua,'YYYY-MM-DD') f_ultactua,
a.empresa empresa,
'https://b5m.gipuzkoa.eus/map-2022/eu/Q_' || a.id_levan map_link_eu,
'https://b5m.gipuzkoa.eus/map-2022/es/Q_' || a.id_levan map_link_es,
d.polygon geom
from b5mweb_nombres.g_levancarto a,b5mweb_nombres.g_rel_muni_levan b,b5mweb_nombres.n_municipios c,b5mweb_25830.cardigind d
where a.tag=b.tag
and b.codmuni=c.codmuni
and a.tag=d.tag"
idx_a["q_municipalcartography"]="b5mcode"
