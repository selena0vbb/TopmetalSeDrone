import numpy as np
import matplotlib.pyplot as plt

import sys
import time
import uproot

def get_waveforms(fname, binary_file=True):
    '''
        Used to oscilloscope .dat files from TopmetalSeDrone
        Output in (mV, ms)
    '''

    dat = np.fromfile(fname,dtype='uint8')#,skiprows=7, encoding='bytes')
    print(dat) 
    with open(fname,mode='rb') as f:
       
        header = f.readline().decode('ascii')
        print(str(header))
        header_vals = header.split(';')
        tscale = float(header_vals[0].split(':')[-1]) * 1000 #ms
        vscale = float(header_vals[1].split(':')[-1]) * 1000 #mV
    
    v = dat * vscale
    return v, tscale

def get_root_wf(fname):
    froot = uproot.open(fname)
    config = froot["Header"]

    wf = froot["wfTree"]["wf"].array(library="np")
#    print(wf)
    #print(froot["Header"].keys())

    return wf

if __name__ == '__main__':
    fname=sys.argv[1]
    start=time.time()
    wf = get_root_wf(fname)
    end=time.time()
    print(end-start)
    plt.plot(wf[0])
    plt.show()
