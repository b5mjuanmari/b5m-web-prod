select
  'AC_' || b.idut as b5mcode,
  case
    when b.linea_e = b.linea_c then b.linea_e
    else b.linea_e || ' / ' || b.linea_c
  end as name,
  b.linea_e as name_eu,
  b.linea_c as name_es,
  b.codigo1 codenclave1,
  b.encl1 enclave1,
  b.muni1 muni1,
  b.codigo2 codenclave2,
  b.encl2 enclave2,
  b.muni2 muni2,
  b.acta as linkact,
  b.cuaderno as linkfieldlog,
  b.t_mojones as numlandmarks,
  b.observacion_e as comment_eu,
  b.observacion_c as comment_es,
  to_char(b.f_validacion, 'YYYY-MM-DD') as validation_date,
  b.id_acta as b5midact,
  b.iddoc_acta as b5middocact,
  b.iddoc_cua as b5midfieldlog,
  a.polyline as geom
from
  b5mweb_25830.gipu_l a
join
  b5mweb_nombres.a_v_actas b on a.tag = to_char(b.idut)
where
  b.anulada = '0'
order by
  b.id_acta asc;
