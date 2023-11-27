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
    if (a == 1) print substr($1, 1, length($1)-1)
    if ($1 == "Geometry") a=1
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
