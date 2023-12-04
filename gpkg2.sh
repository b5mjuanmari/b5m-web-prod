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
con1="b5mweb_25830/web+@//exploracle:1521/bdet"
con2="etl_cfg/web+@//etlowb:1521/bdowb"
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

# =============================================== #
#  +-------------------------------------------+  #
#  |     Datuak kargatzea / Carga de datos     |  #
#  +-------------------------------------------+  #
# =============================================== #

# ===================== #
#                       #
# 0.1. update_date info #
#                       #
# ===================== #

updd=`sqlplus -s ${con2} <<-EOF
set feedback off
set linesize 32767
set trim on
set pages 0

select to_char(fecha_inicio,'YYYY-MM-DD')
from etl_sinc
where rownum=1
order by id_sinc desc;

exit;
EOF`

# ================================== #
#                                    #
# 0.2. Menpekotasunak / Dependencias #
#                                    #
# ================================== #

source "${dir}/gpkg2_sql.sh"
source "${dir}/gpkg2_fnc.sh"

# ===================== #
#                       #
# 0.3. Hasiera / Inicio #
#                       #
# ===================== #

ini="Hasiera / Inicio: $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$ini"
cd "$dir"

# =========================================== #
#                                             #
# 1. m_municipalities (udalerria / municipio) #
#                                             #
# =========================================== #

