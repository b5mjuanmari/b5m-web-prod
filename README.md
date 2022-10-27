# b5m-gpkg

Carga de datos en formato GPKG como base de datos del servicio OGC WFS que ofrece los datos geográficos de Gipuzkoa al visor b5map.

## Objective

El objetivo de la carga es ofrecer los datos geográficos de Gipuzkoa para su consulta y localización

## Elements

The Service architecture has the following elements (more will be added):
La arquitectura de la carga tiene los siguientes *scripts*:

- [gpkg.sh](/gpkg.sh): Bash *script* donde se configura la carga GPKG por medio de la librería <a href="https://gdal.org/" target="_blank">GDAL</a>.
- [gpkg_sql.sh](/gpkg_sql.sh): fichero donde se configuran, por medio de *arrays*, las llamadas SQL a la base de datos de Oracle de explotación del b5m.
- [gpkg.dsv](gpkg.dsv): fichero DSV donde se configuran las categorías de información geográfica a cargar
