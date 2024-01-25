import numpy as np
import uproot
import matplotlib.pyplot as plt
from numba import jit
import time
'''
	File containing functions related to converting the pixel-scan video output to an image

'''
SCAN_FREQ = 1 #MHz
SAMPL_FREQ  = 62.5 #MHz

PIX_SAMPLS = SAMPL_FREQ/SCAN_FREQ #number of samples per pixel

def get_trigger_loc(trigger_video):
	#gets start of frame
	trigger_loc = np.argmax(np.diff(trig[0:500000])) #finds location of largest jump in the signal
	
	return trigger_loc
@jit(nopython=True)
def compute_frame(video_out, start, settling_time = 20, read_time = 30):
	num_samples = int(10000 * PIX_SAMPLS)

	row_53_loc = int(5300 * PIX_SAMPLS)
	row_54_loc = int(5400 * PIX_SAMPLS)

	if PIX_SAMPLS %1 ==0:
		whole_samples = True
	else:
		whole_samples  = False
	total_samples = 0
	pix_vals = np.empty(10000)
	for i in np.arange(0, 10000, 1):
	
		if whole_samples:
			break
		else:
			if i  % 2 == 0:
				pix_region = video_out[start+total_samples: start + total_samples + 62]
				total_samples += 62
			else:
				pix_region = video_out[start+total_samples:start+total_samples +63]
				total_samples += 63
			pix_vals[i] = np.average(pix_region[settling_time: settling_time + read_time])
		
		if i >= 5300 and i < 5400:#Disconnected Row
			pix_vals[i] = np.nan
		
	frame = np.reshape(pix_vals, (100,100))

	return frame 


if __name__ == '__main__':
	fname = '../../Tek_Scope/1MHz_baseline.npy'
	dat = np.load(fname)

	t = dat[:,0] * 1E6
	vout = dat[:,1]
	trig = dat[:,2] * 1E-2
	
	start = get_trigger_loc(trig)
#	plt.plot(trig[start:])
	start_time = time.time()
	baseline =	compute_frame(vout,start)
	end_time = time.time()
	print(end_time-start_time)
	
	fname = '../../Tek_Scope/1MHz_light.npy'
	dat = np.load(fname)

	t = dat[:,0] * 1E6
	vout = dat[:,1]
	trig = dat[:,2] * 1E-2

	start_time = time.time()
	frame =	compute_frame(vout,start)
	end_time = time.time()
	print(end_time-start_time)
	
	im = plt.imshow(frame-baseline)
	plt.show()

