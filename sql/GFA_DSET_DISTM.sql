select
  b5mcode,
  codmuni1,
  muni1_eu,
  muni1_es,
  codterm1 as codregion1,
  term1_eu as region1_eu,
  term1_es as region1_es,
  codmuni2,
  muni2_eu,
  muni2_es,
  codterm2 as codregion2,
  term2_eu as region2_eu,
  term2_es as region2_es,
  to_char(dist, '9999999999.9') as distance_km,
  to_char(fecha,'YYYY-MM-DD') as datecalculation
from
  b5mweb_25830.gi_wfs_dm
where
  geom is not null
order by
  b5mcode;
