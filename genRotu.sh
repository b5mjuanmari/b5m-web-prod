#!/bin/bash

# Genera los ficheros shp para la rotulación

# Variables
export LC_NUMERIC=C.UTF-8
usu="b5mweb_25830"
pas="web+"
bd="bdet"
t="GIPUTZ"
dir="/home/data/datos_explotacion/CUR/shape/EPSG_25830/Tiles"

o="$(pwd)"
prc="$(echo "$0" | gawk 'BEGIN{FS="/"}{split($NF,a,".");print a[1]}')"
gaur="$(date +'%Y%m%d')"
log="${o}/log/${prc}_${gaur}.log"
rm $log 2> /dev/null

# Shapes
hidro="${dir}/r_hidronimia"
oroni="${dir}/r_oronimia"
barri="${dir}/r_barrios"
carre="${dir}/r_carre"
munic="${dir}/r_municip"
parzo="${dir}/r_parzo"
alt25="${dir}/r_alti25"
alt05="${dir}/r_alti5"
cotas="${dir}/r_cotas"
calle="${dir}/r_calles"
edifn="${dir}/r_edifn"
edifp="${dir}/r_edifp"

hidro1=1
oroni1=1
barri1=1
carre1=1
munic1=1
munic2=1
parzo1=1
alt251=1
alt051=1
cotas1=1
calle1=1
edifn1=1
edifp1=1

# Hasiera
dh="$(date '+%Y-%m-%d %H:%M:%S')"
echo "$0: hasiera: $dh" >> $log

# Genera el shp de hidronimia
if [ $hidro1 -eq 1 ] ; then
echo "$0: $hidro - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${hidro}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${hidro}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,substr(a.nomrotular_c,1,1)||lower(substr(a.nomrotular_c,2,length(a.nomrotular_c)-1)) nombre_c,substr(a.nomrotular_e,1,1)||lower(substr(a.nomrotular_e,2,length(a.nomrotular_e)-1)) nombre_e,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,c.polyline geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,almacen_cache.tutrel@almacen_cache_lnk b,b5mweb_25830.ibai_plus c
where a.idut=b.idutpadre
and b.iduthijo= c.idut
and b.tiporelacion like 'composici%'
and a.tipo_e in('ibaia','erreka')
and c.oculto is null
and a.rotular_e <>0" 2> /dev/null
fi

# Genera el shp de oronimia
if [ $oroni1 -eq 1 ] ; then
echo "$0: $oroni - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${oroni}.* 2> /dev/null
# Creación de la tabla de oronimia, en donde nos aseguramos
# de que si hay registros con nombre oficiales y no oficiales
# nos quedamos solo con los oficiales
toro_tmp="$(echo "${oroni}_tmp" | gawk 'BEGIN{FS="/"}{print $NF}')"
sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set lin 4000
set trim on
set pages 0
set tab on
set spa 0
set serveroutput on

drop table ${toro_tmp};

create table $toro_tmp as
select a.*,b.polygon
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.montesind b
where a.idut=b.idut
and a.rotular_e<>0
and a.oficial=1;

insert into $toro_tmp
select a.*,b.polygon
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.montesind b
where a.idut=b.idut
and a.rotular_e<>0
and a.oficial=0
and a.idut not in (
select idut
from $toro_tmp
);

commit;

exit;
EOF

ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${oroni}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,a.nomrotular_c nombre_c,a.nomrotular_e nombre_e,a.rotular_c,a.rotular_e,a.oficial,a.tipo_c,a.tipo_e,a.tipo_ut,b.polygon geom
from b5mweb_25830.${toro_tmp} a,b5mweb_25830.montesind b
where a.idut=b.idut
and a.rotular_e<>0" 2> /dev/null

sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set lin 4000
set trim on
set pages 0
set tab on
set spa 0
set serveroutput on

drop table ${toro_tmp};

exit;
EOF
fi

