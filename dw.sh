#!/bin/bash

f1="/tmp/dw_download_01.csv"
f2="/tmp/dw_download_02.csv"
f3="/tmp/dw_download_02.json"

rm "$f2" 2> /dev/null
gawk '
BEGIN {
	FS = ","
	print "\"B5MCODE2\",\"TYPES_DW\""
}
{
	fs = sprintf("%.2f", $11/1000000)
	gsub("\"", "")
	if (NR > 2) {
		a03 = $3
		a06 = $3 "|" $6
		a08 = "{#name_eu#:#" $3 "#,#name_es#:#" $4 "#,#name_en#:#" $5 "#,#series_dw#:[{#years#:" $6 ",#b5mcode_dw#:#" $7 "#,#format#:[{#format_dw#:#" $8 "#,#url_dw#:#" $9 "#,#file_type_dw#:#" $10 "#,#file_size_mb#:" fs "}"
		if (a01 != $1 && a01 != "") {
			res = res "]}]"
			gsub("#", "\047", res)
			print "\"" a01 "\",\"[" res "\""
			res = ""
		}
		if (a03 != b03 ) {
			if (res == "") {
				res = a08
			} else {
				res = res "]}]}," a08
			}
		} else {
			if ($6 != c06) {
				res = res ",{#years#:" $6 ",#b5mcode_dw#:#" $7 "#,#format#:["
				if ($8 != c08) {
					res = res "{#format_dw#:#" $8 "#,#url_dw#:#" $9 "#,#file_type_dw#:#" $10 "#,#file_size_mb#:" fs "}"
				}
			} else {
				if ($8 != c08) {
					res = res ",{#format_dw#:#" $8 "#,#url_dw#:#" $9 "#,#file_type_dw#:#" $10 "#,#file_size_mb#:" fs "}]}"
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
	gsub("#", "\047", res)
	print "\"" a01 "\",\"[" res "]}]\""
}
' "$f1" > "$f2"

# JSON
rm "$f3" 2> /dev/null
gawk '
BEGIN {
	FS = "\""
}
{
	if (NR > 1) {
		print $4
		exit
	}
}
' "$f2" | sed "
s/'/\"/g
" > "$f3"

exit 0
