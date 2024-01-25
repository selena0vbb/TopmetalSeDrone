import serial
import time
DONT_CARE = "0101" #used for dont care bits, value irrelevant
DAC_START = "0000"
SA_PXL_SELECT = "0001" #select pixel via UART
SA_PXL_SWITCH = "0011" #select pixel via hardware switches
LA_PXL_SELECT = "0100" #select pixel via UART


def dac_voltage(adu, vref=2.5, gain=1):
    '''
        Converts from ADU input to voltage value
    '''
    v_out = (adu/2**16) * vref

    return v_out

def volt_dac(volt, vref = 2.5, gain=1):
    '''
        Converts from v input to DAC value
    '''
#    volt = mv/100
    d_in = volt/(vref*gain) * 2**16
    return int(d_in)


class fpga_UART_commands():

    def __init__(self):
        '''
            Sets initial values
            Defaults to a baud rate of 9600 and ttyUSB1.

        '''
        self.baud_rate = 9600
        self.internal_ref = False
        self.port_name = '/dev/ttyUSB1'
        self.ser = serial.Serial(self.port_name, self.baud_rate)
    
    def set_port(self,port):
        '''
            Changes the port name, probably not working as of yet... simple fix for later
        '''
        self.port_name = port

    def uart_write(self,binary_string):
        '''
            Writes strings of binary values to the FPGA via UART
            Only writes 8 bits at a time, for now
        '''
        if len(binary_string) != 8:
            print("wrong length")
            return
        uart_packet=bytearray()
        uart_packet.append(int(binary_string,2))
        self.ser.write(uart_packet)
     
    def DAC_write_start(self):
        '''
            Tells the FPGA that the 32 bits after these 8 will be used for the DAC and should be written via SPI
        '''
        self.uart_write(DONT_CARE+DAC_START)

    def LA_pixel_select(self, pxl_num):
        '''
            Selects a pixel out of the large array
            If the pxl_num is larger than the number of pixels, this will end up just scanning the pixel array
        '''
        self.LA_scan_on()
        time.sleep(0.05)
        self.uart_write(DONT_CARE+LA_PXL_SELECT)
        DATA = format(pxl_num, '016b')
        self.uart_write(DATA[8:])
        self.uart_write(DATA[:8])

    def LA_scan_on(self):
        '''
            Turns the large array pixel scan on just by setting the pixl number higher than the no. of pixels.
            I think this is necessary to turn on before a pixel switch in order to clock to the correct pixel.
        '''
        self.uart_write(DONT_CARE+LA_PXL_SELECT)
        DATA = format(12000, '016b')
        self.uart_write(DATA[8:])
        self.uart_write(DATA[:8])

    def SA_pixel_select(self, pxl_num):
        '''
            Selects a pixel out of the small array
        '''
        if pxl_num >=9:
            print("Pixel Number too high")
            return
        DATA = format(pxl_num, '04b')
        self.uart_write(DATA+SA_PXL_SELECT)

    def SA_use_switch(self):
        '''
            Allows user to select a pixel via the hardware switches on the BASYS3 FPGA board
        '''
        self.uart_write(DONT_CARE + SA_PXL_SWITCH)

    def spi_write(self, binary_string):
        '''
            Takes 32bit binary string and sends it via serial to the UART on the FPGA to be sent via SPI to the DAC
            Does this by first dividing the 32 bit into 4 packets of 8 bits and sending one byte at a time

        '''


        if len(binary_string) != 32:
            print("wrong length")
            return
        self.DAC_write_start()
        packets = [int(binary_string[i:i+8],2) for i in range(0,32,8)]
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
    #fpga.SA_pixel_select(1)
    #fpga.SA_use_switch()
    fpga.LA_pixel_select(5302)

    '''
    fpga.set_internal_ref()
    fpga.set_dac_voltage(0,0.3)
    fpga.set_dac_voltage(1,1.5)
    fpga.set_dac_voltage(2, 1.14) 
    fpga.set_dac_voltage(3,0.696)
    fpga.set_dac_voltage(4, 1.143)
    fpga.set_dac_voltage(5, 0.5)
    fpga.set_dac_voltage(6, 0.27)
    fpga.set_dac_voltage(7, 1)
    '''
