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
    pdo.slot_command[slot-1] = 7
    pdo.slot_aux[slot-1] = state
    
    ec.master.slaves[board-1].output = pdo.pack_output()
    ec.master.send_processdata()
    ec.master.receive_processdata(5000)

def set_all_relays(state):
    for i in range(32):
        pdo.slot_command[i] = 13
        pdo.slot_aux[i] = state
        
    for slave in ec.master.slaves:
        slave.output = pdo.pack_output()
        ec.master.send_processdata()
        ec.master.receive_processdata(5000)

# for i in range(32):
#     pdo.slot_command[i] = 7
#     pdo.slot_aux[i] = 0
    
# packed = pdo.pack_output()

# for slave in ec.master.slaves:
#     slave.output=packed
#     ec.master.send_processdata()
#     ec.master.receive_processdata(5000)
#     time.sleep(1)
    
# Turn relays on board 1
for i in range(32):
    set_relay(2,i,1)
    # set_all_relays(1)

time.sleep(1)

for i in range(32):
    # set_relay(1,i,0)
    set_all_relays(0)