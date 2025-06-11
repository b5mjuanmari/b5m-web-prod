select
  a.url_2d as b5mcode,
  c.idut as b5midut,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  b.puente_tunel as bridge_tunnel,
  c.polyline as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_nombres.v_vialtramo b on b.idnombre = a.idnombre
join
  b5mweb_25830.vialesind c on c.idut = b.idut
where
  a.id_nombre2 = '0990'
  and b.nomtipo_e = 'trenbidea'
order by
  a.url_2d;
