#!/bin/bash
#
# ===================================================================================== #
#  +---------------------------------------------------------------------------------+  #
#  | gpkg2.sh                                                                        |  #
#  | Geopackageak sortzea b5m-ren lokalizazio- eta kontsulta-zerbitzuetarako         |  #
#  | Generación de Geopackages para los servicios de localización y consulta del b5m |  #
#  +---------------------------------------------------------------------------------+  #
# ===================================================================================== #
#

# Inguruneko aldagaiak / Variables de entorno
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Tildeak eta eñeak / Tildes y eñes
export NLS_LANG=.AL32UTF8
set NLS_LANG=.UTF8
#export NLS_LANG=American_America.UTF8

# Aldagaiak / Variables
dir="${HOME}/SCRIPTS/GPKG"
gpkd="/home/data/gpkg2"
gpkp="$gpkd"
usr="b5mweb_25830"
pas="web+"
db="bdet"
tpl="giputz"
usrd1="juanmari"
usrd2="develop"
hstd1="b5mdev"
usrp1="juanmari"
usrp2="live"
hstp1a="b5mlive1.gipuzkoa.eus"
hstp1b="b5mlive2.gipuzkoa.eus"
tmpd="/tmp"

# Beste aldagaiak / Otras variables
i1=0
logd="${dir}/log"
crn="$(echo "$0" | gawk 'BEGIN{FS="/"}{print NF}')"
scr="$(echo "$0" | gawk 'BEGIN{FS="/"}{print $NF}')"
log="$(echo "$0" | gawk -v logd="$logd" -v dat="$(date '+%Y%m%d')" 'BEGIN{FS="/"}{split($NF,a,".");print logd"/"a[1]"_"dat".log"}')"
err="$(echo "$0" | gawk -v logd="$logd" -v dat="$(date '+%Y%m%d')" 'BEGIN{FS="/"}{split($NF,a,".");print logd"/"a[1]"_"dat"_err.csv"}')"
if [ ! -d "$logd" ]
then
	mkdir "$logd" 2> /dev/null
fi
rm "$log" 2> /dev/null
rm "$err" 2> /dev/null

# Eremuak deskribatzeko aldagaiak / Variables de descripción de campos
des_c1="field_name,description_eu,description_es,description_en"
des_c2="field descriptions"

# Deskarga-taulen aldagaiak / Variables de las tablas de descarga
dwm_c1="\"id_dw\",\"b5mcode\",\"b5mcode2\",\"name_es\",\"name_eu\",\"name_en\",\"year\",\"path_dw\",\"type_dw\",\"type_file\",\"url_metadata\""
dwn_url1="https://b5m.gipuzkoa.eus"

# Konfigurazio-fitxategia dagoen egiaztatu / Comprobar si hay un fichero de configuración
fconf="$(echo $0 | gawk 'BEGIN{FS=".";i=1}{while(i<NF){printf("%s.",$i);i++}}END{printf("dsv\n")}')"
if [ ! -f "$fconf" ]
then
	echo "Ez dago $fconf konfigurazio-fitxategia"
	exit 1
fi
nf=`gawk '{t=substr($0,1,1);if((t=="1")||(t=="2")||(t=="3")){print $0}}' "$fconf" | wc -l`

# Menpekotasunak / Dependencias
source "${dir}/gpkg2_fnc.sh"
source "${dir}/gpkg2_sql.sh"

# Hasiera / Inicio
ini="Hasiera / Inicio: $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$ini"
cd "$dir"

# =============================================== #
#  +-------------------------------------------+  #
#  |     Datuak kargatzea / Carga de datos     |  #
#  +-------------------------------------------+  #
# =============================================== #

# =================================================== #
#                                                     #
# 1. m_municipalities (udalerriak / municipios) (13") #
#                                                     #
# =================================================== #

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
let i1=$i1+1
vconf=`grep "$m_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${aconf[2]}"
if [ "$m_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - $des01\c"
	f01="${tmpd}/${m_gpk}_01.gpkg"
	c01="${tmpd}/${m_gpk}_01.csv"
	f02="${tmpd}/${m_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${usr}/${pas}@${db}:${tpl} -nln "$m_gpk" -lco DESCRIPTION="$des01" -sql "$m_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sqlplus -s ${usr}/${pas}@${db} <<-EOF1 | gawk '
	{
	  if (NR != 1)
	  	print $0
	}
	' > "$c01"
	set serveroutput on
	set feedback off
	set linesize 32767
	set long 20000000
	set longchunksize 20000000
	set trim on
	set pages 0
	set tab on
	set spa 0
	set mark csv on

	${m_sql_02};

	exit;
	EOF1
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" "$c01" -nln "${m_gpk}_more_info" -lco DESCRIPTION="${des01} more info"
	rm "$c01" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f02" "$f01" -nln "$m_gpk" -lco DESCRIPTION="$des01" -sql "$m_sql_03"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$m_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cop_gpk "$typ01" "$m_gpk"
	msg " - ${typ01}\c"
fi

# Bukaera / Final
msg ""
msg "$fin"
fin="Bukaera / Final:  $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$fin"

exit 0
