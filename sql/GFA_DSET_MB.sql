select
  c.url_2d as b5mcode,
  a.idut as b5midut,
  a.idnombre as b5midname,
  b.codmuni,
  e.codmuniine,
  decode(c.muni_e, c.muni_c, c.muni_e, c.muni_e || ' / ' || c.muni_c) as name, -- KML
  c.muni_e as name_eu,
  c.muni_c as name_es,
  c.nombre_e as enclave_eu,
  c.nombre_c as enclave_es,
  d.nombre_e as region_eu,
  d.nombre_c as region_es,
  a.polygon as geom
from
  b5mweb_25830.gipu_a a
join
  b5mweb_25830.giputz b on a.idut = b.idut
join
  b5mweb_nombres.solr_gen_toponimia_2d c on a.idnombre = c.idnombre
left join
  b5mweb_nombres.solr_gen_toponimia_2d d on b.idnomcomarca = d.idnombre
left join
  b5mweb_nombres.n_municipios e on b.codmuni = e.codmuni
where
  c.tabla = 'n_municipios'
  and (d.tipo_c = 'comarca' or d.idnombre is null)
order by
  a.idnombre asc;
