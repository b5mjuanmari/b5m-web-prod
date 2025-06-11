select
  c.url_2d as b5mcode,
  a.idut as b5midut,
  b.nombre_e as name,
  b.nombre_e as name_eu,
  b.nombre_c as name_es,
  b.nomtipo_e as type_eu,
  b.nomtipo_c as type_es,
  b.codigo1 as codmuni,
  b.codigo2 as codvial,
  b.puente_tunel as bridge_tunnel,
  b.descripcion_e description_eu,
  b.descripcion_c description_es,
  b.observacion_e observation_eu,
  b.observacion_c observation_es,
  a.polyline as geom
from
  b5mweb_25830.vialesind a
join
  b5mweb_nombres.v_vialtramo b on b.idut = a.idut
left join
  b5mweb_nombres.solr_gen_toponimia_2d c on c.idnombre = b.idnombre
order by
  a.idut;