# Genera el shp de barrios
# Nota: al seleccionar los nombre a rotular se quita Auzoa o auzoa
# (excepto Arrantzaleen auzoa [een auzoa])
if [ $barri1 -eq 1 ] ; then
echo "$0: $barri - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${barri}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${barri}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,replace(replace(replace(replace(a.nomrotular_c,' auzoa',''),' Auzoa',''),'een','een auzoa'),', ','') nombre_c,replace(replace(replace(replace(a.nomrotular_e,' auzoa',''),' Auzoa',''),'een','een auzoa'),', ','') nombre_e,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,b.polygon geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.barrioind b
where a.idut=b.idut
and a.rotular_e <>0" 2> /dev/null
fi

# Genera el shp de carreteras
if [ $carre1 -eq 1 ] ; then
echo "$0: $carre - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${carre}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${carre}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select b.idut,listagg(a.nomrotular_c,'/') within group (order by a.nomrotular_c) nombre_c,listagg(a.nomrotular_e,'/') within group (order by nomrotular_e) nombre_e,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut||'_'||d.color tipo_ut,sdo_aggr_union(sdoaggrtype(b.polyline,0.005)) geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.vialesind b,b5mweb_nombres.v_vialtramo c,b5mweb_nombres.vv_color d
where  a.idnombre_c=c.idnombre
and a.idnombre_c=d.codigo
and c.idut=b.idut
and c.puente_tunel='0'
and a.rotular_e<>0
and a.tipo_c in ('carretera')
group by b.idut,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,d.color" 2> /dev/null
fi

# Genera el shp de municipios
if [ $munic1 -eq 1 ] ; then
echo "$0: $munic - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${munic}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${munic}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select
a.idut,
a.nomrotular_c nombre_c,
a.nomrotular_e nombre_e,
decode(a.nomrotular_c,a.nomrotular_e,a.nomrotular_c,a.nomrotular_e||' / '||a.nomrotular_c) nombre_mul,
a.rotular_c,a.rotular_e,
a.tipo_c,a.tipo_e,
a.tipo_ut,
sdo_geom.sdo_centroid(c.polygon,m.diminfo) geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,almacen_cache.cla_nombres@almacen_cache_lnk b,b5mweb_25830.a_edifind c,b5mweb_nombres.n_edifgen d,all_sdo_geom_metadata m
where (b.idut=c.idut
and c.idut=d.idut
and d.codmuni=a.idnombre_c
and m.table_name='A_EDIFIND'
and m.column_name='POLYGON'
and m.owner='O_MW_25830'
and b.tipo_ut='edificio'
and b.nomrotular_e='Udaletxea'
and b.tipo_c='edificio'
and a.tipo_ut='municipio'
and d.nomedif_e='Udaletxea'
and d.idut<>61895
and a.idut<>240630
and d.idpostal not in(35078,35079,70634)
and a.rotular_e<>0)
or (b.idut=c.idut
and c.idut=d.idut
and m.table_name='A_EDIFIND'
and m.column_name='POLYGON'
and m.owner='O_MW_25830'
and b.tipo_ut='edificio'
and b.tipo_c='edificio'
and a.tipo_ut='municipio'
and d.idut=25570
and a.idnombre_c=144900
and b.idnombre_c=76933
and a.rotular_e<>0)" 2> /dev/null

# Nota:
# and d.id_area<>61895 \
# and a.idut<>240630 \
# es para quitar uno de los ayuntamientos de Pasaia
#
# Y, lo que esta despues del 'or' es para que salga
# el municipio de Itsaso, rotulado sobre el edificio Ostatua,
# como si fuera el ayuntamiento

fi

# Genera el shp de municipios para rotular los límites municipales
if [ $munic2 -eq 1 ] ; then
echo "$0: ${munic}_l - $(date '+%Y-%m-%d %H:%M:%S')" >> $log

# Primero se crea un LRS de Oracle Spatial con todas las líneas de límite.
# Para cada línea se consultan los municipios que están a cada lado.
# Para el primer municipio se salva la línea tal y como está con los atributos
# de ese municipio, y para el segundo se hace la inversa de la línea y luego
# se salva con los atributos del segundo municipio.
# El resultado final se exporta r_municip_l.shp.
# MapServer rotulará los nombres de los municipios a ambos lados de la
# línea de límite, con la opción "angle follow" más un offset para que
# el rótulo no quede encima de la línea. Los nombres salen correctamente
# a cada lado porque el sentido de las dos líneas que conforman un
# límite de rotulación es distinto para cada municipio

