#!/bin/bash
#
# Altimetry data from LIDAR in Gipuzkoa
#

# Variables
yd=2017
cs2cs="/usr/local/bin/cs2cs"
gdall="/usr/local/bin/gdallocationinfo"
lidard="/home9/lidar"

if [ "$1" = "" ] || [ "$1" = "-h" ] || [ "$1" = "-help" ] || [ "$1" = "--h" ] || [ "$1" = "--help" ]
then
	echo "Usage: z_gipu [-c x y] [-srs srs_def] [-z type_z] [-l type_lidar] [-y year] [-d debug]"
	echo ""
	echo "Description:"
	echo "-c x y: x and y coordinates of the point to be consulted."
	echo "-srs srs_def: Spatial Reference System. These are supported:"
	echo "              epsg:25830 (default), epsg:4326 and epsg:3857"
	echo "-z type_z: altitude type: o (orthometric, referring to Alicante (default)"
	echo "                          oa (orthometric, referring to Amsterdam [EVRS2002])"
	echo "                          e (ellipsoidal)"
	echo "-l type_lidar: LIDAR type: s (Terrain/Lurra/Suelo) (default)"
	echo "                           v (Surface/Hegaldia/Vuelo)"
	echo "-y year: $yd (default)"
	echo "         2012"
	echo "         2008"
	echo "         2005"
	echo "-d debug: 0 (no, default)"
	echo "          1 (yes)"
	exit 1
fi

