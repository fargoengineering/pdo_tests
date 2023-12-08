'''
For the first benchmark, we will measure the frequency of an analog read from Slots.

To do this, set 31 boards as analog input, then set the first slot to command 10. This will tell that slot to start a counter that increments each loop and sends it back over PDO.
After a second, set first slot PDO back to 5 (normal) and measure number of loops in a second.
'''
from fei_ethercat_192 import *
from fei_pdo import *
import threading
import random
import time

gv = global_vars()
ec = etherCAT()
pdo = fei_pdo()

data_list = []

ec.run_ec()

def split_bytes(long):
    data1 = ((long >> 16) & 0xFF00) | ((long >> 16) & 0xFF)
    data2 = ((long) & 0xFF00) | (long & 0xFF)
    
    return data1,data2

def split_bytes_gpt(long):
    data1 = (long >> 16) & 0xFFFF
    data2 = long & 0xFFFF
    return data1, data2

def get_input_one():
    packed_input = ec.master.slaves[0].input
    pdo.unpack_input(packed_input)
    
def get_input():
    for slave in ec.master.slaves:
        packed_input = slave.input
        pdo.unpack_input(packed_input)

    
def set_output(packed_output):
    for slave in ec.master.slaves:
        slave.output = packed_output
        ec.master.send_processdata()
        ec.master.receive_processdata(5000)
        packed_input = slave.input 
        # print(packed_input)
        pdo.unpack_input(packed_input)
        
def adc_to_voltage(adc_value):
        # Define the ADC range and corresponding voltage range
        adc_min = 0
        adc_max = 4096
        voltage_min = 0.0
        voltage_max = 18

        # Calculate the voltage using linear interpolation
        voltage = voltage_min + (adc_value - adc_min) * (voltage_max - voltage_min) / (adc_max - adc_min)
        # Ensure voltage is not below zero
        voltage = max(voltage, 0.0)
        # Round to two decimal places
        voltage = round(voltage, 2)

        return voltage
    
# Set all slots to analog input
thread = threading.Thread(target=get_input_one)
for i in range(32):
    pdo.slot_command[i] = 5
    pdo.slot_aux[i] = 3
    
packed = pdo.pack_output()
set_output(packed)
time.sleep(2)

# set the first slot command to 8 for loop counter:
pdo.slot_command[0] = 8
packed = pdo.pack_output()
set_output(packed)

time.sleep(1)
set_output(packed)
# After one second, receive input from slot 1 (loop counter) from data.

    
get_input_one()
print(f"data_in: {pdo.slot_data_in}")
print(f"command_in: {pdo.slot_command_in}")
data_bytes = ec.split_bytes(pdo.slot_data_in[0])

print(f"loopcount: {pdo.slot_data_in[0]}")


# Set all commands back to 5
while(1):
    for i in range(32):
        pdo.slot_command[i] = 5
        pdo.slot_aux[i] = 5
    packed = pdo.pack_output()
    set_output(packed)
    time.sleep(.5)
    get_input_one()

    print("Final commands set to: "+str(pdo.slot_command_in))
    print("Final Data: "+str(pdo.slot_data_in))

    data = split_bytes(pdo.slot_data_in[0])
    print(data[0])
    print(data[1])
    print(adc_to_voltage(data[0]))
    print(adc_to_voltage(data[1]))
    time.sleep(.1)