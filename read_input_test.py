from fei_ethercat_192 import *
from fei_pdo import *
import threading
import random
import time

gv = global_vars()
ec = etherCAT()
pdo = fei_pdo()

data_list = []

def split_bytes_16(long):
    data1 = ((long >> 16) & 0xFF00) | ((long >> 16) & 0xFF)
    data2 = ((long) & 0xFF00) | (long & 0xFF)
    
    return data1,data2

def split_bytes_4(long):
    byte1 = (long >> 24) & 0xFF
    byte2 = (long >> 16) & 0xFF
    byte3 = (long >> 8) & 0xFF
    byte4 = long & 0xFF

    return byte1, byte2, byte3, byte4

ec.run_ec()

slot = 5
board = 1

pdo.slot_command[slot-1] = 5
pdo.slot_aux[slot-1] = 3

ec.master.slaves[board-1].output = pdo.pack_output() # ec.pack_output()
ec.master.send_processdata()
ec.master.receive_processdata(5000)

time.sleep(2)

while(1):
    ec.master.send_processdata()
    ec.master.receive_processdata(5000)

    pdo.unpack_input(ec.master.slaves[board-1].input)

    data_in = pdo.slot_data_in[slot-1]

    unshifted_data_values = split_bytes_16(data_in)

    print(f"Slot data in: \n 0: {unshifted_data_values[0]}\n1: {unshifted_data_values[1]}\n")
    
    time.sleep(2)