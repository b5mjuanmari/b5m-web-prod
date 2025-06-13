select
  a.url_2d as b5mcode,
  case when a.nombre_e = a.nombre_c then a.nombre_e else a.nombre_e || ' / ' || a.nombre_c end as name,
  a.nombre_e as name_eu,
  a.nombre_c as name_es,
  a.tipo_e as type_eu,
  a.tipo_c as type_es,
  a.tipo_i as type_en,
  a.codmunis as codmuni,
  a.muni_e as muni_eu,
  a.muni_c as muni_es,
  a.cuen_e as basin_eu,
  a.cuen_c as basin_es,
  a.desc_e as desc_eu,
  a.desc_c as desc_es,
  a.desc_i as desc_en,
  b.codcalle as codpath,
  b.calle_e as street_eu,
  b.calle_c as street_es,
  b.noportal as house_number,
  trim(trailing ' ' from b.bis) as bis,
  b.cp as postcode,
  b.accesorio as accessory,
  b.bloque as block,
  b.distrito as coddistri,
  b.seccion as codsec,
  b.nomedif_e as name_building_eu,
  b.nomedif_c as name_building_es,
  a.geom_cen.sdo_point.x as x_cen_etrs89,
  a.geom_cen.sdo_point.y as y_cen_etrs89,
  replace(to_char(sdo_cs.transform(a.geom_cen,4326).sdo_point.x,'fm99d00000'),',','.') || ',' ||
  replace(to_char(sdo_cs.transform(a.geom_cen,4326).sdo_point.y,'fm99d00000'),',','.') as cen_lonlat,
  replace(to_char(sdo_geom.sdo_min_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr,4326)),1),'fm99d00000'),',','.') || ',' ||
  replace(to_char(sdo_geom.sdo_min_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr,4326)),2),'fm99d00000'),',','.') || ',' ||
  replace(to_char(sdo_geom.sdo_max_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr,4326)),1),'fm99d00000'),',','.') || ',' ||
  replace(to_char(sdo_geom.sdo_max_mbr_ordinate(sdo_geom.sdo_mbr(sdo_cs.transform(a.geom_mbr,4326)),2),'fm99d00000'),',','.') as bbox_lonlat,
  a.idnombre as b5midname,
  a.geom_cen as geom
from
  b5mweb_nombres.solr_gen_toponimia_2d a
left outer join
  b5mweb_nombres.solr_edifdirpos_2d b on a.url_2d = b.url_2d
where
  a.tabla <> 'cuadriculas'
order by
  a.nombre_e asc;