municc="$(echo "$munic" | gawk 'BEGIN{FS="/"}{print $NF}')"
t01="${municc}_l_tmp1"
t02="${municc}_l_tmp2"
t03="${municc}_l_tmp3"
t01u="$(echo "$t01" | gawk '{print toupper($0)}')"
t02u="$(echo "$t02" | gawk '{print toupper($0)}')"
t03u="$(echo "$t03" | gawk '{print toupper($0)}')"

# Creación de la tabla provisional de líneas de término
sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set lin 4000
set trim on
set pages 0
set tab on
set spa 0
set serveroutput on

drop table ${t01};
delete from user_sdo_geom_metadata
where lower(table_name)='${t01}';

create table $t01 (
tag number primary key,
polyline sdo_geometry);

insert into user_sdo_geom_metadata(table_name,column_name,diminfo,srid)
values(
'${t01u}',
'POLYLINE',
sdo_dim_array(
sdo_dim_element('X',530000,610000,0.001),
sdo_dim_element('Y',4740000,4820000,0.001)
),
25830);

declare
	i number:=1;
  v1 gipu_l.tag%type;
  v2 number;
  v3 number;
  v4 sdo_point_type;
  v5 sdo_elem_info_array;
  v6 sdo_ordinate_array;

  cursor c1 is
  select tag
  from b5mweb_25830.gipu_l;

  cursor c2 is
  select * from table(
  select sdo_util.extract_all(a.polyline)
  from b5mweb_25830.gipu_l a where a.tag=v1);
begin
  open c1;
  loop
    fetch c1 into v1;
    exit when c1%notfound;
    open c2;
    loop
      fetch c2 into v2,v3,v4,v5,v6;
      exit when c2%notfound;
			begin
				insert into $t01
				values (
				i,
				sdo_geometry(
				v2,
				v3,
				null,
				v5,
				v6)
				);
			end;
			i:=i+1;
    end loop;
    close c2;
  end loop;
  close c1;
end;
/

create index ${t01}_gidx
on ${t01}(polyline)
indextype is mdsys.spatial_index
parameters('layer_gtype=MULTILINE');

exit;
EOF

# Para saber la longitud del tramo más largo
l_lrs="$(sqlplus -s ${usu}/${pas}@${bd} <<-EOF | gawk '{print $1}'
set serveroutput on
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0

select max(sdo_geom.sdo_length(a.polyline,m.diminfo)) l
from $t01 a,user_sdo_geom_metadata m
where lower(m.table_name)='${t01}';

exit;
EOF)"

sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set lin 4000
set trim on
set pages 0
set tab on
set spa 0
set serveroutput on

drop table ${t02};
drop table ${t03};
delete from user_sdo_geom_metadata
where lower(table_name)='${t02}';
delete from user_sdo_geom_metadata
where lower(table_name)='${t03}';

create table $t02
as select a.tag,sdo_lrs.convert_to_lrs_geom(a.polyline,m.diminfo) geom
from $t01 a,user_sdo_geom_metadata m
where lower(m.table_name)='${t01}'
and lower(m.column_name)='polyline';

create table ${t03}(
id number primary key,
muni_eu varchar2(128),
muni_es varchar2(128),
muni_mul varchar2(128),
geom sdo_geometry);

insert into user_sdo_geom_metadata(table_name,column_name,diminfo,srid)
values(
'${t02u}',
'GEOM',
sdo_dim_array(
sdo_dim_element('X',530000,610000,0.001),
sdo_dim_element('Y',4740000,4820000,0.001),
sdo_dim_element('M',0,${l_lrs},0.001)
),
25830);

insert into user_sdo_geom_metadata(table_name,column_name,diminfo,srid)
values(
'${t03u}',
'GEOM',
sdo_dim_array(
sdo_dim_element('X',530000,610000,0.001),
sdo_dim_element('Y',4740000,4820000,0.001)
),
25830);

create index ${t03u}_gidx
on ${t03}(geom)
indextype is mdsys.spatial_index
parameters('layer_gtype=MULTILINE');

