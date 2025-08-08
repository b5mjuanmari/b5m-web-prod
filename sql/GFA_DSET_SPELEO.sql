select
  'CV_' || a.tag as b5mcode,
  case
    when coalesce(b.nombre_e, b.nombre_c) = b.nombre_c then coalesce(b.nombre_e, b.nombre_c)
    else coalesce(b.nombre_e, b.nombre_c) || ' / ' || b.nombre_c
  end as name,
  b.nombre_e as name_eu,
  b.nombre_c as name_es,
  a.sinonimo as synomym,
  upper(substr(a.tipo_e, 1, 1)) || substr(a.tipo_e, 2) as type_eu,
  upper(substr(a.tipo_c, 1, 1)) || substr(a.tipo_c, 2) as type_es,
  upper(substr(a.tipo_i, 1, 1)) || substr(a.tipo_i, 2) as type_en,
  'Katalogo Espeleologikoa' as class_eu,
  'Catálogo Espeleológico' as class_es,
  'Speleological Catalogue' as class_en,
  a.origen_e as origin_eu,
  a.origen_c as origin_es,
  replace(a.origen_c, 'Sociedad de Ciencias Aranzadi', 'Aranzadi Science Society') as origin_en,
  b.codmunis as codmuni,
  b.muni_e as muni_eu,
  b.muni_c as muni_es,
  a.desnivel as heightdifference,
  a.desarrollo as length,
  case
    when a.macizo = 'PM' then a.macizo
    else upper(substr(a.macizo, 1, 1)) || lower(substr(a.macizo, 2))
  end as massif,
  upper(substr(a.zona, 1, 1)) || lower(substr(a.zona, 2)) as zone,
  a.x x_etrs89utm30N,
  a.y y_etrs89utm30N,
  a.z altitude,
  a.web_e url_eu,
  a.web_c url_es,
  a.geom as geom
from b5mweb_25830.cuevas a
join b5mweb_nombres.solr_gen_toponimia_2d b on a.tag = b.id_nombre1;
