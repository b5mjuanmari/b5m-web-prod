with grouped_data as (
  select
    'MG_' || a.id_mojon as b5mcode,
    a.id_mojon as name,
    a.tipo as codetype,
    c.tipo_eu as type_eu,
    c.tipo_es as type_es,
    c.tipo_en as type_en,
    a.precision as codeprecission,
    d.precisi_eu as precission_eu,
    d.comenta_eu as precissioncomment_eu,
    d.precisi_es as precission_es,
    d.comenta_es as precissioncomment_es,
    d.precisi_en as precission_en,
    d.comenta_en as precissioncomment_en,
    a.localizacion as location,
    a.observacion_e as locationcomment_eu,
    a.observacion_c as locationcomment_es,
    a.estado as codecondition,
    e.estado_eu as condition_eu,
    e.estado_es as condition_es,
    e.estado_en as condition_en,
    a.tipologia as codetypology,
    f.tipolo_eu as typology_eu,
    f.tipolo_es as typology_es,
    f.tipolo_en as typology_en,
    a.revision as inspectiondate,
    b.idut as b5midut,
    rtrim(xmlagg(xmlelement(e, g.codigos || ', ' ) order by g.codigos).extract('//text()').getclobval(), ', ') as codenclaves,
    rtrim(xmlagg(xmlelement(e, g.encls || ', ' ) order by g.encls).extract('//text()').getclobval(), ', ') as enclaves,
    rtrim(xmlagg(xmlelement(e, g.munis || ', ' ) order by g.munis).extract('//text()').getclobval(), ', ') as municipalities
  from
    b5mweb_nombres.a_mojon a
  left join
    b5mweb_25830.muga b on a.id_mojon = b.idut
  left join
    b5mweb_nombres.a_mojon_tipo c on a.tipo = c.tipo
  left join
    b5mweb_nombres.a_mojon_precision d on a.precision = d.precision
  left join
    b5mweb_nombres.a_mojon_estado e on a.estado = e.estado
  left join
    b5mweb_nombres.a_mojon_tipologia f on a.tipologia = f.tipolo
  left join
    b5mweb_nombres.a_mojterminos g on a.id_mojon = g.id_mojon
  group by
    'MG_' || a.id_mojon,
    a.id_mojon,
    a.tipo,
    c.tipo_eu,
    c.tipo_es,
    c.tipo_en,
    a.precision,
    d.precisi_eu,
    d.comenta_eu,
    d.precisi_es,
    d.comenta_es,
    d.precisi_en,
    d.comenta_en,
    a.localizacion,
    a.observacion_e,
    a.observacion_c,
    a.estado,
    e.estado_eu,
    e.estado_es,
    e.estado_en,
    a.tipologia,
    f.tipolo_eu,
    f.tipolo_es,
    f.tipolo_en,
    a.revision,
    b.idut
)
select
  gd.*,
  b.point as geom
from
  grouped_data gd
left join
  b5mweb_25830.muga b on gd.b5midut = b.idut;
