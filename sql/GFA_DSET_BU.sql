select
  'E_A' || b.idut as b5mcode,
  case
    when replace(
      replace(
        replace(
          case
            when a.nomedif_e is null then a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
            else a.nomedif_e || ' - ' || a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
          end,
          ' - , ', ','
        ),
        ',  ', ' '
      ),
      '  ', ' '
    ) = replace(
      replace(
        replace(
          case
            when a.nomedif_e is null then a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
            else a.nomedif_e || ' - ' || a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
          end,
          ' - , ', ','
        ),
        ',  ', ' '
      ),
      '  ', ' '
    )
    then replace(
      replace(
        replace(
          case
            when a.nomedif_e is null then a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
            else a.nomedif_e || ' - ' || a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
          end,
          ' - , ', ','
        ),
        ',  ', ' '
      ),
      '  ', ' '
    )
    else replace(
      replace(
        replace(
          case
            when a.nomedif_e is null then a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
            else a.nomedif_e || ' - ' || a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
          end,
          ' - , ', ','
        ),
        ',  ', ' '
      ),
      '  ', ' '
    ) || ' / ' ||
    replace(
      replace(
        replace(
          case
            when a.nomedif_e is null then a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
            else a.nomedif_e || ' - ' || a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
          end,
          ' - , ', ','
        ),
        ',  ', ' '
      ),
      '  ', ' '
    )
  end as name,
  replace(
    replace(
      replace(
        case
          when a.nomedif_e is null then a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
          else a.nomedif_e || ' - ' || a.calle_e || ', ' || a.noportal || a.bis || ' ' || a.muni_e
        end,
        ' - , ', ','
      ),
      ',  ', ' '
    ),
    '  ', ' '
  ) as name_eu,
  replace(
    replace(
      replace(
        case
          when a.nomedif_e is null then a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
          else a.nomedif_e || ' - ' || a.calle_c || ', ' || a.noportal || a.bis || ' ' || a.muni_c
        end,
        ' - , ', ','
      ),
      ',  ', ' '
    ),
    '  ', ' '
  ) as name_es,
  upper(substr(b.tipo_eu, 1, 1)) || substr(b.tipo_eu, 2) as type_eu,
  upper(substr(b.tipo_es, 1, 1)) || substr(b.tipo_es, 2) as type_es,
  upper(substr(b.tipo_es, 1, 1)) || substr(b.tipo_es, 2) as type_en,
  upper(substr(b.subtipo_eu, 1, 1)) || substr(b.subtipo_eu, 2) as subtype_eu,
  upper(substr(b.subtipo_es, 1, 1)) || substr(b.subtipo_es, 2) as subtype_es,
  upper(substr(b.subtipo_es, 1, 1)) || substr(b.subtipo_es, 2) as subtype_en,
  a.codmuni as codmuni,
  a.muni_e as muni_eu,
  a.muni_c as muni_es,
  a.codcalle as codpath,
  a.calle_e as street_eu,
  a.calle_c as street_es,
  a.noportal as house_number,
  case
    when a.bis = ' ' then null
    else a.bis
  end as bis,
  case when a.codpostal = ' '
    then null
    else cast(a.codpostal as integer)
  end as postcode,
  a.accesorio as accessory,
  a.bloque as block,
  a.distrito as coddistr,
  a.seccion as codsec,
  a.idnomedif as b5midnamebuilding,
  a.nomedif_e as name_building_eu,
  a.nomedif_c as name_building_es,
  e_synonyms.synonyme_id as b5midnamebuilingothers,
  e_synonyms.synonyme_eu as name_building_others_eu,
  e_synonyms.synonyme_es as name_building_others_eu,
  c.altura_med as average_height,
  c.altura_max as max_height,
  to_char(d.dateofconstruction_end, 'yyyy-mm-dd') as date_construction,
  b.idut as b5midut,
  sdo_aggr_union(sdoaggrtype(b.polygon, 0.005)) as geom
from
  b5mweb_nombres.n_edifgen a
right join
  b5mweb_25830.a_edifind b on a.idut = b.idut
left join
  mde_web.alturas_edificios c on a.idut = c.etiqueta
left join
  b5mweb_inspire.bu_building d on a.idut = d.localid
left join (
  select
    idnombueno,
    listagg(idnombre, ', ') within group (order by idnombre) as synonyme_id,
    listagg(nomcompleto_e, '; ') within group (order by nomcompleto_e) as synonyme_eu,
    listagg(nomcompleto_c, '; ') within group (order by nomcompleto_c) as synonyme_es
  from (
    select distinct idnombueno, idnombre, nomcompleto_e, nomcompleto_c
    from b5mweb_nombres.solr_sinonimos
  )
  group by
    idnombueno
) e_synonyms on e_synonyms.idnombueno = a.idnomedif
where
  b.polygon.sdo_gtype = 2003
  and not exists (
    select 1
    from b5mweb_nombres.solr_sinonimos s
    where s.idnombre = a.idnomedif
  )
group by
  b.idut, b.tipo_eu, b.tipo_es, b.subtipo_eu, b.subtipo_es, a.idpostal,
  a.idnomedif, a.nomedif_e, a.nomedif_c, a.codmuni,
  a.muni_e, a.muni_c, a.codcalle, a.calle_e, a.calle_c, a.noportal,
  a.bis, a.codpostal, a.accesorio, a.bloque, a.distrito, a.seccion,
  c.altura_med, c.altura_max, d.dateofconstruction_end,
  e_synonyms.synonyme_id, e_synonyms.synonyme_eu, e_synonyms.synonyme_es;
