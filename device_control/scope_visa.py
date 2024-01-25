import pyvisa
import matplotlib.pyplot as plt
import numpy as np
from struct import unpack
import time
def to_xy(ADC_data, xyscale):
    volts = (ADC_data-xyscale[0])*xyscale[1]
    time = np.arange(0, xyscale[0] * len(volts), xyscale[0])
    
    return time, volts
    
class rigol_visa():
    def __init__(self):
        rm = pyvisa.ResourceManager('@py')

       # self.scope = rm.open_resource('USB0::6833::1301::MS5A223404106::0::INSTR')
        self.scope = rm.open_resource('TCPIP::10.95.99.71::INSTR')
    def get_preamble(self):
        return '0'
    def get_scale(self):
        xscale = float(self.scope.query(':WAV:XINC?'))
        yscale = float(self.scope.query(':WAV:YINC?'))
        yoff = float(self.scope.query(':WAV:YOR?'))

        return xscale, yscale, yoff
    def waveform_prep(self):
        self.scope.write(':ACQ:MDEP 100k')
        self.scope.write(':WAV:SOUR CHAN1')
        self.scope.write(':WAV:MODE RAW')
        self.scope.write(':WAV:FORM BYTE')
        self.scope.write(':WAV:STOP 80000')
        print(self.scope.query(':ACQ:MDEP?')) 
        self.scope.chunk_size = 100012 
    
    def record_wfs(self,num=25):
        self.scope.write('REC:ENAB ON')
        self.scope.write('REC:FRAM %i' %num)
        self.scope.write('REC:STAR ON')

    def get_rec_wf(self, acq_num):
        self.scope.write(':WAV:SOUR CHAN1')
        self.scope.write(':WAV:MODE RAW')
        self.scope.write(':WAV:FORM BYTE')
        self.scope.write(':WAV:STOP 80000')

        self.scope.write(':REC:CURR ' + str(acq_num))
        self.scope.write(':WAV:DATA?')
        data = self.scope.read_raw()
        print(len(data))
        ADC_wave = np.array(unpack('%iB' % len(data),data))
        return ADC_wave
    def get_waveform(self, ch_num = 1):
        self.waveform_prep()       
        self.scope.write(':REC:CURR 1')
        self.scope.write(':WAV:DATA?')
        data = self.scope.read_raw()
        self.scope.write(':REC:CURR 3')
        self.scope.write(':WAV:DATA?')
        data = self.scope.read_raw()

#        if len(data) == 12:
#            data = self.scope.read_raw()
#        data = self.scope.read_raw()
#        print(data)
        #data = self.scope.query(':WAV:DATA?')
        #
        t3 = time.time()
        print('\n' + str(len(data)))
        #while len(data) <10000:
        #    print(len(data))
        #    self.waveform_prep()
        #    self.scope.write(':WAV:DATA?')
        #    data = self.scope.read_raw()
               
        #headerlen = 2 + int(data[1])
        #print(headerlen)
        #header = data[:headerlen]
        #ADC_wave_b = data[headerlen:-1]
        ADC_wave = np.array(unpack('%iB' % len(data),data))
        #print(list(ADC_wave))
        #plt.plot(ADC_wave)
        #plt.show()
        #return ADC_wave, ADC_wave_b
        return ADC_wave, [1]
class tek_visa():
    def __init__(self):
        rm = pyvisa.ResourceManager('@py')
        
       # self.scope = rm.open_resource('USB0::1689::932::C040658::0::INSTR')
        #self.scope = rm.open_resource('USB0::6833::1301::MS5A223404106::0::INSTR')
        self.scope = rm.open_resource('TCPIP::10.95.99.119::INSTR')
        print(self.scope.query('*IDN?'))

    def get_preamble(self):
        self.preamble = self.scope.query('WFMOUTPRE?')
        print(self.preamble)
       
    def get_scale(self):
        #self.scope.write('DATA:SOU CH1')
        xscale = float(self.scope.query('WFMPRE:XINC?'))
        yscale = float(self.scope.query('WFMPRE:YMU?'))
        yoff = float(self.scope.query('WFMPRE:YOFF?'))     
        print(self.scope.query('WFMO:YZEro?'))
        print(self.scope.query('WFMO:YOFf?'))
        return xscale, yscale,yoff

        
    def get_FastFrames(self):
        
        start=time.time()
        time.sleep(2)
        num_f = 20
        self.scope.write('ACQ:STATE ON')
        while (float(self.scope.query('ACQ:STATE?')) == 1):
            continue
        ch_num=1
        self.scope.write('DATA:SOU CH%i' %ch_num)
        self.scope.chunk_size = 1260000 
       
        self.scope.write('DATA:WIDTH 1')
        self.scope.write('DATA:ENC SRPB')

        self.scope.write('DATA:STOP 10000') #sets max data length

        self.scope.write('CURVE?')
   

        data = self.scope.read_raw()
        print(len(data)/num_f)
        t3 = time.time()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        print(headerlen)
        ADC_wave_b = data[headerlen:-1]
        ADC_wave_b = data
        
        ADC_wave = np.array(unpack('%iB' % (len(ADC_wave_b)),ADC_wave_b))
        print(len(ADC_wave_b)/num_f)
        print(len(ADC_wave))
        

        ADC_wave = np.array_split(ADC_wave, num_f)
        print(len(ADC_wave[0]))
        print(len(ADC_wave[10]))
        t4 = time.time()
        end=time.time()
        print(end-start)
 
        return ADC_wave

    def get_waveform(self, ch_num):
        print(self.scope.query('HORizontal:FASTframe:REF:FRAme?'))
        t1 = time.time()
        self.scope.write('DATA:SOU CH%i' %ch_num)
        self.scope.chunk_size = 1260000 
       
        self.scope.write('DATA:WIDTH 1')
        self.scope.write('DATA:ENC SRPB')

        self.scope.write('DATA:STOP 225000') #sets max data length
        t2 = time.time()
  #      self.scope.write(':WAV:DATA?')
        self.scope.write('CURVE?')
   

        data = self.scope.read_raw()
        plt.plot(data)
        plt.show()
        t3 = time.time()
        print(len(data))
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave_b = data[headerlen:-1]
        ADC_wave = np.array(unpack('%iB' % (len(ADC_wave_b)),ADC_wave_b))
        t4 = time.time()



        print(len(ADC_wave))
        return ADC_wave, ADC_wave_b
if __name__ == '__main__':
    scope = tek_visa();
#    dat, x = scope.get_waveform(1)
    scope.get_preamble()
#    xyscale = scope.get_scale()
    dat = scope.get_FastFrames()
#    print(xyscale)
    plt.plot(dat[0] )
    plt.plot(dat[9])
    plt.show()
