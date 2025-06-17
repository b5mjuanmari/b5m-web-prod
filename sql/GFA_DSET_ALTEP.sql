select
  idut as b5midut,
  etiqueta as name,
  etiqueta as altimetry_value,
  case
    when tipo = 'cota de cima' then 'Gailur kota'
    when tipo = 'cota de collado' then 'Mendi-lepo kota'
    when tipo = 'cota de depresión' then 'Sakonune kota'
    when tipo = 'cota de gálibo' then 'Galibo kota'
    when tipo = 'cota de túnel' then 'Tunel kota'
    when tipo = 'cota sin discriminar' then 'Bereizi gabeko kota'
    when tipo = 'cota sobre la red viaria' then 'Bide sarearen gaineko kota'
    when tipo = 'cota sobre puente' then 'Zubi gaineko kota'
    else upper(substr(tipo, 1, 1)) || substr(tipo, 2)
  end as type_eu,
  upper(substr(tipo, 1, 1)) || substr(tipo, 2) as type_es,
  case
    when tipo = 'cota de cima' then 'Summit elevation'
    when tipo = 'cota de collado' then 'Mountain pass elevation'
    when tipo = 'cota de depresión' then 'Depression elevation'
    when tipo = 'cota de gálibo' then 'Clearance elevation'
    when tipo = 'cota de túnel' then 'Tunnel elevation'
    when tipo = 'cota sin discriminar' then 'Elevation without discrimination'
    when tipo = 'cota sobre la red viaria' then 'Elevation above road network'
    when tipo = 'cota sobre puente' then 'Elevation above bridge'
    else upper(substr(tipo, 1, 1)) || substr(tipo, 2)
  end as type_en,
  point as geom
from
  b5mweb_25830.alti_r;
