#!/bin/bash
#
# ================================================= #
#  +---------------------------------------------+  #
#  | gpkg2_fnc.sh                                |  #
#  | Funtzioak Geopackageak sortzeko             |  #
#  | Funciones para la generación de Geopackages |  #
#  +---------------------------------------------+  #
# ================================================= #
#

function msg {
	# echo mezua / mensaje
	if [ $crn -le 2 ]
	then
		echo -e "$1"
	fi
	echo -e "$1" >> "$log"
}

function rfl {
  # Eremuak berrizendatu / Renombrar campos
  flist="$(ogrinfo -al -so "$1" "$2" | gawk '
  BEGIN {
    a=0
  }
  {
    if (a == 1 && $1 != "Geometry") print substr($1, 1, length($1)-1)
    if ($1 == "FID") a=1
  }
  ')"
  for fl in $flist
  do
    fl2="$(echo "$fl" | gawk '{print tolower($0)}')"
    ogrinfo -dialect ogrsql -sql "alter table $2 rename column $fl to ${fl}999" "$1" > /dev/null
    ogrinfo -dialect ogrsql -sql "alter table $2 rename column ${fl}999 to $fl2" "$1" > /dev/null
  done
}

function cnx {
	# Kanpoko zerbitzarietarako konexioa akats-egiaztatzearekin
	# Conexión a servidores externos con verificación de error
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
				echo " - Errorea / Error $2 $1 #${3}# "
		else
				sleep 10
		fi
	done
}

function cp_gpk {
	# Datuak kopiatu / Copiar los datos
	tmpg="/tmp/${2}.gpkg"
	fidg="${gpkd}/${2}.gpkg"
	fipg="${gpkp}/${2}.gpkg"

	if [ $1 -eq 1 ] || [ $1 -eq 2 ]
	then
		# Garapenera kopiatu  / Copiar a desarrollo
		ta01="rm \"$tmpg\""
		tb01="$(cnx "${usrd1}@${hstd1}" "ssh" "$ta01")"
		ta02="put \"$tmpg\" \"$tmpg\""
		tb02="$(cnx "${usrd1}@${hstd1}" "sftp" "$ta02")"
		ta03="cd \"$gpkd\";if [ -f \"$tmpg\" ];then sudo rm \"$fidg\";else exit;fi;if [ ! -d \"$gpkd\" ];then sudo mkdir \"$gpkd\";sudo chown -R ${usrd2}:${usrd2} \"$gpkd\";fi;sudo mv \"$tmpg\" \"$fidg\";sudo chown ${usrd2}:${usrd2} \"$fidg\";rm \"$tmpg\""
		tb03="$(cnx "${usrd1}@${hstd1}" "ssh" "$ta03")"
		tbs01="${tb01}${tb02}${tb03}"
		if [ "$tbs01" != "" ]
		then
			msg " - $tbs01\c"
		fi
	fi

	if [ $1 -eq 2 ]
	then
		# Ekoizpenera kopiatu / Copiar a producción
		hstp1_a=("$hstp1a" "$hstp1b")
		for hstp1 in "${hstp1_a[@]}"
		do
			ta04="rm \"$tmpg\""
			tb04="$(cnx "${usrp1}@${hstp1}" "ssh" "$ta04")"
			ta05="put \"$tmpg\" \"$tmpg\""
			tb05="$(cnx "${usrp1}@${hstp1}" "sftp" "$ta05")"
			ta06="cd \"$gpkp\";if [ -f \"$tmpg\" ];then sudo rm \"$fipg\";else exit;fi;if [ ! -d \"$gpkp\" ];then sudo mkdir \"$gpkp\";sudo chown -R ${usrp2}:${usrp2} \"$gpkp\";fi;sudo mv \"$tmpg\" \"$fipg\";sudo chown ${usrp2}:${usrp2} \"$fipg\";rm \"$tmpg\""
			tb06="$(cnx "${usrp1}@${hstp1}" "ssh" "$ta06")"
			tbs02="${tb04}${tb05}${tb08}"
			if [ "$tbs02" != "" ]
			then
				msg " - $tbs02\c"
			fi
		done
	fi
}

