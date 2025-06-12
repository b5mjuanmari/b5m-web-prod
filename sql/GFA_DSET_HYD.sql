select
  a.url_2d as b5mcode,
  b.idut as b5midut,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  b.subtipo as subtype,
  trim(initcap(substr(b.subtipo, 1, instr(b.subtipo, ' / ') - 1))) as subtype_eu,
  trim(initcap(substr(b.subtipo, instr(b.subtipo, ' / ') + 3))) as subtype_es,
  b.nivel as "LEVEL",
  b.idnomcuenca as idnombasin,
  b.cuenca_e as basin_eu,
  b.cuenca_c as basin_es,
  b.polyline as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_25830.ibaiak b on to_char(b.idnombre) = a.id_nombre1
order by
  a.url_2d, b.idut;
