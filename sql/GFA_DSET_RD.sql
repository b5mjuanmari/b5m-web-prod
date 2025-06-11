select
  a.url_2d as b5mcode,
  b.idut as b5midut,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  f.description_eu as type_eu,
  f.description_es as type_es,
  d.puente_tunel as bridge_tunnel,
  d.descripcion_e description_eu,
  d.descripcion_c description_es,
  d.observacion_e observation_eu,
  d.observacion_c observation_es,
  c.polyline as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_nombres.v_rel_vial_tramo b on to_char(b.idnombre) = a.id_nombre1
join
  b5mweb_25830.vialesind c on c.idut = b.idut
join
  b5mweb_nombres.v_vialtramo d on d.idut = b.idut
join
  b5mweb_nombres.vv_color e on to_char(e.codigo) = a.id_nombre1
join
  b5mweb_nombres.vv_color_desc f on f.color = e.color
where
  a.id_nombre2 = '9000'
order by
  a.url_2d;
