# This module will send messages to the NGIO via etherCAT to enable banks bluetooth for ota updating.
# ENABLE ONE BANKS BLUETOOTH AT A TIME (1 bank = 8 slot boards)
# Send command = 6 to V51_S3 to send ble enable SPI command.
from slot_program import *
from fei_ethercat_192 import *
from fei_pdo import *

# just need to call update() from slot_program to start the ble_ota process. 
# the rest of the code should be sending ethercat to enable 1 bank at a time.
# may need to update V51_S3 with some logic to determine which bank to activate ble...maybe...


pdo = fei_pdo()
ec = etherCAT()

num_banks = 4
num_slots = 32
ble_command = 6

# start EC Master
ec.run_ec()

def reset_slot_commands():
    for i in range(len(pdo.slot_command)):
        pdo.slot_command[i] = 6 
        pdo.slot_aux[i] = 0

def send_pdo(package):
    if len(ec.master.slaves) == 0:
        print("NO DEVICES ONLINE!")
        return False
    for slave in ec.master.slaves:
        print("Connected to "+slave.name)
        slave.output = package
        ec.master.send_processdata()
        ec.master.receive_processdata(5000)
    return True

# Update 1 slot at a time
def update_1_at_a_time():
    for slot in range(num_slots):
        reset_slot_commands()
        time.sleep(1)
        pdo.slot_command[slot] = ble_command
        pdo.slot_aux[slot] = 1
        packed = pdo.pack_output()
        
        print(pdo.slot_command)
        # Send the pdo to enable the current bank:
        if send_pdo(packed) == False:
            break
        time.sleep(3)

        update()        
        time.sleep(3)
    
    # Turn off all bluetooth
    reset_slot_commands()
    send_pdo(pdo.pack_output())
        
        
# Update 8 slots at a time:
def update_8_at_a_time():
    for bank in range(1, num_banks + 1):
        print(bank)
        reset_slot_commands()
        if bank==1:
            for i in range(8):
                # Data and aux bytes don't matter
                pdo.slot_command[i] = ble_command
        elif bank == 2:
            for i in range(8,16):
                # Data and aux bytes don't matter
                pdo.slot_command[i] = ble_command
        elif bank == 3:
            for i in range(16,24):
                # Data and aux bytes don't matter
                pdo.slot_command[i] = ble_command
        elif bank == 4:
            for i in range(24,32):
                # Data and aux bytes don't matter
                pdo.slot_command[i] = ble_command
        else:
            print("no more banks!")
            break
        packed = pdo.pack_output()
        print(pdo.slot_command)
        # Send the pdo to enable the current bank:
        if send_pdo(packed) == False:
            break
        # stop sending ble on command    
        # reset_slot_commands()
        # if send_pdo() == False:
        #     break
        time.sleep(3)
        # now that ble should be active, start the ota process:
        update()
        time.sleep(3)
        # repeat until all banks updated.                
        
        
        
if __name__ == "__main__":            
    # update_8_at_a_time()
    update_1_at_a_time()