declare
  v1 ${t02}.tag%type;
  v2 number;
  v3 ${t02}.geom%type;
  v4a sdo_geometry;
  v4b sdo_geometry;
  v4c sdo_geometry;
  v5 number;
  v6 varchar2(128);
  v6eu varchar2(128);
  v6es varchar2(128);
  v6mul varchar2(128);
  v7 varchar2(128);
  v7eu varchar2(128);
  v7es varchar2(128);
  v7mul varchar2(128);
  v8 ${t01}.tag%type;
  v9 sdo_geometry;
  v9r sdo_geometry;
  i number:=1;

  cursor c1 is
  select a.tag,sdo_geom.sdo_length(a.geom,m.diminfo),a.geom
  from $t02 a,user_sdo_geom_metadata m
  where m.table_name='${t02u}'
  and m.column_name='GEOM';
begin
  open c1;
  loop
    fetch c1 into v1,v2,v3;
    exit when c1%notfound;
    v5:=v2/2;
    select sdo_lrs.locate_pt(v3,v5,1) into v4a
    from dual;
    select sdo_lrs.locate_pt(v3,v5,-1) into v4b
    from dual;
    select sdo_lrs.locate_pt(v3,v5,0) into v4c
    from dual;
    begin
      select b.municipio,trim(regexp_substr(b.municipio,'[^/]+',1,1)),trim(regexp_substr(b.municipio,'[^/]+',1,2)) into v6,v6eu,v6es
      from b5mweb_25830.giputz a,b5mweb_nombres.n_municipios b
      where a.codmuni=b.codmuni
      and sdo_relate(a.polygon,v4a,'MASK=(ANYINTERACT) QUERYTYPE=WINDOW')='TRUE';
    exception
      when others then
        v6:='';
        v6eu:='';
        v6es:='';
    end;
    if v6es is null then
      v6eu:=v6;
    end if;
    if v6es is null then
      v6es:=v6;
    end if;
    begin
      select b.municipio,trim(regexp_substr(b.municipio,'[^/]+',1,1)),trim(regexp_substr(b.municipio,'[^/]+',1,2)) into v7,v7eu,v7es
      from b5mweb_25830.giputz a,b5mweb_nombres.n_municipios b
      where a.codmuni=b.codmuni
      and sdo_relate(a.polygon,v4b,'MASK=(ANYINTERACT) QUERYTYPE=WINDOW')='TRUE';
    exception
      when others then
        v7:='';
        v7eu:='';
        v7es:='';
    end;
    if v7es is null then
      v7eu:=v7;
    end if;
    if v7es is null then
      v7es:=v7;
    end if;
    select tag,polyline into v8,v9
    from $t01
    where sdo_relate(polyline,v4c,'MASK=(ANYINTERACT) QUERYTYPE=WINDOW')='TRUE';
    select sdo_util.reverse_linestring(v9) into v9r from dual;

    if v6 is not null then
			if v6eu = v6es then
				v6mul := v6eu;
			else
				v6mul := v6eu || ' / ' || v6es;
			end if;
      execute immediate 'insert into $t03 values(:1,:2,:3,:4,:5)' using i,v6eu,v6es,v6mul,v9;
      i:=i+1;
    end if;

    if v7 is not null then
			if v7eu = v7es then
				v7mul := v7eu;
			else
				v7mul := v7eu || ' / ' || v7es;
			end if;
      execute immediate 'insert into $t03 values(:1,:2,:3,:4,:5)' using i,v7eu,v7es,v7mul,v9r;
      i:=i+1;
    end if;
  end loop;
  close c1;
end;
/

exit;
EOF

# Se genera el SHP
rm "${munic}_l."* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
"${munic}_l.shp" \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select * from ${t03}" 2> /dev/null

# Se borran las tablas temporales
sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set lin 4000
set trim on
set pages 0
set tab on
set spa 0
set serveroutput on

drop table ${t01};
drop table ${t02};
drop table ${t03};
delete from user_sdo_geom_metadata
where lower(table_name)='${t01}';
delete from user_sdo_geom_metadata
where lower(table_name)='${t02}';
delete from user_sdo_geom_metadata
where lower(table_name)='${t03}';

