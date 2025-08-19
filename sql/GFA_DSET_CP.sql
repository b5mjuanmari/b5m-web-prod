Catastro/Catastro_WMS

-- GUNEAK_ZONAS
-- GFA_DST_CP_ZONING
select herria as MUNI, kodea as CADASTRALZONINGCODE from GUNEAK_ZONAS

-- HIRILUR_URBANO
-- GFA_DST_CP_URBAN
select erreferentz as NATIONALCADASTRALREFERENCE, erreferentz as NAME, herria as MUNI, zona as CADASTRALZONINGCODE, concat('https://ssl6.gipuzkoa.eus/Catastro/map.htm?id=', substr(herria, 2), '&RefCat=', erreferentz) as URLINFO from HIRILUR_URBANO

-- LANDALUR_RUSTICA
-- GFA_DST_CP_LAND
select erreferentz as NATIONALCADASTRALREFERENCE, erreferentz as NAME, herria as MUNI, concat('https://ssl6.gipuzkoa.eus/Catastro/map.htm?id=', substr(herria, 2), '&LRefCat=', erreferentz) as URLINFO from LANDALUR_RUSTICA
