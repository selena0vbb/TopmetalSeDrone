#!/bin/bash
#
echo "Performing a Calibration of Pixels, NB1"

cp config/Config.ini config/SA_calib_config.ini
#sed -i 's/LA_pxl_num = */LA_pxl_num-hereh/' config/LA_calib_config.ini

#random ints

for pix in {4..5..3}
do
	echo $pix	
	sed -i "s/SA_pxl_num =.*/SA_pxl_num = ${pix}/" config/SA_calib_config.ini
	
	for i in {0..9}
	do
	#	if [[ $i%3 -eq 0 ]]
	#	then
	#		continue
	#	else

	#		echo "Setting Pixel ${i}"
	#	fi
		echo 1.$i
		sed -i "s/ch_1 =.*/ch_1 = 1.${i}/" config/SA_calib_config.ini
		
		python3.8 main.py -id 2 -sp 100 -o pixel${pix}_1${i}00.root -config config/SA_calib_config.ini
	done

	for i in {0..4}
	do
	#	if [[ $i%3 -eq 0 ]]
	#	then
	#		continue
	#	else

	#		echo "Setting Pixel ${i}"
	#	fi
		echo 2.$i
		sed -i "s/ch_1 =.*/ch_1 = 2.${i}/" config/SA_calib_config.ini
		
		python3.8 main.py -id 2 -sp 100 -o pixel${pix}_2${i}00.root -config config/SA_calib_config.ini
	done
done