function sql_more_info {
	# more_info-a kudeatzeko SQL prozesua / Proceso SQL para gestionar el more_info
	sqlplus -s "$con" <<-EOF1 | gawk \
	-v k_gpk="$k_gpk" \
	-v k_des0="${k_des[0]}" \
	-v k_abs0="${k_abs[0]}" \
	-v k_des1="${k_des[1]}" \
	-v k_abs1="${k_abs[1]}" \
	-v k_des2="${k_des[2]}" \
	-v k_abs2="${k_abs[2]}" \
	-v m_gpk="$m_gpk" \
	-v m_des0="${m_des[0]}" \
	-v m_abs0="${m_abs[0]}" \
	-v m_des1="${m_des[1]}" \
	-v m_abs1="${m_abs[1]}" \
	-v m_des2="${m_des[2]}" \
	-v m_abs2="${m_abs[2]}" \
	-v s_gpk="$s_gpk" \
	-v s_des0="${s_des[0]}" \
	-v s_abs0="${s_abs[0]}" \
	-v s_des1="${s_des[1]}" \
	-v s_abs1="${s_abs[1]}" \
	-v s_des2="${s_des[2]}" \
	-v s_abs2="${s_abs[2]}" \
	'
	BEGIN {
		FS="\",\""
	}
	{
	  if (NR == 1) {
			getline
			gsub("MORE_INFO", "MORE_INFO_EU")
			print $0",\"MORE_INFO_ES\",\"MORE_INFO_EN\""
		} else {
			a0=$2
			a1=$2
			a2=$2
			gsub("ZZ_K_FTN", k_gpk, a0)
			gsub("ZZ_K_DES", k_des0, a0)
			gsub("ZZ_K_ABS", k_abs0, a0)
			gsub("ZZ_K_FTN", k_gpk, a1)
			gsub("ZZ_K_DES", k_des1, a1)
			gsub("ZZ_K_ABS", k_abs1, a1)
			gsub("ZZ_K_FTN", k_gpk, a2)
			gsub("ZZ_K_DES", k_des2, a2)
			gsub("ZZ_K_ABS", k_abs2, a2)
			gsub("ZZ_M_FTN", m_gpk, a0)
			gsub("ZZ_M_DES", m_des0, a0)
			gsub("ZZ_M_ABS", m_abs0, a0)
			gsub("ZZ_M_FTN", m_gpk, a1)
			gsub("ZZ_M_DES", m_des1, a1)
			gsub("ZZ_M_ABS", m_abs1, a1)
			gsub("ZZ_M_FTN", m_gpk, a2)
			gsub("ZZ_M_DES", m_des2, a2)
			gsub("ZZ_M_ABS", m_abs2, a2)
			gsub("ZZ_S_FTN", s_gpk, a0)
			gsub("ZZ_S_DES", s_des0, a0)
			gsub("ZZ_S_ABS", s_abs0, a0)
			gsub("ZZ_S_FTN", s_gpk, a1)
			gsub("ZZ_S_DES", s_des1, a1)
			gsub("ZZ_S_ABS", s_abs1, a1)
			gsub("ZZ_S_FTN", s_gpk, a2)
			gsub("ZZ_S_DES", s_des2, a2)
			gsub("ZZ_S_ABS", s_abs2, a2)
			print $1"\",\""a0",\""a1",\""a2
		}
	}
	' > "$1"
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

	${2};

	exit;
	EOF1
}

