select
  a.nombre name,
  a.codmuni as codmuni,
  b.muni_e as muni_eu,
  b.muni_c as muni_es,
  a.tipoclavo type,
  'https://b5m.gipuzkoa.eus/web5000/pdf/' || a.archivo url,
  a.geom
from
  b5mweb_bta.puntogeodesicobta a
left join
  b5mweb_nombres.solr_gen_toponimia_2d b on a.codmuni = b.idnombre and b.tabla = 'n_municipios'
where
  a.geom is not null
  and a.visible_web = 1
order by
  a.nombre;
