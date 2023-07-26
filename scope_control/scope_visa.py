import pyvisa
import matplotlib.pyplot as plt
import numpy as np
from struct import unpack

def to_xy(ADC_data, xyscale):
    volts = (ADC_data-xyscale[0])*xyscale[1]
    time = np.arange(0, xyscale[0] * len(volts), xyscale[0])
    
    return time, volts
    


class tek_visa():
    def __init__(self):
        rm = pyvisa.ResourceManager('@py')
        self.scope = rm.open_resource('USB0::1689::932::C040658::0::INSTR')

        print(self.scope.query('*IDN?'))

    def get_preamble(self):
        self.preamble = self.scope.query('WFMOUTPRE?')
        print(self.preamble)
       
    def get_scale(self):
        xscale = float(self.scope.query('WFMPRE:XINCR?'))
        yscale = float(self.scope.query('WFMPRE:YMULT?'))
        yoff = float(self.scope.query('WFMPRE:YOFF?'))     

        return xscale, yscale,yoff

    def get_waveform(self, ch_num):
        self.scope.write('DATA:SOU CH%i' %ch_num)
        
       
        self.scope.write('DATA:WIDTH 1')
        self.scope.write('DATA:ENC RPB')

        self.scope.write('DATA:STOP 125000') #sets max data length
        self.scope.write('CURVE?')
        data = self.scope.read_raw()
        
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
    
        return ADC_wave 

if __name__ == '__main__':
    scope = tek_scope();
    scope.get_preamble()

    ADC_wave = scope.get_waveform(1)
    xyscale = scope.get_scale()
    time,volts= to_xy(ADC_wave,xyscale)

    plt.plot(time, volts)
    plt.show()


