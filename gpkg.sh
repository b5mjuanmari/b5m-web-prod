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
gpkgd1="/home/data/gpkg"
gpkgp1="/home5/GPKG"
gpkgp2="$gpkgd1"
dir="${HOME}/SCRIPTS/GPKG"
usu="b5mweb_25830"
pas="web+"
bd="bdet"
usud1a="juanmari"
usud1b="develop"
hosd1="b5mdev"
usup1="genasys"
hosp1="explogenamap"
usup2a="juanmari"
usup2b="live"
hosp2a="b5mlive1.gipuzkoa.eus"
hosp2b="b5mlive2.gipuzkoa.eus"
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

function conx {
	# Conexión a servidores externos con comprobación de errores
	nc=10
	for c in $(seq 1 $nc)
	do
		a=`/usr/bin/${2} $1 <<-EOF2 2>&1 > /dev/null
		$3
		EOF2`
		b="$(echo "$a" | gawk 'END{print $1}')"
		if [ "$b" != "ssh_exchange_identification:" ] && [ "$b" != "Connection" ]
		then
			break
		fi
		if [ $c -eq $nc ] && { [ "$b" = "ssh_exchange_identification:" ] || [ "$b" = "Connection" ]; }
		then
				echo "Error $2 $1 #${3}# "
		else
				sleep 10
		fi
	done
}

function hacer_gpkg {
	# Tareas Oracle 1
	if [ "${or1_a["$nom"]}" != "" ]
	then
		sqlplus -s ${usu}/${pas}@${bd} <<-EOF2 > /dev/null
		${or1_a["$nom"]}

		exit;
		EOF2
	fi

	# Geopackage inicio
	t="GIPUTZ"
	rm "$fgpkg1" 2> /dev/null
	ogr2ogr -f "GPKG" -s_srs "EPSG:25830" -t_srs "EPSG:25830" -lco DESCRIPTION="${des_a["$nom"]}" "$fgpkg1" OCI:${usu}/${pas}@${bd}:${t} -nln "$nom" -sql "${sql_a["$nom"]}" > /dev/null

	# Renombrar campos
	clist="$(ogrinfo -al -so "$fgpkg1" | gawk '
	BEGIN {
		a=0
	}
	{
		if (a == 1) print substr($1, 1, length($1)-1)
		if ($1 == "Geometry") a=1
	}
	')"
	for c in $clist
	do
		c2="$(echo "$c" | gawk '{print tolower($0)}')"
		ogrinfo -dialect ogrsql -sql "alter table $nom rename column $c to ${c}999" "$fgpkg1" > /dev/null
		ogrinfo -dialect ogrsql -sql "alter table $nom rename column ${c}999 to $c2" "$fgpkg1" > /dev/null
	done

	# Crear índice
	ogrinfo -sql "create index ${nom}_idx1 on $nom (${idx_a["$nom"]})" "$fgpkg1" > /dev/null

	# Copiar a destino
	ta01="rm \"/tmp/${tmp}\""
	tb01="$(conx "${usud1a}@${hosd1}" "ssh" "$ta01")"
	ta02="put \"$fgpkg1\" \"/tmp/${tmp}\""
	tb02="$(conx "${usud1a}@${hosd1}" "sftp" "$ta02")"
	ta03="cd \"$gpkgd1\";if [ -f \"/tmp/${tmp}\" ];then sudo rm \"$gpkg\";else exit;fi;sudo mv \"/tmp/${tmp}\" \"$gpkg\";sudo chown ${usud1b}:${usud1b} \"$gpkg\";rm \"/tmp/${tmp}\""
	tb03="$(conx "${usud1a}@${hosd1}" "ssh" "$ta03")"
	tbs01="${tb01}${tb02}${tb03}"
	if [ "$tbs01" != "" ]
	then
		msg " - $tbs01\c"
	fi
	# Geopackage fin

	# Oracle carga inicio
	# En el caso de las distancias entre municipios, provisonalmente
	# se hace la carga a Oracle ya que el rendimiento de la consulta
	# es mejor
	if [ "$nom" = "dm_distancemunicipalities" ]
	then
		sql_ora_a="${sql_a["$nom"]}"
		sql_ora_b="${sql_b["$nom"]}"
		sql_ora_c="${sql_c["$nom"]}"
		sql_ora="${sql_ora_b}${sql_ora_a};${sql_ora_c}"
		sqlplus -s ${usu}/${pas}@${bd} <<-EOF2 > /dev/null
		$sql_ora
		commit;

		exit;
		EOF2
	fi
	# Oracle carga fin

	# Tareas Oracle 2
	if [ "${or2_a["$nom"]}" != "" ]
	then
		sqlplus -s ${usu}/${pas}@${bd} <<-EOF2 > /dev/null
		${or2_a["$nom"]}

		exit;
		EOF2
	fi
}

