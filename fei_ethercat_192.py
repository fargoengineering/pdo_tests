import pysoem
import struct
import collections
import time
from global_vars import *

class etherCAT:
    
    PRODUCT_CODE = 0xBEEF
    VENDOR_ID = 0x00000EEA
    
    slot_type = 0
    slave_count = 1
    slave_pdo_byte_count = 192
    
    def __init__(self):  
        self.master = pysoem.Master()
        # self.gv = global_vars()
        # self.ec_adapter_name = "eth0"      # linux format 
        self.ec_adapter_name = "\\Device\\NPF_{2AFC35B5-1EE7-49B9-927D-D2CE5EDC52DD}"    # Windows Format (-_-)
        SlaveSet = collections.namedtuple('SlaveSet', 'slave_name product_code config_func')
        self._expected_slave_mapping = {0: SlaveSet('FEI_SLAVE', self.PRODUCT_CODE, None)}        
        
        # 192 byte PDO arrays
        self.slot_command = [0] * 32          # slot command byte
        self.slot_data = [0] * 32             # slot data [64 bytes]
        self.slot_aux = [0] * 32              # slot auxillary data (i.e slot type, ble status)
        
        self.slot_command_in = [0] * 32
        self.slot_data_in = [0] * 32
        self.slot_aux_in = [0] * 32
        self.pack_format = '32B32l32B'        # 32 bytes, 32 longs, 32 bytes [command, data, auxillary]
        
        
        
    def set_output(self,c,slot_number,data1_value,data2_value,data3_value,data4_value,data5_value):
        self.slot_command[int(slot_number)] = c
        values = [int(byte) for byte in [data1_value,data2_value,data3_value,data4_value]]
        shifted_vals = [value << (8 * i) for i, value in enumerate(values)]
        data_out = sum(shifted_vals)
        self.slot_data[int(slot_number)] = data_out
        self.slot_aux[int(slot_number)] = data5_value
    
    def pack_output(self):
        # Convert the first 32 values in slot_command to integers
        command_values = [int(val) for val in self.slot_command[:32]]
        
        # Convert the next 32 values in slot_data to longs
        data_values = [int(val) for val in self.slot_data[:32]]
        
        # Convert the last 32 values in slot_aux to integers
        aux_values = [int(val) for val in self.slot_aux[:32]]
        
        # Pack the values using the format string and the *args syntax
        self.packed_output = struct.pack(self.pack_format, *command_values, *data_values, *aux_values)
        
        return self.packed_output
    
    def unpack_input(self,packed_input):
        # Unpack the packed data into three separate arrays
        unpacked_values = struct.unpack(self.pack_format, packed_input)
        
        # Update self.slot_command with the first 32 values
        self.slot_command_in = list(unpacked_values[:32])
        
        # Update self.slot_data with the next 32 values
        self.slot_data_in = list(unpacked_values[32:64])
        
        # Update self.slot_aux with the last 32 values
        self.slot_aux_in = list(unpacked_values[64:])
        
    def run_ec(self):        
        self.master.open(self.ec_adapter_name)   # make sure matching correct platform
        
        if self.master.config_init() > 0:            
            for i,slave in enumerate(self.master.slaves):
                print(f"Slave name: {slave.name}")
                print("connected to slave")
                
            self.master.config_map()
            
            # wait 50 ms for slaves to reach SAFE_OP state
            if self.master.state_check(pysoem.SAFEOP_STATE, 50000) != pysoem.SAFEOP_STATE:
                self.master.read_state()
                for slave in self.master.slaves:
                    if not slave.state == pysoem.OP_STATE:
                        print(f"{slave.name} did not reach OP state")
                # raise Exception('not all slaves reached OP state')
            
            # go to OP state    
            self.master.state = pysoem.OP_STATE
            self.master.write_state()

            self.master.state_check(pysoem.OP_STATE, 50000)
            if self.master.state != pysoem.OP_STATE:
                self.master.read_state()
                for slave in self.master.slaves:
                    if not slave.state == pysoem.OP_STATE:
                        print('{} did not reach OP state'.format(slave.name))
                raise Exception('not all slaves reached OP state')
                
    def update_pdo(self,command,slot_number,board_number,data1,data2,data3,data4,data5):        
        # WRITE OUTPUT PDO
        # 20 byte code:
        packed_output = struct.pack('BBBBBBBB',int(command),int(slot_number),int(board_number),int(data1),int(data2),int(data3),int(data4),int(data5))    # old pdo version
        self.master.slaves[0].output = packed_output
        ###############
        # 192 byte code: 
        # packed_output = self.set_output(command,slot_number,data1,data2,data3,data4,data5)
        # self.master.slaves[0].output = packed_output
        ################
        self.master.send_processdata()        
        self.slot_type = data5  # save slot_type for quick reference        
        time.sleep(0.05) 
        
    def read_pdo(self):
        # Read Input PDO
        self.master.send_processdata()
        self.master.receive_processdata(2000)
        try:
            voltage__bytes = self.master.slaves[0].input
            # print(voltage__bytes)
            # print(f"input as bytes: {voltage__bytes}")                                        
            unpacked_data = struct.unpack('llHHH', voltage__bytes)
            # Now, unpacked_data contains the values as a tuple.
            data1 = unpacked_data[0]
            data2 = unpacked_data[1]
            data3 = unpacked_data[2]
            data4 = unpacked_data[3]
            data5 = unpacked_data[4]
            # data6 = unpacked_data[5]
            # data7 = unpacked_data[6]
            # data8 = unpacked_data[7]
            
            a2d_count = self.adc_to_voltage(data3)
            if int(self.slot_type) == 3 or int(self.slot_type) == 4:
                # convert data3 to voltage
                return(f"data1: {a2d_count} V\n data2: {data4}\n data3: {data5}\n ")
            else:
                return((f"data1: {data3}\n data2: {data4}\n data3: {data5}\n"))
        except Exception as e:
            print(e)
            print("EtherCAT Device Not Online!")
        
    def read_pdo_192(self):
        # Read Input PDO
        self.master.send_processdata()
        self.master.receive_processdata(2000)

        try:
            all_pdo = [ [0]* self.slave_pdo_byte_count for i in range(self.slave_count)]
            for i in range(self.slave_count):

                pdo_bytes = self.master.slaves[i-1].input
                                                    
                unpacked_data = struct.unpack(self.pack_format, pdo_bytes)
                
                all_pdo[i-1] = unpacked_data
                
            return all_pdo
        except Exception as e:
            print(e)
            print("EtherCAT Device Not Online!")
            
            
    def read_pdo_test(self):
        # Read Input PDO
        self.master.send_processdata()
        self.master.receive_processdata(2000)
        try:
            voltage__bytes = self.master.slaves[0].input
            # print(voltage__bytes)
            # print(f"input as bytes: {voltage__bytes}")                                        
            unpacked_data = struct.unpack('llHHH', voltage__bytes)
            # Now, unpacked_data contains the values as a tuple.
            data1 = unpacked_data[0]
            data2 = unpacked_data[1]
            data3 = unpacked_data[2]
            data4 = unpacked_data[3]
            data5 = unpacked_data[4]
            # data6 = unpacked_data[5]
            # data7 = unpacked_data[6]
            # data8 = unpacked_data[7]
            
            a2d_count = self.adc_to_voltage(data3)
            return data3,data4
        except Exception as e:
            print(e)
            print("EtherCAT Device Not Online!")
        
    def close_ec(self):
        self.master.state = pysoem.INIT_STATE
        # request INIT state for all slaves
        self.master.write_state()
        time.sleep(1)
        self.master.close()
        time.sleep(1)
                
    def adc_to_voltage_old(self,adc_count):
        # Define the data points
        data_points = {
            30: 0.0,
            767: 3.3,
            940: 4.0,
            1163: 5.0,
            1400: 6.0,
            1870: 8.0,
            1900: 10.0  # Added 10 volts with an ADC count of about 1900
        }

        # Sort the data points by ADC count
        sorted_counts = sorted(data_points.keys())

        # Handle values below the lowest ADC count
        if adc_count < sorted_counts[0]:
            return 0.0

        # Find the two closest data points for interpolation
        lower_count = sorted_counts[0]
        upper_count = sorted_counts[-1]
        for count in sorted_counts:
            if count > adc_count:
                upper_count = count
                break
            lower_count = count

        # Check for exact match and return the corresponding voltage
        if lower_count == upper_count:
            return data_points[lower_count]

        # Linear interpolation
        lower_voltage = data_points[lower_count]
        upper_voltage = data_points[upper_count]

        voltage = lower_voltage + (adc_count - lower_count) * (upper_voltage - lower_voltage) / (upper_count - lower_count)
        
        # Round to two decimal places
        voltage = round(voltage, 2)
        
        return voltage

    def adc_to_voltage(self,adc_value):
        # Define the ADC range and corresponding voltage range
        adc_min = 0
        adc_max = 4096
        voltage_min = 0.0
        voltage_max = 17.25

        # Calculate the voltage using linear interpolation
        voltage = voltage_min + (adc_value - adc_min) * (voltage_max - voltage_min) / (adc_max - adc_min)
        # Ensure voltage is not below zero
        voltage = max(voltage, 0.0)
        # Round to two decimal places
        voltage = round(voltage, 2)

        return voltage

    def pack_bytes_to_pdo(self,byteArray):
        if len(byteArray) != 8:
            raise ValueError("Input byteArray must contain exactly 8 values")

        # Use the 'Q' format specifier to pack into an unsigned long long (64 bits)
        packed_value = struct.pack('Q', *byteArray)
        # Unpack the bytes to a 64-bit integer (unsigned long long)
        unpacked_value = struct.unpack('Q', packed_value)[0]

        return unpacked_value



# # Example usage:
# ec = etherCAT()
# adc_value = 1000  # Replace this with your ADC count
# voltage = adc_to_voltage(adc_value)
# print(f"ADC Count: {adc_value}, Voltage: {voltage} V")
# ec.run_ec()
# # command, slot#, board#, data1,2,3,4,5
# ec.update_pdo(5,1,1,4,5,6,7,8)
# ec.close_ec()
        
        