import pysoem
import struct
import collections

class fei_pdo:
    
    def __init__(self):
        self.slot_command = [0] * 32          # slot command byte
        self.slot_data = [0] * 32             # slot data [64 bytes]
        self.slot_aux = [0] * 32              # slot auxillary data (i.e slot type, ble status)
        
        self.slot_command_in = [0] * 32
        self.slot_data_in = [0] * 32
        self.slot_aux_in = [0] * 32
        # self.pack_format = '32B32l32B'        # 32 bytes, 32 longs, 32 bytes [command, data, auxillary]
        self.pack_format = 'BlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlBBlB'        
        
        
    def set_output(self,c,slot_number,board_num,data1_value,data2_value,data3_value,data4_value,data5_value):
        self.slot_command[slot_number] = c
        values = [int(byte) for byte in [data1_value,data2_value,data3_value,data4_value]]
        shifted_vals = [value << (8 * i) for i, value in enumerate(values)]
        data_out = sum(shifted_vals)
        self.slot_data[slot_number] = data_out
        self.slot_aux[slot_number] = data5_value
    
    def pack_output(self):
        # Convert the first 32 values in slot_command to integers
        command_values = [int(val) for val in self.slot_command[:32]]
        
        # Convert the next 32 values in slot_data to longs
        data_values = [int(val) for val in self.slot_data[:32]]
        
        # Convert the last 32 values in slot_aux to integers
        aux_values = [int(val) for val in self.slot_aux[:32]]

        slot_all_pdo = [0] * 96          # 32 bytes, 32 longs, 32 bytes [command, data, auxillary]

        for i in range(32):
            slot_all_pdo[3*(i-1)] = self.slot_command[i-1]
            slot_all_pdo[(3*(i-1)) + 1] = self.slot_data[i-1]
            slot_all_pdo[(3*(i-1)) + 2] = self.slot_aux[i-1]
        
        # Pack the values using the format string and the *args syntax
        # self.packed_output = struct.pack(self.pack_format, *command_values, *data_values, *aux_values)
        self.packed_output = struct.pack(self.pack_format, *slot_all_pdo)
        
        return self.packed_output
    
    def unpack_input(self):
        # Unpack the packed data into three separate arrays
        unpacked_values = struct.unpack(self.pack_format, self.packed_output)
        
        # Update self.slot_command with the first 32 values
        self.slot_command_in = list(unpacked_values[:32])
        
        # Update self.slot_data with the next 32*4 values
        self.slot_data_in = list(unpacked_values[32:64]) # 32:64
        
        # Update self.slot_aux with the last 32 values
        self.slot_aux_in = list(unpacked_values[64:]) # 64:

    def unpack_input_192(self, unpacked_values):
        # Update self.slot_command with the first 32 values
        command_in = list(unpacked_values[:32])
        
        # Update self.slot_data with the next 32*4 values
        data_in = list(unpacked_values[32:64]) # 32:64
        
        # Update self.slot_aux with the last 32 values
        aux_in = list(unpacked_values[64:]) # 64:

        slot_all_pdo = list(unpacked_values[:])

        fpd = fei_pdo_data()

        # for i in range(32):
        #     fpdt = fei_pdo_data_types(command_in[i-1], data_in[i-1], aux_in[i-1])
        #     fpd.List_slave_data[i-1] = fpdt

        for i in range(32):
            fpdt = fei_pdo_data_types(slot_all_pdo[3*(i-1)], slot_all_pdo[(3*(i-1)) + 1], slot_all_pdo[(3*(i-1)) + 2])
            fpd.List_slave_data[i-1] = fpdt
        
        return fpd
        
class fei_pdo_data_types:
    
    def __init__(self):
        command = 0
        data = 0
        aux = 0
    
    def __init__(self,_command,_data,_aux):
        command = _command
        data = _data
        aux = _aux
        
class fei_pdo_data:

    def __init__(self):
        f1 = fei_pdo_data_types()
        List_slave_data = [f1] * 32


f1 = fei_pdo_data_types(1,2,3)

class_list = []

class_list.append(f1)
    
        
    