function sql_more_info2 {
	# more_info-a JSON moduan jartzeko SQL eta GAWK prozesua
	# Proceso SQL y GAWK para poner el more_info en forma de JSON
	sqlplus -s "$con" <<-EOF1 | gawk \
	'
	BEGIN {
		FS = "\",\""
		OFS = "\",\""
	}
	{
		# Bikoiztutako informazioa ezabatu
		if (NR <=2 ) {
			getline
		} else {
			for (i = 3; i <= NF; i++) {
				i0 = split($i, i1, "|")
				$i = ""
				i2 = ""
				for (j = 1; j <= i0; j++) {
					gsub("\"", "", i1[j])
					if (i2 != i1[j])
						$i = $i "|" i1[j]
					i2 = i1[j]
				}
				$i = substr($i, 2, length($i)-1)
			}
			gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\","); gsub(",,", ",\"\",")
			print $0 "\""
		}
	}
	' | gawk \
	'
	BEGIN {
		FS = "\",\""
		OFS = "\",\""
		print "\"B5MCODE","MORE_INFO_EU","MORE_INFO_ES","MORE_INFO_EN\""
	}
	{
		a11 = "["
		a21 = a11
		a31 = a11
		$NF = substr($NF, 1, length($NF)-1)
		i = 2
		j = 1
		for (i = 2; i <= NF; i++ + i++ + i++ + i++) {
			i2 = $(i + 1); i3 = $(i + 2); i4 = $(i + 3);
			split($i, i1, "|")
			i2c = split(i2, i2a, "|")
			i3c = split(i3, i3a, "|")
			i4c = split(i4, i4a, "|")
			if (j > 1)
				a1 = ","
			else
				a1 = ""
			a1 = a1 "{#featuretypename#:#ZZ_FTN#,#description#:#ZZ_DES_EU#,#abstract#:#ZZ_ABS_EU#,"
			a1 = a1 "#numberMatched#:"i2c","
			a1 = a1 "#features#:["
			for (k = 1; k <= i2c; k++) {
				if (k > 1)
					a1 = a1 ","
				a1 = a1 "{#b5mcode#:#"i2a[k]"#,"
				a1 = a1 "#name_eu#:#"i3a[k]"#,"
				a1 = a1 "#name_es#:#"i4a[k]"#}"
			}
			a1 = a1 "]"
			if (i + 3 != NF)
				a1 = a1 "}"
			gsub("#", "\x27", a1)
			if (i2c == 0)
				a1 = ""
			a2 = a1; a3 = a1
			gsub("_EU", "_ES", a2); gsub("_EU", "_EN", a3)
			gsub("ZZ_FTN", i1[1], a1); gsub("ZZ_DES_EU", i1[2], a1); gsub("ZZ_ABS_EU", i1[5], a1)
			gsub("ZZ_FTN", i1[1], a2); gsub("ZZ_DES_ES", i1[3], a2); gsub("ZZ_ABS_ES", i1[6], a2)
			gsub("ZZ_FTN", i1[1], a3); gsub("ZZ_DES_EN", i1[4], a3); gsub("ZZ_ABS_EN", i1[7], a3)
			a11 = a11 "" a1
			a21 = a21 "" a2
			a31 = a31 "" a3
			gsub("\\[,", "[", a11); gsub("\\[,", "[", a21); gsub("\\[,", "[", a31)
			j++
		}
		print $1, a11 "}]", a21 "}]", a31 "}]\""
	}
	' | gawk \
	'
	{
		gsub("\\]}}\\]", "]}]")
		print $0
	}
	' > "$1"
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

	${2};

	exit;
	EOF1
}

function sql_poi {
	# POIak kudeatzeko SQL prozesua / Proceso SQL para gestionar los POIs
	sqlplus -s "$con" <<-EOF1 | gawk '
	{
	gsub("poi_null","")
	if (NR != 1) {
		if (NR == 2)
			print tolower($0)
		else
			print $0
	}
	}
	' > "$1"
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

	${2};

	exit;
	EOF1
}

function dw_types_list {
	# Deskargen motak zerrendatu
	x1=530000
	y1=4740000
	x2=610000
	y2=4820000
	dw_wkt="polygon ((${x1} ${y1}, ${x2} ${y1}, ${x2} ${y2}, ${x1} ${y2}, ${x1} ${y1}))"
	csv01="/tmp/${dw_fs}_types.csv"
	rm "$csv01" 2> /dev/null
	sqlplus -s "$con" <<-EOF1 | gawk -v a="$dw_wkt" '
	BEGIN {
		FS = ","
	}
	{
		if (NR == 1) {
			getline
			getline
		}
		gsub("\"","")
		res = res "{@dw_type_id@:" $1 ",@dw_name_eu@:@" $2 "@,@dw_name_es@:@" $3 "@,@dw_name_en@:@" $4 "@},"
	}
	END {
		res = substr(res, 1, length(res)-1)
		res = "[" res "]"
		gsub("@", "\047", res)
		print "\"dw_types_id\",\"dw_types\",\"geom\""
		print "1,\"" res "\",\"" a "\""
	}
	' > "$csv01"
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

	${dw_sql_01_05};

	exit;
	EOF1
	ogr2ogr -f "GPKG" -update -s_srs "EPSG:25830" -t_srs "EPSG:25830" "$f01" "$csv01" -nln "${dw_gpk}_types" -lco DESCRIPTION="$des01 types" -oo GEOM_POSSIBLE_NAMES="geom" -oo KEEP_GEOM_COLUMNS="no"
	rm "$csv01" 2> /dev/null
}

