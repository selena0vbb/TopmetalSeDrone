import serial
import time
DONT_CARE = "0101" #used for dont care bits, value irrelevant
DAC_START = "0000"
SA_PXL_SELECT = "0001" #select pixel via UART
SA_PXL_SWITCH = "0011" #select pixel via hardware switches
LA_PXL_SELECT = "0100" #select pixel via UART


def dac_voltage(adu, vref=2.5, gain=1):
    v_out = (adu/2**16) * vref

    return v_out

def volt_dac(volt, vref = 2.5, gain=1):
    '''
        converts from v input to DAC value
    '''
#    volt = mv/100
    d_in = volt/(vref*gain) * 2**16
    return int(d_in)


class fpga_UART_commands():

    def __init__(self):
        self.baud_rate = 9600
        self.internal_ref = False
        self.port_name = '/dev/ttyUSB1'
        self.ser = serial.Serial(self.port_name, self.baud_rate)
    
    def set_port(port):
        self.port_name = port

    def uart_write(self,binary_string):
        if len(binary_string) != 8:
            print("wrong length")
            return
        uart_packet=bytearray()
        uart_packet.append(int(binary_string,2))
        print(uart_packet)

        self.ser.write(uart_packet)
    
    def DAC_write_start(self):
        self.uart_write(DONT_CARE+DAC_START)

    def LA_pixel_select(self, pxl_num):
        self.uart_write(DONT_CARE+LA_PXL_SELECT)
        DATA = format(pxl_num, '016b')
        
    def LA_scan_on():
        return -1

    def SA_pixel_select(self, pxl_num):
        DATA = format(pxl_num, '04b')

        self.uart_write(DATA+SA_PXL_SELECT)

    def SA_use_switch():
        return -1
    def spi_write(self, binary_string):
        '''
            Takes 32bit binary string and sends it via serial to the UART on the FPGA to be sent via SPI to the DAC
            Does this by first dividing the 32 bit into 4 packets of 8 bits and sending one byte at a time

        '''


        if len(binary_string) != 32:
            print("wrong length")
            return
        self.DAC_write_start()
        print(binary_string)
        packets = [int(binary_string[i:i+8],2) for i in range(0,32,8)]
        print(packets)
        uart_packet = bytearray()
        
        uart_packet.append(packets[3])
        uart_packet.append(packets[2])
        uart_packet.append(packets[1])
        uart_packet.append(packets[0])
    
        self.ser.write(uart_packet)
#        time.sleep(0.1) 
    def set_internal_ref(self):
        '''
            Tells the DAC to use its internal reference voltage (~2.5V)
            Necessary to use the DAC and must be done on power up
        '''

        bin_string = "00001000000000000000000000000001"
        self.spi_write(bin_string) 
    def set_dac_voltage(self, channel, value, load=True, update_all=False, adu=False):
        '''
            Sends a 16bit value to the DAC at a channel
            If load is true, then the value is instantly loaded onto the DAC. If false, the voltage is only present once the value is loaded
        '''
        PRFX = "0000"
        if load:
            if update_all:
                CNTRL = "0010"
            else:
                CNTRL = "0011"
        else:
            CNTRL="0000"

        ADDR = format(channel, '04b')
        if adu==True:
            DATA = format(value, '016b')
        else:
            DATA = format(volt_dac(value), '016b')

        FEAT = "1111" #mostly don't matter
        
        bin_string = PRFX + CNTRL + ADDR + DATA + FEAT
        
        self.spi_write(bin_string)
    
    def load_dac(self, channel=-1):
        '''
            Loads values onto DAC voltages
            if channel = -1, then it loads all values
            if channel is 0-7 then it loads specific channel
        '''
        
        PRFX = "0000"
        CNTRL = "0001"

        if channel>=0 and channel <=7:
            ADDR = format(channel, '04b')
        else:
            ADDR = "1111"
        DATA = format(0, '016b')
        FEAT = "1111"

        bin_string = PRFX + CNTRL + ADDR + DATA + FEAT

        self.spi_write(bin_string)

    

    def power_down(self):
        '''
            For now, we will do this just by turning off the internal reference

        '''
        bin_string  = "00001000000000000000000000000000"
        self.spi_write(bin_string)


if __name__ == '__main__':
    fpga = fpga_UART_commands()
    #fpga.SA_pixel_select(0)
    fpga.set_internal_ref()
    fpga.set_dac_voltage(0,0.3)
    fpga.set_dac_voltage(1,1.5)
    fpga.set_dac_voltage(2, 1.14) 
    fpga.set_dac_voltage(3,0.696)
    fpga.set_dac_voltage(4, 1.143)
    fpga.set_dac_voltage(5, 0.5)
    fpga.set_dac_voltage(6, 0.27)
    fpga.set_dac_voltage(7, 1)
