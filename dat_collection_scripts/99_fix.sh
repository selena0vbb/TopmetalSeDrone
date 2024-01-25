#!/bin/bash
#
echo "Performing a Calibration of Pixels"

cp config/Config.ini config/LA_calib_config.ini
#sed -i 's/LA_pxl_num = */LA_pxl_num-hereh/' config/LA_calib_config.ini

for i in {0..99}
do
#	if [[ $i%3 -eq 0 ]]
#	then
#		continue
#	else

#		echo "Setting Pixel ${i}"
#	fi
	sed -i "s/LA_pxl_num =.*/LA_pxl_num = ${i}99/" config/LA_calib_config.ini
	
	python3.8 main.py -id 2 -sp 20 -o LA_pixel${i}99.root -config config/LA_calib_config.ini
done