function dw_scan {
	# Deskarga fitxategien tamainak eskaneatu
	csv01="/tmp/${dw_fs}.csv"
	ctl01="/tmp/${dw_fs}.ctl"
	log01="/tmp/${dw_fs}.log"
	bad01="/tmp/${dw_fs}.bad"
	rm "$csv01" 2> /dev/null
	dw_list=`sqlplus -s "$con" <<-EOF1 | gawk '
	{
		if (NR > 1)
			print $0
	}
	'
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

	${dw_sql_02};

	exit;
	EOF1`

	i=1
	j=1
	while read a
	do
		b=`echo "$a" | gawk '{ gsub("\"", ""); print $0 }'`
		IFS=',' read -a c <<< "$b"
		IFS=';' read -a d1 <<< "${c[6]}"
		IFS=';' read -a d2 <<< "${c[7]}"
		IFS=';' read -a d3 <<< "${c[9]}"
		IFS=';' read -a d4 <<< "${c[10]}"
		k=0
		for e in "${d1[@]}"
		do
			if [ $i -gt 1 ]
			then
				if [ "${d2[$k]}" = "" ]
				then
					d2z="${d2[$k-1]}"
				else
					d2z="${d2[$k]}"
				fi
				while read f
				do
					IFS=' ' read -a g <<< "$f"
					dw_grid=`echo "${g[8]} ${d4}" | gawk '{ b = split($1, a , "/"); c = substr($2, 1, 1); d = substr($2, 2, 2); split(a[b], e, d); print e[c] }'`
					if [ "${c[4]}" = "photo" ]
					then
						dw_grid="${c[5]}${c[15]}_${dw_grid}"
					fi
					echo "${j},${c[0]},${c[1]},\"${dw_grid}\",\"${d3[$k]}\",${g[4]}" >> "$csv01"
					let j=$j+1
				done <<- EOF3
				`ls -l ${e}/${d2z} 2> /dev/null`
				EOF3
			fi
			let k=$k+1
		done
		let i=$i+1
	done <<- EOF1
	"$dw_list"
	EOF1

	# Deskarga fitxategiak kargatu
	sqlplus -s "$con" <<-EOF1 > /dev/null

	${dw_sql_03};

	exit;
	EOF1
	dw_fs_list=`sqlplus -s "$con" <<-EOF1 | gawk '
	{
		gsub("\"", "")
		if (NR > 2) {
			if (NR > 3)
				printf(",")
			printf("%s",tolower($0))
		}
	}
	'
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

	${dw_sql_04};

	exit;
	EOF1`
	rm "$ctl01" 2> /dev/null
	echo "load data" > "$ctl01"
	echo "infile '${csv01}'" >> "$ctl01"
	echo "badfile '${bad01}'" >> "$ctl01"
	echo "into table ${ora_sch_01}.$dw_fs" >> "$ctl01"
	echo "fields terminated by \",\" optionally enclosed by '\"'" >> "$ctl01"
	echo "( ${dw_fs_list} )" >> "$ctl01"
	rm "$log01" 2> /dev/null
	rm "$bad01" 2> /dev/null
	sqlldr "$con" control="$ctl01" log="$log01" > "/dev/null" 2> "/dev/null"
	if [ -f "$bad01" ]
	then
		msg " (err#1)\c"
		bad02=`echo "$log" | gawk 'BEGIN { FS = "." }{print $1 ".bad" }'`
		csv02=`echo "$log" | gawk 'BEGIN { FS = "." }{print $1 ".csv" }'`
		cp "$bad01" "$bad02"
		cp "$csv01" "$csv02"
		rm "$bad01" 2> /dev/null
	fi
	rm "$ctl01" 2> /dev/null
	rm "$log01" 2> /dev/null
	rm "$csv01" 2> /dev/null
	sqlplus -s "$con" <<-EOF1 > /dev/null

	${dw_sql_05};

	exit;
	EOF1
}

function dw_types_grid {
	# Deskargen motak
	dw_tp_grd=`sqlplus -s ${con} <<-EOF1 | gawk '
	{
		if (NR > 1)
			printf(",")
		printf("\"%s\"", $1)
	}
	END {
		printf("\n")
	}
	'
	set feedback off
	set linesize 32767
	set trim on
	set pages 0

	${dw_sql_06};

	exit;
	EOF1`
	echo "$dw_tp_grd"
}

