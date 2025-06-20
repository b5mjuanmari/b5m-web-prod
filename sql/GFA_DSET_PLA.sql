select
  idut as b5midut,
  idutagr as b5midutagr,
  case
    when etiqueta_e = etiqueta_c then etiqueta_e
    else etiqueta_e || ' / ' || etiqueta_c
  end as name,
  etiqueta_e as name_eu,
  etiqueta_c as name_es,
  polyline as geom
from
  b5mweb_25830.restoind;
