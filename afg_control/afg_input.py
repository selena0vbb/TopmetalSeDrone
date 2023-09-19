import pyvisa
import matplotlib.pyplot as plt
import numpy as np
from struct import unpack

#def to_xy(ADC_data, xyscale):
 #   volts = (ADC_data-xyscale[0])*xyscale[1]
  #  time = np.arange(0, xyscale[0] * len(volts), xyscale[0])
    
   # return time, volts
    


class afg_visa():
	def __init__(self):
		rm = pyvisa.ResourceManager('@py')
		print(rm.list_resources())
		self.scope = rm.open_resource('USB0::2391::22279::MY59000490::0::INSTR')
		print(self.scope.query('*IDN?'))
        #print(self.scope.query('*TST?'))
        
	def setch1_voltage(self,status, voltage,frequency):
		self.scope.write('OUTP1 '+ str(status))
		self.scope.write('SOURce1:VOLTage +'+str(voltage))
		self.scope.write('SOURce1:FREQuency +' + str(frequency))

	def setch2_voltage(self,status2, voltage2,frequency2):
		'''
		signal in V, Hz 

		'''

		self.scope.write('OUTP2 '+ str(status2))
		self.scope.write('SOURce2:VOLTage +'+str(voltage2))
		self.scope.write('SOURce2:FREQuency +' + str(frequency2))
		self.scope.write('OUTP2:LOAD INF')



if __name__ == '__main__':
    afg = afg_visa()
    #afg.setch1_voltage('ON',0.7,+1.0E+06)
    #afg.setch2_voltage('ON',0.4,+1.0E+06)


   # scope.get_preamble()

#    ADC_wave = scope.get_waveform(1)
  #  xyscale = scope.get_scale()
 #   time,volts= to_xy(ADC_wave,xyscale)

#    plt.plot(time, volts)
#    plt.show()
#
