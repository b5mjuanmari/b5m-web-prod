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

# Variables descripción campos
des_c1="field_name,description_eu,description_es,description_en"
des_c2="field descriptions"

# Varibales tablas descargas
dwm_c1="\"id_dw\",\"b5mcode\",\"b5mcode2\",\"name_es\",\"name_eu\",\"name_en\",\"year\",\"path_dw\",\"type_dw\",\"type_file\",\"url_metadata\""
dw_url1="https://b5m.gipuzkoa.eus"
dwn_srs1="EPSG:25830"
dwn_srs2="ETRS89 / UTM zone 30N"
dwn_srs3="https://epsg.io/25830"

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

	# Crear tabla con las descripciones de los campos
	ca0="$(ogrinfo -al -so $fgpkg1 $nom | gawk 'BEGIN{a=0;FS=":"}{if(match($0,"Geometry Column")!=0){a=1;getline};if(a==1){print $1}}')"
	IFS='#' read -a ca1 <<< "${der_a["$nom"]}"
	rm "$csv" 2> /dev/null
	echo "$des_c1" > "$csv"
	for ca2 in $ca0
	do
		for ca3 in "${ca1[@]}"
		do
			IFS='|' read -a ca4 <<< "$ca3"
			if [ "$ca2" = "${ca4[0]}" ]
			then
				echo $ca3 | sed 's/|/,/g' >> "$csv"
			fi
		done
	done
	ca5="$(wc -l "$csv" | gawk '{print $1}')"
	if [ $ca5 -gt 1 ]
	then
		ogr2ogr -f "GPKG" -update "$fgpkg1" "$csv" -nln "${nom}_desc" -lco DESCRIPTION="$nom $des_c2"
	fi
	rm "$csv" 2> /dev/null

	# Crear tablas de descargas
	if [ "${dwn_a["$nom"]}" = "1" ]
	then
		dwn_c2=`sqlplus -s ${usu}/${pas}@${bd} <<-EOF2 2> /dev/null
		set mark csv on

		select *
		from b5mweb_nombres.dw_list;

		exit;
		EOF2`
		rm "$csv" 2> /dev/null
		i=0
		for dwn_d in `echo "$dwn_c2"`
		do
			if [ $i -eq 0 ]
			then
				echo "$dwn_d" | gawk '
				{
					gsub("\"ID_DW\"", "\"ID_DW\",\"B5MCODE2\",\"B5MCODE_DW\"")
					gsub("PATH_DW", "URL_DW")
					gsub("\"TYPE_FILE\"", "\"TYPE_FILE\",\"SIZE_MB_FILE\"")
					gsub("\"URL_METADATA\"", "\"URL_METADATA\",\"SRS_NAME\",\"SRS_DES\",\"SRS_URL\"")
					gsub(",\"CODE_DW\"", "")
					print tolower($0)
				}
				' > "$csv"
				dw_fields2=`gawk '
				{
					gsub("\"", "")
					gsub(",", ",b.")
					gsub("id_dw,", "")
					print $0
				}
				' "$csv"`
				let i=$i+1
			else
				IFS=',' read -a dwn_e <<< "$dwn_d"
				dw_dir1=`echo "${dwn_e[5]}" | gawk '{ gsub("\"", ""); print $0 }'`
				dw_dir2=`echo "$dw_dir1" | gawk 'BEGIN { FS="/" } { print $NF }'`
				for dwn_f1 in `ls ${dw_dir1}/*.zip`
				do
					dwn_f2=`echo "$dwn_f1" | gawk 'BEGIN { FS="/" } { print $NF }'`
					code_dw=`echo "$dwn_f2" | gawk 'BEGIN { FS="_" } { print $2 }'`
					dw_url2="${dw_url1}/${dw_dir2}/${dwn_f2}"
					code_dw2=`echo "$dwn_f2" | gawk -v b="${dwn_e[9]}" 'BEGIN { FS="." } { gsub ("\"", "", b); split($1, a, "_"); print b "_" a[1] "_" a[3] }'`
					size_mb=`ls -l ${dwn_f1} | gawk '{ printf "%.2f\n", $5 * 0.000001 }'`
					echo "${i},\"DW_${code_dw}\",\"DW_${code_dw}_${code_dw2}\",${dwn_e[1]},${dwn_e[2]},${dwn_e[3]},${dwn_e[4]},\"${dw_url2}\",${dwn_e[6]},${dwn_e[7]},${size_mb},${dwn_e[8]},\"${dwn_srs1}\",\"${dwn_srs2}\",\"${dwn_srs3}\"" >> "$csv"
					let i=$i+1
				done
			fi
		done
		dwn_g="$(wc -l "$csv" | gawk '{print $1}')"
		if [ $dwn_g -gt 1 ]
		then
			dwn_des="downloads"
			ogr2ogr -f "GPKG" -update "$fgpkg1" "$csv" -nln "${nom}_asoc" -lco DESCRIPTION="$nom $dwn_des"
		fi
		rm "$csv" 2> /dev/null

		# Spatial Views
		# https://gdal.org/drivers/vector/gpkg.html
		ogr2ogr -f "GPKG" -update "$fgpkg1" -sql "create view ${nom}_view as select a.*,${dw_fields2} from $nom a join ${nom}_asoc b on a.b5mcode = b.b5mcode2" "$fgpkg1"
		ogr2ogr -f "GPKG" -update "$fgpkg1" -sql "insert into gpkg_contents (table_name, identifier, data_type, srs_id) values ('${nom}_view', '${nom}_view', 'features', 25830)" "$fgpkg1"
		ogr2ogr -f "GPKG" -update "$fgpkg1" -sql "insert into gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m) values ('${nom}_view', 'geom', 'GEOMETRY', 25830, 0, 0)" "$fgpkg1"
	fi

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
	csv="/tmp/${nom}_tmp.csv"
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
