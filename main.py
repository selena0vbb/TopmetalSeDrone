import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('tmse_control/')
sys.path.append('scope_control/')
sys.path.append('afg_control/')

import afg_input as afg
import scope_visa as svi
import DAC_control
import fpga_comm
import argparse
import configparser
import uproot

import pyfiglet
from tabulate import tabulate

import time
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

    header = data_preamble + '\n' + dac_preamble + config_preamble + '\n#CHIP ID : %i\n' %args.chip_id + '\n\n'
    return header
def write_root(output_file,waveform, config, xyscale):
    file = uproot.recreate(output_file)
    
    #Scope Scale
    file["Header/xscale(t)"]= str(xyscale[0])
    file["Header/yscale(V)"]= str(xyscale[1])
    file["Header/yoffset(V)"]= str(xyscale[2])

    #header
    config_dict = {s:dict(config.items(s)) for s in config.sections()}
    for key in config_dict.keys():
        for key_value in config_dict[key].keys():
            #print(config_dict[key][key_value])
            file["Header/%s/%s" %(key,key_value)] = config_dict[key][key_value]
     
    #waveforms
    #file["waveform"] = {"wf": [waveform, waveform, waveform, waveform] }
    file.mktree("wfTree", {"wf": ("uint8", (len(waveform), ))}, title = "waveforms")
    return file

if __name__ == '__main__':

    tek_scope = svi.tek_visa()
    afg_device = afg.afg_visa() 

    fpga_device = fpga_comm.fpga_UART_commands()
    fpga_device.set_internal_ref()

    parser = argparse.ArgumentParser(prog = 'TMSeDrone')

    parser.add_argument('-id',type=int, dest='chip_id', required=True, help = 'Chip ID Number, written on QFN pacakging')

    parser.add_argument('-sp' , type=int, dest='num_wfs', help='Number of single pixel (CSA) waveforms')
    parser.add_argument('-config', type=argparse.FileType('r', encoding='UTF-8'), dest='config_file', help='Config File', default='config/Config.ini')
    parser.add_argument('-ofile', type = str, dest = 'ofile', help = 'Prefix for output file(s)', default='video_out.root')
    
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
            if config['TMSe Pixel']['SA_pxl_num'] != '-1':
                print("Selecting pixel: %i" %(int(config['TMSe Pixel']['SA_pxl_num'])))
                fpga_device.SA_pixel_select(int(config['TMSe Pixel']['SA_pxl_num']))
            elif config['TMSe Pixel']['LA_pxl_num'] != -1:
                print("Selecting LA pixel: %i" %(int(config['TMSe Pixel']['SA_pxl_num'])))
                afg_device.setch1_voltage('ON',3.3, 1E6)
                fpga_device.LA_pixel_select(int(config['TMSe Pixel']['LA_pxl_num']))
                afg_device.setch1_voltage('OFF',3.3, 1E6)

        if config['Calibration']['Calib'] == 'True':
            pulse_height = float(config['Calibration']['gring_height']) /1000
            gring_freq = float(config['Calibration']['gring_freq'])

            afg_device.setch2_voltage('ON',pulse_height ,gring_freq)
        print(config.items())
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
        tek_scope.get_preamble() 
        xyscale =  tek_scope.get_scale()
       
        header = make_header(xyscale, config,args,ch_names, val)  
        
        for i in range(args.num_wfs): 
            start = time.time()
            wf, wf_b = tek_scope.get_waveform(1)
            if i == 0:
                file = write_root(args.ofile,wf, config, xyscale)
            file["wfTree"].extend( {"wf": [wf]} )
            end=time.time()
            print("Waveforms: %i \t Acquisition time: %.3f" %(i, end-start))
    else: #read pixel array
        print('pixel array read not available')
        

