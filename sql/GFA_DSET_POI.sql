select
  'POI_' || a.id_actividad as b5mcode,
  case
    when coalesce(a.nombre_comercial_e, a.nombre_comercial_c) = a.nombre_comercial_c then coalesce(a.nombre_comercial_e, a.nombre_comercial_c)
    else coalesce(a.nombre_comercial_e, a.nombre_comercial_c) || ' / ' || a.nombre_comercial_c
  end as name,
  coalesce(a.nombre_comercial_e, a.nombre_comercial_c) as name_eu,
  a.nombre_comercial_c as name_es,
  e.name_eu as type_eu,
  e.name_es as type_es,
  e.name_en as type_en,
  e.title_eu as class_eu,
  e.title_es as class_es,
  e.title_en as class_en,
  e.description_eu as class_description_eu,
  e.description_es as class_description_es,
  e.description_en as class_description_en,
  i.url || '/' || g.icon as class_icon,
  d.title_eu as category_eu,
  d.title_es as category_es,
  d.title_en as category_en,
  d.description_eu as category_description_eu,
  d.description_es as category_description_es,
  d.description_en as category_description_en,
  i.url || '/' || h.icon as category_icon,
  'D_A' || a.id_postal as b5mcode_d,
  b.codmuni as codmuni,
  b.muni_e as muni_eu,
  b.muni_c as muni_es,
  b.codcalle as codstreet,
  b.calle_e as street_eu,
  b.calle_c as street_es,
  b.noportal as house_number,
  b.bis as bis,
  to_char(b.accesorio) as accessory,
  b.codpostal as postal_code,
  a.cla_santi as b5midpoi,
  c.point as geom
from b5mweb_nombres.n_actipuerta a
join b5mweb_nombres.n_dir_postal b on a.id_postal = b.idnombre
join b5mweb_25830.puertas c on a.id_puerta = c.id_puerta
join b5mweb_nombres.poi_classes e on a.cla_santi = e.code
join b5mweb_nombres.poi_cat_class f on e.id = f.poi_class_id
join b5mweb_nombres.poi_categories d on d.id = f.poi_category_id
join b5mweb_nombres.poi_icons g on e.icon_id = g.id
join b5mweb_nombres.poi_icons h on d.icon_id = h.id
join b5mweb_nombres.poi_icons_url i on i.id = 1
where a.id_postal <> 0
  and d.enabled = 1
  and a.cla_santi <> 'F.1.1'
union all
select b5mcode, name, name_eu, name_es, type_eu, type_es, type_en, class_eu, class_es, class_en,
   class_description_eu, class_description_es, class_description_en,
   class_icon, category_eu, category_es, category_en,
   category_description_eu, category_description_es, category_description_en,
   category_icon, b5mcode_d, codmuni, muni_eu, muni_es,
   codstreet, street_eu, street_es, house_number, bis, accessory, postal_code,
   b5midpoi, geom
from (
  select
    'POI_' || b.idnombre as b5mcode,
    case
      when b.izena = b.nombre then b.izena
      else b.izena || ' / ' || b.nombre
    end as name,
    b.izena as name_eu,
    b.nombre as name_es,
    f.name_eu as type_eu,
    f.name_es as type_es,
    f.name_en as type_en,
    f.title_eu as class_eu,
    f.title_es as class_es,
    f.title_en as class_en,
    f.description_eu as class_description_eu,
    f.description_es as class_description_es,
    f.description_en as class_description_en,
    j.url || '/' || h.icon as class_icon,
    e.title_eu as category_eu,
    e.title_es as category_es,
    e.title_en as category_en,
    e.description_eu as category_description_eu,
    e.description_es as category_description_es,
    e.description_en as category_description_en,
    j.url || '/' || i.icon as category_icon,
    case
      when c.idpostal is null or c.idpostal = 0 then null
      else 'D_A' || c.idpostal
    end as b5mcode_d,
    c.codmuni as codmuni,
    d.nombre_e as muni_eu,
    d.nombre_c as muni_es,
    c.codcalle as codstreet,
    c.calle as street_eu,
    c.calle as street_es,
    c.noportal as house_number,
    c.bis as bis,
    c.acc as accessory,
    c.cp as postal_code,
    f.code as b5midpoi,
    a.point as geom,
    row_number() over (partition by
      b.idnombre, b.izena, b.izena, b.nombre,
      f.title_eu, f.title_es, f.title_en,
      f.description_eu, f.description_es, f.description_en,
      j.url, h.icon,
      e.title_eu, e.title_es, e.title_en,
      e.description_eu, e.description_es, e.description_en,
      i.icon, c.idpostal, c.codmuni,
      d.nombre_e, d.nombre_c, c.codcalle,
      c.calle, c.noportal, c.bis, c.acc, c.cp, f.code
      order by b.idnombre) as rn
    from b5mweb_25830.monu1p a
    join b5mweb_25830.monu1 b on a.idut = b.idut
    left join b5mweb_nombres.n_edifacti2 c
      on c.idut = b.idut
      and c.cla_santi = 'F.1.1'
    left join b5mweb_nombres.solr_gen_toponimia_2d d
      on c.codmuni = d.id_nombre1
      and d.tabla = 'n_municipios'
    join b5mweb_nombres.poi_classes f
      on f.code = 'F.1.1'
    join b5mweb_nombres.poi_cat_class g
      on f.id = g.poi_class_id
    join b5mweb_nombres.poi_categories e
      on e.id = g.poi_category_id
    join b5mweb_nombres.poi_icons h
      on f.icon_id = h.id
    join b5mweb_nombres.poi_icons i
      on e.icon_id = i.id
    join b5mweb_nombres.poi_icons_url j
      on j.id = 1
)
where rn = 1
union all
select
  'POI_' || a.idnombre as b5mcode,
  case
    when a.izena = a.nombre then a.izena
    else a.izena || ' / ' || a.nombre
  end as name,
  a.izena as name_eu,
  a.nombre as name_es,
  f.name_eu as type_eu,
  f.name_es as type_es,
  f.name_en as type_en,
  f.title_eu as class_eu,
  f.title_es as class_es,
  f.title_en as class_en,
  f.description_eu as class_description_eu,
  f.description_es as class_description_es,
  f.description_en as class_description_en,
  j.url || '/' || h.icon as class_icon,
  e.title_eu as category_eu,
  e.title_es as category_es,
  e.title_en as category_en,
  e.description_eu as category_description_eu,
  e.description_es as category_description_es,
  e.description_en as category_description_en,
  j.url || '/' || i.icon as category_icon,
  case
    when c.idpostal is null or c.idpostal = 0 then null
    else 'D_A' || c.idpostal
  end as b5mcode_d,
  c.codmuni as codmuni,
  d.nombre_e as muni_eu,
  d.nombre_c as muni_es,
  c.codcalle as codstreet,
  c.calle as street_eu,
  c.calle as street_es,
  c.noportal as house_number,
  c.bis as bis,
  c.acc as accessory,
  c.cp as postal_code,
  f.code as b5midpoi,
  a.geom as geom