IFS=' ' read -a pars <<< "$@"
i=0
while [ $i -lt $# ]
do
	par="${pars[$i]}"
	if [ "$par" = "-c" ]
	then
		let j=$i+1
		let k=$i+2
		coors="${pars[$j]} ${pars[$k]}"
	fi
	if [ "$par" = "-srs" ]
	then
		let j=$i+1
		srs="${pars[$j]}"
	fi
	if [ "$par" = "-z" ]
	then
		let j=$i+1
		z="${pars[$j]}"
	fi
	if [ "$par" = "-l" ]
	then
		let j=$i+1
		l="${pars[$j]}"
	fi
	if [ "$par" = "-y" ]
	then
		let j=$i+1
		yr="${pars[$j]}"
	fi
	if [ "$par" = "-d" ]
	then
		let j=$i+1
		deb="${pars[$j]}"
	fi
	let i=$i+1
done
if [ "$coors" = "" ] || [ "$coors" = " " ]
then
	echo "Coordinates are missing."
	echo
	$0 -h
	exit 1
fi
if [ "$srs" = "" ] || [ "$srs" = " " ]
then
	srs="epsg:25830"
fi
if [ "$z" = "" ] || [ "$srs" = " " ]
then
	z="o"
fi
if [ "$l" = "" ] || [ "$srs" = " " ]
then
	l="s"
fi
if [ "$yr" = "" ] || [ "$srs" = " " ]
then
	yr=$yd
fi
if [ "$deb" = "" ]
then
	deb=0
fi
if [ "$deb" = "1" ]
then
	echo "Debug info:"
	echo "DB debug level: @${deb}@"
	echo "DB coors: @${coors}@"
	echo "DB srs: @${srs}@"
	echo "DB z: @${z}@"
	echo "DB l: @${l}@"
	echo "DB year: @${yr}@"
fi

x="$(echo "$coors" | gawk '{print $1}')"
y="$(echo "$coors" | gawk '{print $2}')"

# Supported SRS: EPSG:4326, EPSG:25830 and EPSG:3857
# (and in regard to older users: EPSG:23030 and EPSG:900913)
if [ "$srs" = "epsg:23030" ] || [ "$srs" = "EPSG:23030" ]
then
	res=`"$cs2cs" +init=epsg:23030 +to +init=epsg:25830 <<-EOF1
	$x $y
	EOF1`
	x2="$(echo "$res" | gawk '{print $1}')"
	y2="$(echo "$res" | gawk '{print $2}')"
elif [ "$srs" = "epsg:4326" ] || [ "$srs" = "EPSG:4326" ]
then
	res=`"$cs2cs" +init=epsg:4326 +to +init=epsg:25830 <<-EOF1
	$x $y
	EOF1`
	x2="$(echo "$res" | gawk '{print $1}')"
	y2="$(echo "$res" | gawk '{print $2}')"
elif [ "$srs" = "epsg:25830" ] || [ "$srs" = "EPSG:25830" ]
then
	x2=$x
	y2=$y
elif [ "$srs" = "epsg:3857" ] || [ "$srs" = "EPSG:3857" ] || [ "$srs" = "epsg:900913" ] || [ "$srs" = "EPSG:900913" ]
then
	res=`"$cs2cs" +init=epsg:3857 +to +init=epsg:25830 <<-EOF1
	$x $y
	EOF1`
	x2="$(echo "$res" | gawk '{print $1}')"
	y2="$(echo "$res" | gawk '{print $2}')"
else
	echo "SRS not supported: $srs"
	exit 1
fi
if [ "$deb" = "1" ]
then
 echo "DB coors calc: @${x2} ${y2}@"
fi

# Calculo altura lidar
if [ "$l" = "s" ] || [ "$l" = "S" ] || [ "$l" = "" ] || [ "$l" = " " ]
then
	if [ $yr -eq 2005 ]
	then
		mapa="suelo2005_2"
	elif [ $yr -eq 2008 ]
	then
		mapa="suelo2008_2"
	elif [ $yr -eq 2012 ]
	then
		mapa="suelo2012_2"
	else
		mapa="suelo2017_2"
	fi
elif [ "$l" = "v" ] || [ "$l" = "V" ]
then
	if [ $yr -eq 2005 ]
	then
		mapa="vuelo2005_2"
	elif [ $yr -eq 2008 ]
	then
		mapa="vuelo2008_2"
	elif [ $yr -eq 2012 ]
	then
		mapa="vuelo2012_2"
	else
		mapa="vuelo2017_2"
	fi
else
	print "LIDAR not supported: $l"
	exit 1
fi
mapa="${lidard}/${mapa}.tif"
z1="$("$gdall" -valonly "$mapa" -geoloc $x2 $y2)"

# Ver si es no data
no_data_val="-340282346638528859811704183484516925440"
if [ "$z1" = "$no_data_val" ] || [ "$z1" = "" ]
then
	z1=-9999
fi

# Calculo geoide (si es necesario)
z2=1
if [ "$z" = "o" ] || [ "$z" = "O" ] || [ "$z" = "" ] || [ "$z" = " " ] || [ "$z1" = "-9999" ]
then
	z2=0
elif [ "$z" = "e" ] || [ "$z" = "E" ]
then
	mapa2="IGEO95"
	#mapa2="REDNAP08"
elif [ "$z" = "oa" ] || [ "$z" = "OA" ]
then
	mapa2="EVRS2002"
else
	print "Altimetry type not supported: $z"
	exit 1
fi
if [ $z2 -ne 0 ]
then
	mapa2="${lidard}/${mapa2}.tif"
	z2="$("$gdall" -valonly "$mapa2" -geoloc $x2 $y2)"
fi

# Z definitiva
if [ "$z2" = "0" ]
then
	zt="$(echo "$z1" | gawk '{printf("%.2f",$1)}')"
else
	if [ "$z" = "oa" ] || [ "$z" = "OA" ]
	then
		zt="$(echo "$z1 $z2" | gawk '{printf("%.2f",$1-$2)}')"
	else
		zt="$(echo "$z1 $z2" | gawk '{printf("%.2f",$1+$2)}')"
	fi
fi

# Invalid values
zt1="$(echo "$zt" | gawk '{if(match($1,"000.000")!=0){print "-9999"}}')"
if [ "$zt" = "" ] || [ "$zt" = "-9999.00" ] || [ "$zt1" = "-9999" ]
then
	zt="-9999"
fi
echo "$zt"

exit 0
