import serial

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

class DAC_8568():

    def __init__(self):
        self.baud_rate = 9600
        self.internal_ref = False
        
        self.ser = serial.Serial('/dev/ttyUSB1', self.baud_rate)
    def spi_write(self, binary_string):
        '''
            Takes 32bit binary string and sends it via serial to the UART on the FPGA
            Does this by first dividing the 32 bit into 4 packets of 8 bits and sending one byte at a time

        '''


        if len(binary_string) != 32:
            print("wrong length")
            return
        packets = [int(binary_string[i:i+8],2) for i in range(0,32,8)]
        uart_packet = bytearray()
        
        uart_packet.append(packets[3])
        uart_packet.append(packets[2])
        uart_packet.append(packets[1])
        uart_packet.append(packets[0])
    
        self.ser.write(uart_packet)
    
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

    test = DAC_8568()

    test.set_internal_ref()
    test.set_dac_voltage(2, 2)
