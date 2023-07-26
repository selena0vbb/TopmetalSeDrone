import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('tmse_control/')
sys.path.append('scope_control/')
import scope_visa as svi
import DAC_control


if __name__ == '__main__':

    scope = svi.tek_visa()
    
    dac_device = DAC_control.DAC8568()
    dac_device.set_internal_ref()

    #set_config




    #read waveforms

