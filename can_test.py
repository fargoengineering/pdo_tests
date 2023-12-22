from fei_ethercat_192 import *
from fei_pdo import *
import threading
import random
import time

gv = global_vars()
ec = etherCAT()
pdo = fei_pdo()

ec.run_ec()

def set_relay(board,slot,state):
    pdo.slot_command[slot-1] = 13
    pdo.slot_data[slot-1]= board
    pdo.slot_aux[slot-1] = state
    
    ec.master.slaves[board-1].output = pdo.pack_output()
    ec.master.send_processdata()
    ec.master.receive_processdata(5000)

def set_all_relays(state):
    # for i in range(32):
    pdo.slot_command[0] = 13
    pdo.slot_aux[0] = state
        
    for slave in ec.master.slaves:
        slave.output = pdo.pack_output()
        ec.master.send_processdata()
        ec.master.receive_processdata(5000)
        
        
# THIS CODE WORKS
def set_output_relay(board,channel,state):
    pdo.slot_command[channel-1] = 13               # send CAN command
    pdo.slot_data[channel-1] = board               # RELAY BOARD NUMBER, NOT NGIO BOARD NUMBER
    pdo.slot_aux[channel-1] = state        
    ec.master.slaves[board-1].output = pdo.pack_output()
    ec.master.send_processdata()
    ec.master.receive_processdata(5000)
    

set_output_relay(1,1,1)