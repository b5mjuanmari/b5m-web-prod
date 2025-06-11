select
  a.url_2d as b5mcode,
  b.idut as b5midut,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  d.puente_tunel as bridge_tunnel,
  c.polyline as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_nombres.v_rel_vial_tramo b on to_char(b.idnombre) = a.id_nombre1
join
  b5mweb_25830.vialesind c on c.idut = b.idut
join
  b5mweb_nombres.v_vialtramo d on d.idut = b.idut
where
  a.id_nombre2 = '0990'
  and d.nomtipo_e = 'trenbidea'
order by
  a.url_2d;
