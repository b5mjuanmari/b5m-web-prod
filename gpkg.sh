#!/bin/bash
#
# gpkg.sh
#
# Generación de Geopackages para los servicios de localización y consulta del b5m
#

# Variables de entorno
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Tildes y eines
export NLS_LANG=.AL32UTF8
set NLS_LANG=.UTF8

# Variables
gpkgd="/home/data/datos_explotacion/CUR/gpkg"
gpkgp="/home5/GPKG"
dir="${HOME}/SCRIPTS/GPKG"
usu="b5mweb_25830"
pas="web+"
bd="bdet"
usup="genasys"
hosp="explogenamap"
logd="${dir}/log"
crn="$(echo "$0" | gawk 'BEGIN{FS="/"}{print NF}')"
scr="$(echo "$0" | gawk 'BEGIN{FS="/"}{print $NF}')"
log="$(echo "$0" | gawk -v logd="$logd" -v dat="$(date '+%Y%m%d')" 'BEGIN{FS="/"}{split($NF,a,".");print logd"/"a[1]"_"dat".log"}')"
if [ ! -d "$logd" ]
then
	mkdir "$logd" 2> /dev/null
fi
rm "$log" 2> /dev/null

# Dependencias
source "${dir}/gpkg_sql.sh"

# Funciones
function msg {
	# echo mensaje
	if [ $crn -le 2 ]
	then
		echo -e "$1"
	fi
	echo -e "$1" >> "$log"
}

function hacer_gpkg {
	# Geopackage
	t="GIPUTZ"
	rm "$fgpkg" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -lco DESCRIPTION="${des_a["$nom"]}" "$fgpkg" OCI:${usu}/${pas}@${bd}:${t} -nln "$nom" -sql "${sql_a["$nom"]}"
}

function copiar_gpkg {
	# Copiar a producción
	gpkg="${nom}.gpkg"
	tmp="${nom}_tmp.gpkg"
	/usr/bin/ssh ${usu2}@${hos2} <<-EOF1 > /dev/null 2> /dev/null
	cd "$gpkgp"
	rm "$tmp"
	EOF1
	/usr/bin/sftp ${usup}@${hosp} <<-EOF1 > /dev/null 2> /dev/null
	cd "$gpkgp"
	put "$fgpkg" "$tmp"
	EOF1
	/usr/bin/ssh ${usup}@${hosp} <<-EOF1 > /dev/null 2> /dev/null
	cd "$gpkgp"
	rm "$gpkg"
	mv "$tmp" "$gpkg"
	rm "$tmp"
	EOF1
}

# Ver si existe el fichero de configuración
fconf="$(echo $0 | gawk 'BEGIN{FS=".";i=1}{while(i<NF){printf("%s.",$i);i++}}END{printf("dsv\n")}')"
if [ ! -f "$fconf" ]
then
        echo "No existe el fichero de configuración $fconf"
        exit 1
fi

# Inicio
ini="Inicio: $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$ini"
cd "$dir"

# Lectura del fichero de configuración
vconf="$(gawk '{t=substr($0,1,1);if((t=="1")||(t=="2")||(t=="3")){print $0}}' "$fconf")"
if [ "$vconf" != "" ]
then
	j="$(echo "$vconf" | wc -l)"
else
	j=0
fi
i=1
while read vconf2
do
	IFS='|' read -a aconf <<< "$vconf2"
	tip="${aconf[0]}"
	nom="${aconf[1]}"
	des="${aconf[2]}"
	fgpkg="${gpkgd}/${nom}.gpkg"
	if [ $j -eq 0 ]
	then
		msg "0/${j}: $(date '+%Y-%m-%d %H:%M:%S') - No se hace nada"
	else
		msg "${i}/${j}: $(date '+%Y-%m-%d %H:%M:%S') - $nom - $des\c"
	fi
	if [ "$tip" = "1" ] || [ "$tip" = "2" ]
	then
		msg " - GPKG\c"
		hacer_gpkg
		msg " - ok\c"
	fi
	if [ "$tip" = "2" ] || [ "$tip" = "3" ]
	then
		msg " - PROD\c"
		copiar_gpkg
		msg " - ok\c"
	fi
	msg ""
	let i=$i+1
done <<-EOF
$vconf
EOF

msg ""
msg "$ini"
fin="Final:  $scr - $(date '+%Y-%m-%d %H:%M:%S')"
msg "$fin"

exit 0
