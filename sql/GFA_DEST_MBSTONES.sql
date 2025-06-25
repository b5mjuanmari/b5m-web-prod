with
mozterminos_data as (
  select
    id_mojon,
    rtrim(xmlagg(xmlelement(e, codigos || ', ') order by codigos).extract('//text()').getclobval(), ', ') as codenclaves,
    rtrim(xmlagg(xmlelement(e, encls || ', ') order by encls).extract('//text()').getclobval(), ', ') as enclaves,
    rtrim(xmlagg(xmlelement(e, munis || ', ') order by munis).extract('//text()').getclobval(), ', ') as municipalities
  from
    b5mweb_nombres.a_mojterminos
  group by
    id_mojon
),
mojacta_data as (
  select
    id_mojon,
    rtrim(xmlagg(xmlelement(e, id_acta || ', ') order by id_acta).extract('//text()').getclobval(), ', ') as id_actas,
    rtrim(xmlagg(xmlelement(e, num || ', ') order by id_acta).extract('//text()').getclobval(), ', ') as nums
  from
    b5mweb_nombres.a_mojacta1
  group by
    id_mojon
),
grouped_data as (
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
    gd.codenclaves,
    gd.enclaves,
    gd.municipalities,
    md.id_actas as b5midacts,
    md.nums as numberinact,
    b.idut as b5midut
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
    mozterminos_data gd on a.id_mojon = gd.id_mojon
  left join
    mojacta_data md on a.id_mojon = md.id_mojon
)
select
  gd.*,
  b.point as geom
from
  grouped_data gd
left join
  b5mweb_25830.muga b on gd.b5midut = b.idut;