function copiar_gpkg {
	# Copiar a producción 1
	#/usr/bin/ssh ${usup1}@${hosp1} <<-EOF1 > /dev/null 2> /dev/null
	#cd "$gpkgp1"
	#rm "$tmp"
	#EOF1
	#/usr/bin/sftp ${usup1}@${hosp1} <<-EOF1 > /dev/null 2> /dev/null
	#cd "$gpkgp1"
	#put "$fgpkg1" "$tmp"
	#EOF1
	#/usr/bin/ssh ${usup1}@${hosp1} <<-EOF1 > /dev/null 2> /dev/null
	#cd "$gpkgp1"
	#rm "$gpkg"
	#mv "$tmp" "$gpkg"
	#rm "$tmp"
	#EOF1
	ta04="cd \"$gpkgp1\";rm \"${tmp}\""
	tb04="$(conx "${usup1}@${hosp1}" "ssh" "$ta04")"
	ta05="put \"$fgpkg1\" \"${gpkgp1}/${tmp}\""
	tb05="$(conx "${usup1}@${hosp1}" "sftp" "$ta05")"
	ta06="cd \"$gpkgp1\";if [ -f \"${tmp}\" ];then rm \"$gpkg\";else exit;fi;mv \"${tmp}\" \"$gpkg\";rm \"${tmp}\""
	tb06="$(conx "${usup1}@${hosp1}" "ssh" "$ta06")"
	tbs02="${tb04}${tb05}${tb06}"
	if [ "$tbs02" != "" ]
	then
		msg " - $tbs02\c"
	fi

	# Copiar a producción 2
	hosp2_a=("$hosp2a" "$hosp2b")
	for hosp2 in "${hosp2_a[@]}"
	do
		ta07="rm \"/tmp/${tmp}\""
		tb07="$(conx "${usup2a}@${hosp2}" "ssh" "$ta07")"
		ta08="put \"$fgpkg1\" \"/tmp/${tmp}\""
		tb08="$(conx "${usup2a}@${hosp2}" "sftp" "$ta08")"
		ta09="cd \"$gpkgd1\";if [ -f \"/tmp/${tmp}\" ];then sudo rm \"$gpkg\";else exit;fi;sudo mv \"/tmp/${tmp}\" \"$gpkg\";sudo chown ${usup2b}:${usup2b} \"$gpkg\";rm \"/tmp/${tmp}\""
		tb09="$(conx "${usup2a}@${hosp2}" "ssh" "$ta09")"
		tbs03="${tb07}${tb08}${tb09}"
		if [ "$tbs03" != "" ]
		then
			msg " - $tbs03\c"
		fi
	done
}

function borrar_gpkg {
	# Borrar el gpkg temporal
	rm "$fgpkg1" 2> /dev/null
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
	fgpkg1="/tmp/${nom}.gpkg"
	gpkg="${nom}.gpkg"
	tmp="${nom}_tmp.gpkg"
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
	borrar_gpkg
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