exit;
EOF

fi

# Genera el shp de parzonerías y mancomunidad de Enirio-Aralar
if [ $parzo1 -eq 1 ] ; then
echo "$0: $parzo - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${parzo}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${parzo}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,
a.nomrotular_c nombre_c,
a.nomrotular_e nombre_e,
decode(a.nomrotular_c,a.nomrotular_e,a.nomrotular_c,a.nomrotular_e||' / '||a.nomrotular_c) nombre_mul,
a.rotular_c,
a.rotular_e,
a.tipo_c,
a.tipo_e,
a.tipo_ut,
sdo_geom.sdo_centroid(b.polygon,m.diminfo) geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.giputz b,all_sdo_geom_metadata m
where a.idut=b.idut
and m.table_name='GIPUTZ'
and m.column_name='POLYGON'
and m.owner='B5MWEB_25830'
and (a.tipo_ut='mancomunidad'
or a.tipo_ut like 'parzoner%')
and a.rotular_e<>0" 2> /dev/null
fi

# Genera el shp de alti25
if [ $alt251 -eq 1 ] ; then
echo "$0: $alt25 - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${alt25}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${alt25}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select etiqueta,idut,replace(etiqueta,'.00','') nombre_c,replace(etiqueta,'.00','') nombre_e,'2' rotular_c,'2' rotular_e,'alti_5' tipo_c,'alti_5' tipo_e,'alti_5' tipo_ut,geom
from b5mweb_25830.alti_5_cortadas
where etiqueta like '%00.00'
or etiqueta like '%25.00'
or etiqueta like '%50.00'
or etiqueta like '%75.00'" 2> /dev/null
fi

# Genera el shp de alti5
if [ $alt051 -eq 1 ] ; then
echo "$0: $alt05 - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${alt05}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${alt05}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select idut,replace(etiqueta,'.00','') nombre_c,replace(etiqueta,'.00','') nombre_e,'2' rotular_c,'2' rotular_e,'alti_5' tipo_c,'alti_5' tipo_e,'alti_5' tipo_ut,geom
from b5mweb_25830.alti_5_cortadas" 2> /dev/null
fi

# Genera el shp de cotas
if [ $cotas1 -eq 1 ] ; then
echo "$0: $cotas - $(date '+%Y-%m-%d %H:%M:%S')" >> $log

tab01="cotas_tmp"
tmp01="/tmp/cotas.tmp"
dat01="/tmp/cotas.dat"
ctl01="/tmp/cotas.ctl"
bad01="/tmp/cotas.bad"
log01="/tmp/cotas.log"
rm $tmp01 2> /dev/null
sqlplus -s ${usu}/${pas}@${bd} <<-EOF > $tmp01
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0
set timing off

select idut||'|'||etiqueta
from b5mweb_25830.alti_r_cortadas
order by idut;

exit;
EOF

gawk '
BEGIN{
FS="|"
}
{
printf("%s|%.2f\n",$1,$2)
}
' $tmp01 | sed 's/\./,/' > $dat01
rm $tmp01 2> /dev/null

sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null
set feedback off
set linesize 32767
set long 20000000
set longchunksize 20000000
set trim on
set pages 0
set tab on
set spa 0
set timing off

drop table ${tab01};
create table ${tab01}(
idut number,
etiqueta varchar2(7),
constraint ${tab01}_pk primary key(idut)
);

exit;
EOF

rm $ctl01 2> /dev/null
rm $log01 2> /dev/null
rm $bad01 2> /dev/null
echo "load data" > $ctl01
echo "infile '${dat01}'" >> $ctl01
echo "insert" >> $ctl01
echo "into table ${tab01}" >> $ctl01
echo "fields terminated by \"|\"" >> $ctl01
echo "trailing nullcols" >> $ctl01
echo "(idut,etiqueta)" >> $ctl01

sqlldr errors=200000 userid=${usu}/${pas}@${bd} control=${ctl01} log=${log01} > /dev/null 2> /dev/null

rm $dat01 2> /dev/null
rm $ctl01 2> /dev/null
rm $log01 2> /dev/null
rm $bad01 2> /dev/null

