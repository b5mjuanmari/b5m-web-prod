select
  a.url_2d as b5mcode,
  case
    when a.nombre_e = a.nombre_c then a.nombre_e
    else a.nombre_e || ' / ' || a.nombre_c
  end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  a.codmunis as codmuni,
  a.muni_e as munis_eu,
  a.muni_c as munis_es,
  case
    when b.tipout_e = 'hondartza_orogra' then 'Hondartza'
    else 'Marearteko hondartza'
  end as type_eu,
  case
    when b.tipout_e = 'hondartza_orogra' then 'Playa'
    else 'Playa intermareal'
  end as type_es,
  case
    when b.tipout_e = 'hondartza_orogra' then 'Beach'
    else 'Intertidal beach'
  end as type_en,
  b.idut as b5midut,
  a.idnombre as b5midname,
  c.polygon as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
join
  b5mweb_nombres.o_orograf b on b.idnombre = a.idnombre
join
  b5mweb_25830.montesind c on b.idut = c.idut
where
  b.tiponom_e = 'hondartza_orogra'
order by
  a.url_2d;
