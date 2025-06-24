select
  'E_A' || b.idut as b5mcode,
  case
    when a.nomedif_e = a.nomedif_c then a.nomedif_e
    else a.nomedif_e || ' / ' || a.nomedif_c
  end as name,
  a.nomedif_e as name_eu,
  a.nomedif_c as name_es,
  a.codmuni as codmuni,
  a.muni_e as muni_eu,
  a.muni_c as muni_es,
  a.codcalle as codstreet,
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
  a.idnomedif as b5midnamebuilding,
  b.idut as b5midut,
  a.idpostal as b5midaddress,
  sdo_geom.sdo_centroid(b.polygon, m.diminfo) as geom
from
  b5mweb_nombres.n_edifgen a
right join
  b5mweb_25830.a_edifind b on a.idut = b.idut
join
  user_sdo_geom_metadata m on m.table_name = 'A_EDIFIND' and m.column_name = 'POLYGON'
where
  lower(a.nomedif_e) = 'udaletxea'
  and a.idpostal <> 0
  and a.idpostal <> 23822
  and a.idpostal <> 42843
order by
  a.codmuni;
