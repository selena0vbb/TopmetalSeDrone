import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('tmse_control/')
sys.path.append('scope_control/')

import scope_visa as svi
import DAC_control
import fpga_comm
import argparse
import configparser

import pyfiglet
from tabulate import tabulate

def make_header(xyscale, config, args,ch_names, val):
    #Oscilloscope Scale Settings
    data_scale_name=['T step(s)', 'Y Scale(V)', 'Y Offset(mV)']
    mylist = list(zip(data_scale_name, xyscale))
    data_preamble ='#Data ::' + ' ; '.join('%s:%s' % x for x in mylist)

    #Bias Settings
    config_header_list = list(zip(ch_names,val))
    dac_preamble ='#Config (V) :: ' + ' ; '.join('%s:%s' %x for x in config_header_list)
    
    
    #TMSe Info
    config_preamble=''
    for section in config:
        if section != 'DAC' and section != 'DEFAULT':
            config_preamble += "\n#%s :: " %section
            for param_name in config[section]:
                config_preamble += "%s : %s ; " %(param_name, config[section][param_name])
#    info_preamble ='Chip ID: %%i ,  %s, LA Pixel Num: %i, SA Pixel Num: %i' %(args.chip_id, config['TMSe Pixel']['LA_pxl_num'], config['TMSe Pixel']['SA_pxl_num'])


    header = data_preamble + '\n' + dac_preamble + config_preamble + '\n#CHIP ID : %i\n' %args.chip_id + '\n\n'
    return header

if __name__ == '__main__':

    tek_scope = svi.tek_visa()

    fpga_device = fpga_comm.fpga_UART_commands()
    fpga_device.set_internal_ref()

    parser = argparse.ArgumentParser(prog = 'TMSeDrone')

    parser.add_argument('-id',type=int, dest='chip_id', required=True, help = 'Chip ID Number, written on QFN pacakging')

    parser.add_argument('-sp' , type=int, dest='num_wfs', help='Number of single pixel (CSA) waveforms')
    parser.add_argument('-config', type=argparse.FileType('r', encoding='UTF-8'), dest='config_file', help='Config File', default='config/Config.ini')
    parser.add_argument('-ofile', type = str, dest = 'ofile', help = 'Prefix for output file(s)', default='video_out')
    
    parser.add_argument('-SA_sel', type = int, dest='sa_pxl_addr', help='Select pixel on small array')
    parser.add_argument('-SA_sw', type=bool, dest = 'use_switch', help='Select pixels via hardware switches')

    #need to do
    parser.add_argument('-LA_sel', type = int, dest='la_pxl_addr', help ='Select pixel on large array')
    parser.add_argument('-LA_clk', type = bool, dest='la_clk_on', help = 'Turn on LA pixel scan')

    args=parser.parse_args() 
    
    if (args.config_file is not None): #write a bias config 
        

        config=configparser.ConfigParser()
        config.read(args.config_file.name)
         
        if config['TMSe Pixel']['Single_pxl']:
            if config['TMSe Pixel']['SA_pxl_num'] != -1:
                print("Selecting pixel: %i" %(int(config['TMSe Pixel']['SA_pxl_num'])))
                fpga_device.SA_pixel_select(int(config['TMSe Pixel']['SA_pxl_num']))
            elif config['TMSe Pixel']['LA_pxl_num'] != -1:
                print('LA not yet tested')
        
        load_instant=False

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
                fpga_device.set_dac_voltage(channel, dac_value, load=True, adu = use_adu) #write DAC value and instantly load onto DAC
            else:
                if channel < 7:
                    fpga_device.set_dac_voltage(channel, dac_value ) #write DAC without loading 
                else:
                    fpga_device.set_dac_voltage(channel, dac_value, load=True,update_all=True, adu = use_adu) #write last channel and load all values
    
    if (args.sa_pxl_addr is not None):
        
        fpga_device.SA_pixel_select(args.sa_pxl_addr)
    else:
        print('skipping this for now')
        #print('this')
        #fpga_device.SA_use_switch()

    if (args.num_wfs is not None): #means we want single pixel waveforms
        
        xyscale =  tek_scope.get_scale()
       
        header = make_header(xyscale, config,args,ch_names, val)  
        for i in range(args.num_wfs): 
            wf, wf_b = tek_scope.get_waveform(1)
            with open(args.ofile+"_%i.dat"%i, "wb") as out:
                out.write(header.encode('utf-8'))
                out.write(('#Data Length: %i\n' %len(wf_b)).encode('utf-8'))
                out.write(wf_b)
        
    else: #read pixel array
        print('pixel array read not available')
        

