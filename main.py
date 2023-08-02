import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('tmse_control/')
sys.path.append('scope_control/')

import scope_visa as svi
import DAC_control

import argparse
import configparser

import pyfiglet
from tabulate import tabulate

def make_header(xyscale, ch_names, val):

    data_scale_name=['T step(s)', 'Y Scale(V)', 'Y Offset(mV)']
    mylist = list(zip(data_scale_name, xyscale))
    data_preamble ='Data ::' + ' ; '.join('%s:%s' % x for x in mylist)

    config_header_list = list(zip(ch_names,val))
    config_preamble ='Config (V) :: ' + ' ; '.join('%s:%s' %x for x in config_header_list)
    
    
    header = data_preamble + '\n' + config_preamble + '\n\n\n\n\n\n'

    return header




if __name__ == '__main__':

    tek_scope = svi.tek_visa()

    dac_device = DAC_control.DAC_8568()
    dac_device.set_internal_ref()

    parser = argparse.ArgumentParser(prog = 'TMSeDrone')

    parser.add_argument('--sp' , type=int, dest='num_wfs', help='Number of single pixel (CSA) waveforms')
    parser.add_argument('-config', type=argparse.FileType('r', encoding='UTF-8'), dest='config_file', help='Config File', default='config/Config.ini')
    parser.add_argument('-ofile', type = str, dest = 'ofile', help = 'Prefix for output file(s)', default='video_out')

    args=parser.parse_args() 

    if (args.num_wfs is not None): #means we want single pixel waveforms
        
        #Load DAC
        load_instant=False
        config=configparser.ConfigParser()
        config.read(args.config_file.name)

        ch = np.arange(0,8,1)
        ch_names = ['SF_IB', 'NB1', 'NB2', 'OUT_IB', 'AMP_IB', 'VREF', 'CSA_VREF', 'VBIAS']
        
        val = []

        for ch_num in ch:
            ch_attr = 'ch_%i'%(ch_num)
            val.append(float(config['DAC'][ch_attr]))

        table_ch_val = list(zip(ch,ch_names,val))

        print(tabulate(table_ch_val, headers=['Channel', 'Value(V)']))
        use_adu=False

        for value_set in table_ch_val:
            channel = value_set[0]
            dac_value = value_set[2]
            if load_instant: 
                dac_device.set_dac_voltage(channel, dac_value, load=True, adu = use_adu) #write DAC value and instantly load onto DAC
            else:
                if channel < 7:
                    dac_device.set_dac_voltage(channel, dac_value, load=False, adu = use_adu) #write DAC without loading 
                else:
                    dac_device.set_dac_voltage(channel, dac_value, load=True,update_all=True, adu = use_adu) #write last channel and load all values
        
        #Select Pixel
        '''
            Need to write VHDL, python to do this

       ''' 

        #Readout waveforms from scope
        '''
            input number waveforms taken

        '''
                
        xyscale =  tek_scope.get_scale()
        
        header = make_header(xyscale, ch_names, val)  
        for i in range(args.num_wfs): 
            wf = tek_scope.get_waveform(1)
        
            with open(args.ofile+"_%i.dat"%i, "w") as out:
                out.write(header)
                out.write(str(list(wf)))

    else: #read pixel array
        print('pixel array read not available')
        

