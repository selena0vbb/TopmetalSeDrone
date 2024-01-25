
class parser():
    
    list_of_commands = ['set_v']
    
    def __init__(self, DAC_instance):
        self.DAC = DAC_instance
 
    def parse_command(self, full_command):
     
        in_str = full_command.split()
        print(in_str) 
        command =  in_str[0]
        args = in_str[1:]
        if command not in self.list_of_commands:
            print('Invalid Command')
            return
        else:
            if command == 'set_v':
                ch = int(args[0])
                value = float(args[1])
                print("Setting DAC Voltage: CH %i VOLT %F" %(ch, value))
                self.DAC.set_dac_voltage(ch, args[1])

   