from b5mweb_25830.monu3 a
left join b5mweb_nombres.n_edifacti2 c
  on c.idut = a.idut
  and c.cla_santi = 'F.1.1'
left join b5mweb_nombres.solr_gen_toponimia_2d d
  on c.codmuni = d.id_nombre1
  and d.tabla = 'n_municipios'
join b5mweb_nombres.poi_classes f
  on f.code = 'F.1.1'
join b5mweb_nombres.poi_cat_class g
  on f.id = g.poi_class_id
join b5mweb_nombres.poi_categories e
  on e.id = g.poi_category_id
join b5mweb_nombres.poi_icons h
  on f.icon_id = h.id
join b5mweb_nombres.poi_icons i
  on e.icon_id = i.id
join b5mweb_nombres.poi_icons_url j
  on j.id = 1
union all
select
  'POI_' || a.idnombre as b5mcode,
  case
    when a.izena = a.nombre then a.izena
    else a.izena || ' / ' || a.nombre
  end as name,
  a.izena as name_eu,
  a.nombre as name_es,
  f.name_eu as type_eu,
  f.name_es as type_es,
  f.name_en as type_en,
  f.title_eu as class_eu,
  f.title_es as class_es,
  f.title_en as class_en,
  f.description_eu as class_description_eu,
  f.description_es as class_description_es,
  f.description_en as class_description_en,
  j.url || '/' || h.icon as class_icon,
  e.title_eu as category_eu,
  e.title_es as category_es,
  e.title_en as category_en,
  e.description_eu as category_description_eu,
  e.description_es as category_description_es,
  e.description_en as category_description_en,
  j.url || '/' || i.icon as category_icon,
  case
    when c.idpostal is null or c.idpostal = 0 then null
    else 'D_A' || c.idpostal
  end as b5mcode_d,
  c.codmuni as codmuni,
  d.nombre_e as muni_eu,
  d.nombre_c as muni_es,
  c.codcalle as codstreet,
  c.calle as street_eu,
  c.calle as street_es,
  c.noportal as house_number,
  c.bis as bis,
  c.acc as accessory,
  c.cp as postal_code,
  f.code as b5midpoi,
  a.point as geom
from b5mweb_25830.monu5 a
left join b5mweb_nombres.n_edifacti2 c
  on c.idut = a.idut
  and c.cla_santi = 'F.1.1'
left join b5mweb_nombres.solr_gen_toponimia_2d d
  on c.codmuni = d.id_nombre1
  and d.tabla = 'n_municipios'
join b5mweb_nombres.poi_classes f
  on f.code = 'F.1.1'
join b5mweb_nombres.poi_cat_class g
  on f.id = g.poi_class_id
join b5mweb_nombres.poi_categories e
  on e.id = g.poi_category_id
join b5mweb_nombres.poi_icons h
  on f.icon_id = h.id
join b5mweb_nombres.poi_icons i
  on e.icon_id = i.id
join b5mweb_nombres.poi_icons_url j
  on j.id = 1;