function dw_data {
	# Datuen taula sortu
	dw_sql_07_1=`echo "$dw_sql_07" | sed "s/ZZ_GRID_DW/$1/g"`
	sqlplus -s "$con" <<-EOF1 | gawk '
	BEGIN {
		FS = ","
		print "\"B5MCODE2\",\"ID_TYPES_DW\",\"TYPES_DW\""
	}
	{
		if (NR > 2) {
			gsub("\"", "")

			# Fitxategiaren tamaina
			fs = sprintf("%.2f", $11/1000000)
			if (fs == "0.00")
				fs = "0.01"

			# Urteak
			split($6, y1, "-")
			y2 = ""
			for (i in y1) {
				if (i != 1)
					y2 = y2 ","
				if (length(y1[i]) == 2)
					y1[i] = y3 "" y1[i]
				y2 = y2 "" y1[i]
				y3 = substr(y1[1], 1, 2)
			}
			yrs = "[" y2 "]"

			if (match(res2, "#" $16 "#" ) == 0 )
				res2 = res2 "#" $16 "#"
			a03 = $3
			a06 = $3 "|" $6
			a08 = "{@dw_type_id@:@" $16 "@,@name_eu@:@" $3 "@,@name_es@:@" $4 "@,@name_en@:@" $5 "@,@series_dw@:[{@years@:" yrs ",@b5mcode_dw@:@" $7 "@,@format@:[{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}"
	    mdt = "@metadata@:{@url@:@" $12 "@,@owner_eu@:@" $13 "@,@owner_es@:@" $14 "@,@owner_en@:@" $15 "@}"
			a08 = a08 "]," mdt
			if (a01 != $1 && a01 != "") {
				res = res "}]"
				gsub("}]}]}," ,"}}]},", res)
				if (substr(res, length(res)-5, 5) != "}]}]}")
					res = res "}]"
				gsub("}}}]}]" ,"}}]}]", res)
				gsub("@},{@years@", "@}},{@years@", res)
				gsub("@", "\047", res)
				gsub("##", "#", res2)
				gsub("#", "|", res2)
				print "\"" a01 "\",\"" res2 "\",\"[" res "\""
				res = ""
				res2 = ""
			}
			if (a03 != b03 || a01 != $1) {
				if (res == "")
					res = a08
				else
					res = res "]}]}," a08
			} else {
				if ($6 != c06) {
					res = res ",{@years@:" yrs ",@b5mcode_dw@:@" $7 "@,@format@:["
					res = res "{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}"
				} else if ($7 != c07) {
	    		mdt = "@metadata@:{@url@:@" $12 "@,@owner_eu@:@" $13 "@,@owner_es@:@" $14 "@,@owner_en@:@" $15 "@}"
					if (substr(res, length(res)-1, 2) != "}}")
					 res = res "}"
					res = res ",{@years@:" yrs ",@b5mcode_dw@:@" $7 "@,@format@:["
					res = res "{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}]," mdt "}"
				} else {
					if ($8 != c08) {
	    			mdt = "@metadata@:{@url@:@" $12 "@,@owner_eu@:@" $13 "@,@owner_es@:@" $14 "@,@owner_en@:@" $15 "@}"
						res = res ",{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}]," mdt "}"
					}
				}
			}
			a01 = $1
			b03 = a03
			b06 = a06
			b08 = a08
			c06 = $6
			c07 = $7
			c08 = $8
		}
	}
	END {
		res = res "}]"
		gsub("}]}]}," ,"}}]},", res)
		if (substr(res, length(res)-5, 5) != "}]}]}")
			res = res "}]"
		gsub("}}}]}]" ,"}}]}]", res)
		gsub("@", "\047", res)
		gsub("##", "#", res2)
		gsub("#", "|", res2)
		print "\"" a01 "\",\"" res2 "\",\"[" res "\""
	}
	' | gawk '
	# Behar ez den metadatua ezabatu
	BEGIN {
		FS = "\047"
	}
	{
		for (i = 1; i <= NF; i++) {
			if ($i == "format_dw") {
				j = i-14
				if (substr($j, 1, 4) == "http") {
					j2 = i-12
					j3 = i-10
					j4 = i-8
					j5 = i-6
					j6 = i-4
					j7 = i-2
					gsub("],\047metadata\047:{\047url\047:\047" $j "\047,\047" $j2 "\047:\047" $j3 "\047,\047" $j4 "\047:\047" $j5 "\047,\047" $j6 "\047:\047" $j7 "\047},{\047format_dw\047", ",{\047format_dw\047")
					gsub("],\047metadata\047:{\047url\047:\047" $j "\047,\047" $j2 "\047:\047" $j3 "\047,\047" $j4 "\047:\047" $j5 "\047,\047" $j6 "\047:\047" $j7 "\047}},{\047format_dw\047", ",{\047format_dw\047")
				}
			}
		}
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

	${dw_sql_07_1};

	exit;
	EOF1
}
