select
  idut as b5midut,
  etiqueta as name,
  etiqueta as altimetry_value,
  upper(substr(mota, 1, 1)) || substr(mota, 2) as type_eu,
  case
    when tipo = 'curva de depresión' then 'Curva de nivel de depresión'
    else upper(substr(tipo, 1, 1)) || substr(tipo, 2)
  end as type_es,
  case
    when mota = 'sakonuneko sestra kurba' then 'Depression contour line'
    when mota = 'sestra kurba' then 'Contour line'
    else upper(substr(mota, 1, 1)) || substr(mota, 2)
  end as type_en,
  polyline as geom
from
  b5mweb_25830.alti_5;
