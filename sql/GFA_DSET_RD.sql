select
  a.url_2d as b5mcode,
  c.idut as b5midut,
  a.idnombre as b5midname,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  e.description_eu as type_eu,
  e.description_es as type_es,
  b.puente_tunel as bridge_tunnel,
  b.descripcion_e description_eu,
  b.descripcion_c description_es,
  b.observacion_e observation_eu,
  b.observacion_c observation_es,
  c.polyline as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_nombres.v_vialtramo b on b.idnombre = a.idnombre
join
  b5mweb_25830.vialesind c on c.idut = b.idut
join
  b5mweb_nombres.vv_color d on to_char(d.codigo) = a.id_nombre1
join
  b5mweb_nombres.vv_color_desc e on e.color = d.color
where
  a.id_nombre2 = '9000'
  and b.nomtipo_e = 'errepidea'
order by
  a.url_2d;
