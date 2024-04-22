#!/bin/bash
#
# orto_fmts.sh - Zerrendatu eta egin ECW edo JPG bat falta den orto batean
#

# Inguruneko aldagaiak
export ORACLE_HOME="/opt/oracle/instantclient"
export LD_LIBRARY_PATH="$ORACLE_HOME"
export PATH="/opt/miniconda3/bin:/opt/LAStools/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/opt/oracle/instantclient:/opt/bin:/snap/bin"
export HOME="/home/lidar"

# Aldagaiak
con="b5mweb_nombres/web+@//exploracle:1521/bdet"
dir="${HOME}/SCRIPTS/GPKG"
scr=`echo "$0" | gawk 'BEGIN { FS = "/" } { print $NF }'`
oin=`echo "$scr" | gawk 'BEGIN {FS = "." } { print $1 }'`
logd="${dir}/log"
log=`echo "$scr" | gawk -v logd="$logd" 'BEGIN { FS="/" } { split($NF, a, "."); print logd "/" a[1] ".log" }'`
rm "$log" 2> /dev/null
tmp01="/tmp/${oin}_01.tmp"
tmp02="/tmp/${oin}_02.tmp"

# Funtzioak
function ecw2jpg {
	echo "ecw2jpg: $1"
	ef1="$1"

	ef2=`echo "$ef1" | gawk '{ gsub("ecw", "jpg"); print $0 }'`
	if [ ! -f "$ef2" ]
	then
		ea=`unzip -o "$ef1"`
		eb=`echo "$ea" | gawk 'END { print $2 }'`
		ec=`echo "$eb" | gawk 'BEGIN { FS = "." } { print $1 }'`
		ed="${ec}.jpg"
		ee="${ec}.jgw"
		ef="${ec}.wld"
		eg="${ec}.jpg.aux.xml"
		rm "$ed" 2> /dev/null
		gdal_translate -of JPEG -co "WORLDFILE=YES" "$eb" "$ed"
		rm "$ee" 2> /dev/null
		mv "$ef" "$ee"
		rm "$ef2" 2> /dev/null
		zip -9 "$ef2" "$ed" "$ee"
		rm "$eb" 2> /dev/null
		rm "$ed" 2> /dev/null
		rm "$ee" 2> /dev/null
		rm "$ef" 2> /dev/null
		rm "$eg" 2> /dev/null
	fi
}

function jpg2ecw {
	echo "jpg2ecw: $1"
	jf1="$1"

	jf2=`echo "$jf1" | gawk '{ gsub("jpg", "ecw"); print $0 }'`
	if [ ! -f "$jf2" ]
	then
		ja=`unzip -o "$jf1"`
		jb1=`echo "$ja" | gawk '{ if (NR == 2) { print $2 } }'`
		jb2=`echo "$ja" | gawk 'END { print $2 }'`
		jc=`echo "$jb1" | gawk 'BEGIN { FS = "." } { print $1 }'`
		jd="${jc}.ecw"
		rm "$jd" 2> /dev/null
		gdal_translate -of ECW "$jb1" "$jd"
		rm "$jf2" 2> /dev/null
		zip -9 "$jf2" "$jd"
		rm "$jb1" 2> /dev/null
		rm "$jb2" 2> /dev/null
		rm "$jd" 2> /dev/null
	fi
}

# Zerrenda
a=`sqlplus -s ${con} <<-EOF
set feedback off
set linesize 32767
set trim on
set pages 0

select unique path_dw
from b5mweb_nombres.dw_list
where id_type=1
order by path_dw;

exit;
EOF`

for b in `echo "$a"`
do
	c=`echo "$b" | gawk 'BEGIN { FS = "/" } { split($NF, a, "_"); print substr(a[1], 2, length(a[1])-1) }'`
	echo "$b - $c"
	d1="${c}_ecw_etrs89"
	d2="${c}_jpg_etrs89"
	e1=`ls ${b}/${d1} | wc -l `
	e2=`ls ${b}/${d2} | wc -l `
	echo "$d1 - $e1"
	echo "$d2 - $e2"
	f1=`ls ${b}/${d1} | gawk '{ gsub("_ecw.zip", ""); print $0 }'`
	f2=`ls ${b}/${d2} | gawk '{ gsub("_jpg.zip", ""); print $0 }'`
	rm "$tmp01" 2> /dev/null
	rm "$tmp02" 2> /dev/null
	ls ${b}/${d1} | gawk '{ gsub("_ecw.zip", ""); print $0 }' > "$tmp01"
	ls ${b}/${d2} | gawk '{ gsub("_jpg.zip", ""); print $0 }' > "$tmp02"
	g=`diff "$tmp01" "$tmp02" | gawk '
	{
		if ($1 == "<") {
			print $2 ";1"
		} else if ($1 == ">")
			print $2 ";2"
	}
	'`
	for h in `echo "$g"`
	do
		IFS=';' read -a i <<< "$h"
		if [ ${i[1]} -eq 1 ]
		then
			ecw2jpg ${b}/${d1}/${i[0]}_ecw.zip
		elif [ ${i[1]} -eq 2 ]
		then
			jpg2ecw ${b}/${d2}/${i[0]}_jpg.zip
		fi
	done
	rm "$tmp01" 2> /dev/null
	rm "$tmp02" 2> /dev/null
done

exit 0
