select
  b.url_2d as b5mcode,
  a.idut as b5midut,
  a.idnombre as b5midname,
  case
    when a.nom_e is null and a.nom_c is null then null
    when a.nom_e = a.nom_c then a.nom_e
    else a.nom_e || ' / ' || a.nom_c
  end as name,
  a.nom_e as name_eu,
  a.nom_c as name_es,
   c_synonyms.synonyme_id as b5midnameothers,
  c_synonyms.synonyme_eu as name_others_eu,
  c_synonyms.synonyme_es as name_others_es,
  trim(initcap(substr(a.subtipo, 1, instr(a.subtipo, ' / ') - 1))) as subtype_eu,
  trim(initcap(substr(a.subtipo, instr(a.subtipo, ' / ') + 3))) as subtype_es,
  a.nivel as "LEVEL",
  a.idnomcuenca as b5midnamebasin,
  a.cuenca_e as basin_eu,
  a.cuenca_c as basin_es,
  a.polyline as geom
from
  b5mweb_25830.ibaiak a
left join
  b5mweb_nombres.solr_gen_toponimia_2d b on b.id_nombre1 = to_char(a.idnombre)
left join (
  select
    idnombueno,
    listagg(idnombre, ', ') within group (order by idnombre) as synonyme_id,
    listagg(nomcompleto_e, ', ') within group (order by nomcompleto_e) as synonyme_eu,
    listagg(nomcompleto_c, ', ') within group (order by nomcompleto_c) as synonyme_es
  from
    b5mweb_nombres.solr_sinonimos
  group by
    idnombueno
) c_synonyms on c_synonyms.idnombueno = to_char(a.idnombre)
where
  not (b.url_2d is null and a.nom_e is not null)
order by
  b.url_2d, a.idut;
