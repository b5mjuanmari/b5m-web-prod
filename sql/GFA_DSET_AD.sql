select
  a.url_2d as b5mcode,
  case
    when a.dirpostal_e = a.dirpostal_c then a.dirpostal_e
    else a.dirpostal_e || ' / ' || a.dirpostal_c
  end as name,
  a.dirpostal_e as name_eu,
  a.dirpostal_c as name_es,
  'posta helbidea' as type_eu,
  'dirección postal' as type_es,
  'postal address' as type_en,
  a.codmuni as codmuni,
  a.municipio_e as muni_eu,
  a.municipio_c as muni_es,
  a.codcalle as codstreet,
  a.calle_e as street_eu,
  a.calle_c as street_es,
  a.noportal as house_number,
  trim(trailing ' ' from a.bis) as bis,
  a.cp as postcode,
  a.accesorio as accessory,
  a.bloque as block,
  a.distrito as coddistri,
  a.seccion as codsec,
  a.nomedif_e as name_building_eu,
  a.nomedif_c as name_building_es,
  a.geom_cen.sdo_point.x as x_cen_etrs89,
  a.geom_cen.sdo_point.y as y_cen_etrs89,
  replace(to_char(sdo_cs.transform(a.geom_cen, 4326).sdo_point.x, 'fm99d00000'), ',', '.') || ',' ||
  replace(to_char(sdo_cs.transform(a.geom_cen, 4326).sdo_point.y, 'fm99d00000'), ',', '.') as cen_lonlat,
  replace(to_char(sdo_geom.sdo_min_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr, 4326)), 1), 'fm99d00000'), ',', '.') || ',' ||
  replace(to_char(sdo_geom.sdo_min_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr, 4326)), 2), 'fm99d00000'), ',', '.') || ',' ||
  replace(to_char(sdo_geom.sdo_max_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr, 4326)), 1), 'fm99d00000'), ',', '.') || ',' ||
  replace(to_char(sdo_geom.sdo_max_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr, 4326)), 2), 'fm99d00000'), ',', '.') as bbox_lonlat,
  a.idnombre as b5midname,
  a.geom_cen as geom
from
  b5mweb_nombres.solr_edifdirpos_2d a
order by
  a.municipio_e, a.calle_e, a.noportal, a.bis;