# 19"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$m_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${s_des[0]} - ${s_des[1]} - ${s_des[2]}"
if [ "$m_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${m_des[0]}\c"
	f01="${tmpd}/${m_gpk}_01.gpkg"
	c01="${tmpd}/${m_gpk}_01.csv"
	f02="${tmpd}/${m_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$m_gpk" -lco DESCRIPTION="$des01" -sql "$m_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$m_sql_02"
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${m_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$m_gpk" -lco DESCRIPTION="$des01" -sql "$m_sql_03" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$m_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$m_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# ================================== #
#                                    #
# 2. s_regions (eskualdea / comarca) #
#                                    #
# ================================== #

# 34"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$s_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${s_des[0]} - ${s_des[1]} - ${s_des[2]}"
if [ "$s_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${s_des[0]}\c"
	f01="${tmpd}/${s_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$s_gpk" -lco DESCRIPTION="$des01" -sql "$s_sql_01"

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f01" "$s_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$s_gpk"
	msg " - ${typ01}"
	rm "$f01" 2> /dev/null
fi

# ======================================================== #
#                                                          #
# 3. d_postaladdresses (posta helbidea / dirección postal) #
#                                                          #
# ======================================================== #

# 8'57"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$d_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${s_des[0]} - ${s_des[1]} - ${s_des[2]}"
if [ "$d_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${d_des[0]}\c"
	f01="${tmpd}/${d_gpk}_01.gpkg"
	c01="${tmpd}/${d_gpk}_01.csv"
	c02="${tmpd}/${d_gpk}_02.csv"
	f02="${tmpd}/${d_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$d_gpk" -lco DESCRIPTION="$des01" -sql "$d_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$d_sql_02"
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${d_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# poi
	rm "$c02" 2> /dev/null
	sql_poi "$c02" "$d_sql_03"
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${d_gpk}_poi" -lco DESCRIPTION="${des01} poi" "$f01" "$c02"
	rm "$c02" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${d_gpk}_2" -lco DESCRIPTION="${des01} 2" -sql "${d_sql_04}" "$f01" "$f01"
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$d_gpk" -lco DESCRIPTION="$des01" -sql "$d_sql_05" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$d_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$d_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# ==================================== #
#                                      #
# 4. e_buildings (eraikina / edificio) #
#                                      #
# ==================================== #

# 9'04"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$e_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${e_des[0]} - ${e_des[1]} - ${e_des[2]}"
if [ "$e_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${e_des[0]}\c"
	f01="${tmpd}/${e_gpk}_01.gpkg"
	c01="${tmpd}/${e_gpk}_01.csv"
	c02="${tmpd}/${e_gpk}_02.csv"
	f02="${tmpd}/${e_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$e_gpk" -lco DESCRIPTION="$des01" -sql "$e_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$e_sql_02"
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${e_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# poi
	rm "$c02" 2> /dev/null
	sql_poi "$c02" "$e_sql_03"
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${e_gpk}_poi" -lco DESCRIPTION="${des01} poi" "$f01" "$c02"
	rm "$c02" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${e_gpk}_2" -lco DESCRIPTION="${des01} 2" -sql "${e_sql_04}" "$f01" "$f01"
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$e_gpk" -lco DESCRIPTION="$des01" -sql "$e_sql_05" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$e_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$e_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# ================================================================================ #
#                                                                                  #
# 5. k_streets_buildings (kalea [eraikin multzoa] / calle [conjunto de edificios]) #
#                                                                                  #
# ================================================================================ #

# 1'36"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$k_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${k_des[0]} - ${k_des[1]} - ${k_des[2]}"
if [ "$k_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${k_des[0]}\c"
	f01="${tmpd}/${k_gpk}_01.gpkg"
	c01="${tmpd}/${k_gpk}_01.csv"
	f02="${tmpd}/${k_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$k_gpk" -lco DESCRIPTION="$des01" -sql "$k_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$k_sql_02"
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${k_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$k_gpk" -lco DESCRIPTION="$des01" -sql "$k_sql_03" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$k_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$k_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# ================================================= #
#                                                   #
# 6. v_streets_axis (kalea [ardatza] / calle [eje]) #
#                                                   #
# ================================================= #

# 9'42"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$v_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${v_des[0]} - ${v_des[1]} - ${v_des[2]}"
if [ "$v_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${v_des[0]}\c"
	f01="${tmpd}/${v_gpk}_01.gpkg"
	c01="${tmpd}/${v_gpk}_01.csv"
	f02="${tmpd}/${v_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$v_gpk" -lco DESCRIPTION="$des01" -sql "$v_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$v_sql_02"
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${v_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$v_gpk" -lco DESCRIPTION="$des01" -sql "$v_sql_03" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$v_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$v_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# =========================== #
#                             #
# 7. c_basins (arroa /cuenca) #
#                             #
# =========================== #

# 17"

# Konfigurazio-fitxategia irakurri / Leer el fichero de configuración
vconf=`grep "$c_gpk" "$fconf"`
IFS='|' read -a aconf <<< "$vconf"
typ01="${aconf[0]}"
gpk01="${aconf[1]}"
des01="${c_des[0]} - ${c_des[1]} - ${c_des[2]}"
if [ "$c_gpk" = "$gpk01" ] && ([ $typ01 = "1" ] || [ "$typ01" = "2" ])
then
	let i1=$i1+1
	msg "${i1}/${nf}: $(date '+%Y-%m-%d %H:%M:%S') - $gpk01 - ${c_des[0]}\c"
	f01="${tmpd}/${c_gpk}_01.gpkg"
	c01="${tmpd}/${c_gpk}_01.csv"
	f02="${tmpd}/${c_gpk}.gpkg"

	# Oinarrizko datuak / Datos básicos
	rm "$f01" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" OCI:${con1}:${tpl} -nln "$c_gpk" -lco DESCRIPTION="$des01" -sql "$c_sql_01"

	# more_info
	rm "$c01" 2> /dev/null
	sql_more_info "$c01" "$c_sql_02"
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "${c_gpk}_more_info" -lco DESCRIPTION="${des01} more info" "$f01" "$c01"
	rm "$c01" 2> /dev/null

	# Behin betiko GPKGa / GPKG definitivo
	rm "$f02" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -nln "$c_gpk" -lco DESCRIPTION="$des01" -sql "$c_sql_03" "$f02" "$f01"
	rm "$f01" 2> /dev/null

	# Eremuak berrizendatu / Renombrar campos
	rfl "$f02" "$c_gpk"

	# Garapenera edo ekoizpenera kopiatu / Copiar a desarrollo o a producción
	cp_gpk "$typ01" "$c_gpk"
	msg " - ${typ01}"
	rm "$f02" 2> /dev/null
fi

# ===================== #
#                       #
# 99.0. Bukaera / Final #
#                       #
# ===================== #

msg "$fin"
fin="Bukaera / Final:  $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$fin"

exit 0
