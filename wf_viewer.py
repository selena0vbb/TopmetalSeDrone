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

    wf = froot["wfTree"]["wf"].array(library="np")[1]
    xscale = float(config["xscale(t)"]) * 1000
    yscale = float(config["yscale(V)"]) * 1000
    print(yscale) 
    print(xscale)
    mv = wf*yscale
    t = xscale * np.arange(0, len(wf), 1)
#    print(wf)
    #print(froot["Header"].keys())

    return wf, mv, t

if __name__ == '__main__':
    fname=sys.argv[1]
    start=time.time()
    wf,mv,t = get_root_wf(fname)
    print(len(wf))
#    end=time.time()
    #print(wf[1] - wf[0])
    plt.plot(t,mv)
    #plt.plot(wf[1])
    plt.show()
