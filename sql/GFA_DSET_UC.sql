select
  a.url_2d as b5mcode,
  replace(replace(replace(a.nombre_e, 'te/Mo', 'te / Mo'), 'Donostia-San', 'Donostia / San'), ', herrigunea', '') as name,
  replace(replace(a.nombre_e, 'te/Mo', 'te / Mo'), 'Donostia-San', 'Donostia / San') as name_eu,
  replace(replace(a.nombre_c, 'te/Mo', 'te / Mo'), 'Donostia-San', 'Donostia / San') as name_es,
  initcap(lower(a.tipo_e)) as type_eu,
  initcap(lower(a.tipo_c)) as type_es,
  initcap(lower(a.tipo_i)) as type_en,
  sdo_aggr_union(sdoaggrtype(b.polygon, 0.005)) as geom
from b5mweb_nombres.solr_gen_toponimia_2d a
join b5mweb_nombres.b_barrios c on a.id_nombre1 = c.idnombre
join b5mweb_25830.barrioind b on b.idut = c.idut
where a.url_2d like 'Z_A%'
  and a.tipo_e = 'hirigunea'
group by a.url_2d, a.tipo_e, a.tipo_c, a.tipo_i, a.nombre_e, a.nombre_c, a.idnombre;
