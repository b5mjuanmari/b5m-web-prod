select
  b.url_2d as b5mcode,
  case
    when b.nombre_e is null and b.nombre_c is null then null
    when b.nombre_e = b.nombre_c then b.nombre_e
    else b.nombre_e || ' / ' || b.nombre_c
  end as name,
  b.nombre_e as name_eu,
  b.nombre_c as name_es,
  a.idut as b5midut,
  a.idnombre as b5midname,
  a.polygon as geom
from
  b5mweb_25830.cuencap a
left join
  b5mweb_nombres.solr_gen_toponimia_2d b on b.id_nombre1 = to_char(a.idnombre)
where
  b.tabla = 'r_cuencas'
order by
  b.url_2d, a.idut;
