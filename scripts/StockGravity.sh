#!/bin/bash

# Something like "^TWII" "0050.TW" "1301.TW" "006201.TWO" "^DJI" "^SSEC"
FileName='stock_list.txt'
StockGravity=`pwd`/../src/StockGravity.py

# Making sure that FileName is in Unix format.
dos2unix $FileName

while read LINE
do
	echo $LINE
	python $StockGravity --yahoo $LINE
	#do your stuff here
done < $FileName

mkdir -p html
mv *.html html/

