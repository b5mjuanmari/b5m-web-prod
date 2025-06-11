select
  a.url_2d as b5mcode,
  b.idut as b5midut,
  a.nombre||' '||a.sentido_eu || ' / ' || a.sentido_es as name,
  a.nombre||' '||a.sentido_eu as name_eu,
  a.nombre||' '||a.sentido_es as name_es,
  a.pk as kp,
  substr(a.url_2d, 1, instr(a.url_2d, '_', 1, 2) - 1) as b5code_road,
  a.carre as road_name_eu,
  a.carre as road_name_es,
  a.sentido_eu as way_eu,
  a.sentido_es as way_es,
  a.sentido_en as way_en,
  a.codmunis as codmuni,
  a.muni_e as muni_eu,
  a.muni_c as muni_es,
  b.point as geom
from
  b5mweb_nombres.solr_pkil_2d a
join
  b5mweb_25830.pkil b on b.idnombre=a.idnombre
order by
  a.url_2d;