rm ${cotas}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${cotas}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,b.etiqueta nombre_c,b.etiqueta nombre_e,'2' rotular_c,'2' rotular_e,'alti_r' tipo_c,'alti_r' tipo_e,a.tipo tipo_ut,a.point geom
from b5mweb_25830.alti_r_cortadas a,b5mweb_25830.${tab01} b
where a.idut=b.idut"

sqlplus -s ${usu}/${pas}@${bd} <<-EOF > /dev/null 2> /dev/null

drop table ${tab01};
exit;
EOF
fi

# Genera el shp de calles
if [ $calle1 -eq 1 ] ; then
echo "$0: $calle - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${calle}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${calle}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select
a.idut,
a.nomrotular_c nombre_c,
a.nomrotular_e nombre_e,
decode(a.nomrotular_c,a.nomrotular_e,a.nomrotular_c,a.nomrotular_e||' / '||a.nomrotular_c) nombre_mul,
a.rotular_c,
a.rotular_e,
a.tipo_c,
a.tipo_e,
a.tipo_ut tipo_ut,
sdo_aggr_union(sdoaggrtype(b.polyline,0.005)) geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.vialesind b,b5mweb_nombres.v_vialtramo c
where  a.idnombre_c=c.idnombre
and c.idut=b.idut
and a.rotular_e<>0
and c.otro is null
and a.tipo_c in ('calle')
group by a.idut,a.nomrotular_c,a.nomrotular_e,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut" 2> /dev/null
fi

# Genera el shp de edificios nombres
if [ $edifn1 -eq 1 ] ; then
echo "$0: $edifn - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${edifn}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${edifn}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,regexp_substr(a.nomrotular_c,'[^#]+',1,1) nombre_c,regexp_substr(a.nomrotular_e,'[^#]+',1,1) nombre_e,replace(a.nomrotular_c,'#','| |') nombre_c2,replace(a.nomrotular_e,'#','| |') nombre_e2,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,b.polygon geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.a_edifind b
where a.idut=b.idut
and a.idnomtipo in (98,99,100)
and a.rotular_e<>0
union all
select a.idut,regexp_substr(a.nomrotular_c,'[^#]+',1,1) nombre_c,regexp_substr(a.nomrotular_e,'[^#]+',1,1) nombre_e,replace(a.nomrotular_c,'#','| |') nombre_c2,replace(a.nomrotular_e,'#','| |') nombre_e2,a.rotular_c,a.rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,b.polygon geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.o_edifind b
where a.idut=b.idut
and a.idnomtipo in (98,99,100)
and a.rotular_e<>0" 2> /dev/null
fi

# Genera el shp de edificios portales
if [ $edifp1 -eq 1 ] ; then
echo "$0: $edifp - $(date '+%Y-%m-%d %H:%M:%S')" >> $log
rm ${edifp}.* 2> /dev/null
ogr2ogr \
-f "ESRI Shapefile" \
-s_srs "EPSG:25830" \
-t_srs "EPSG:25830" \
${edifp}.shp \
OCI:${usu}/${pas}@${bd}:${t} \
-sql "select a.idut,replace(ltrim(a.nomrotular_c,'0'),'Y','bis') nombre_c,replace(ltrim(a.nomrotular_e,'0'),'Y','bis') nombre_e,1 rotular_c,1 rotular_e,a.tipo_c,a.tipo_e,a.tipo_ut,b.polygon geom
from almacen_cache.cla_nombres@almacen_cache_lnk a,b5mweb_25830.a_edifind b,b5mweb_nombres.n_edifdirpos c
where a.idut=b.idut
and b.idut=c.idut
and a.idnombre_e=c.idnombre
and a.idnomtipo=97
and c.accesorio=0
and lower(a.nomrotular_e) not like 's/n%'" 2> /dev/null
fi

# Kopia
#echo "$0: kopia - $(date '+%Y-%m-%d %H:%M:%S')" >> $log

# Bukaera
db="$(date '+%Y-%m-%d %H:%M:%S')"
echo "$0: bukaera: $db" >> $log

exit 0
