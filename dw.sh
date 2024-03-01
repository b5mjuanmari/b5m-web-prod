#!/bin/bash

f1="/tmp/dw_download_99.csv"
f2="/tmp/dw_download_02.csv"

rm "$f2" 2> /dev/null

gawk '
BEGIN {
	FS = ","
	print "\"B5MCODE2\",\"TYPES_DW\""
}
{
	if (NR > 2) {
		gsub("\"", "")
		fs = sprintf("%.2f", $11/1000000)
		if (fs = "0.00")
			fs = "0.01"
		a03 = $3
		a06 = $3 "|" $6
		a08 = "{@name_eu@:@" $3 "@,@name_es@:@" $4 "@,@name_en@:@" $5 "@,@series_dw@:[{@years@:" $6 ",@b5mcode_dw@:@" $7 "@,@format@:[{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}"
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
			print "\"" a01 "\",\"[" res "\""
			res = ""
		}
		if (a03 != b03 || a01 != $1) {
			if (res == "") {
				res = a08
			} else {
				res = res "]}]}," a08
			}
		} else {
			#print "KK1: " $1, $3, $6, $8 "|" a01, b03, c06, c08 >> "/tmp/zz"
			if ($6 != c06) {
				res = res ",{@years@:" $6 ",@b5mcode_dw@:@" $7 "@,@format@:["
				#if ($8 != c08) {
					res = res "{@format_dw@:@" $8 "@,@url_dw@:@" $9 "@,@file_type_dw@:@" $10 "@,@file_size_mb@:" fs "}"
				#}
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
	print "\"" a01 "\",\"[" res "\""
}
' "$f1" | gawk '
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
			}
		}
	}
	print $0
}
' > "$f2"

exit 0
