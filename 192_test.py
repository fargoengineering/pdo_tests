from fei_ethercat_192 import *
from fei_pdo import *
import threading

gv = global_vars()
ec = etherCAT()
pdo = fei_pdo()
key = []


# start EC Master
ec.run_ec()

# Set some PDO values...
#
j=1
for i in range(32):
  pdo.slot_command[i] = 5
  pdo.slot_data[i] = (i + 1)  
  pdo.slot_aux[i] = 1
  
  if j < 6:
    j=j+1
  else:
    j=1

for i in range(len(pdo.extraBytes)):
  pdo.extraBytes[i] = 1

#Now pack those data's to the struct and update PDO:
# packed = pdo.pack_output()
# print(packed)

while(1):
  # Loop through slot types:
  for i in range(32):
    pdo.slot_aux[i] = j
    
  if j < 6: j=j+1
  else: j=1
  packed = pdo.pack_output()
  # print(packed)  
  print("GO")
  print(pdo.slot_aux[i])
  
  ec.master.slaves[0].output = packed
  ec.master.send_processdata()
  ec.master.receive_processdata(2000)
  packed_input = ec.master.slaves[0].input
  pdo.unpack_input(packed_input)
  # for slave in ec.master.slaves:
  #   slave.output = packed
  #   ec.master.send_processdata()
  #   ec.master.receive_processdata(5000)
  #   packed_input = slave.input #ec.master.slaves[0].input
  #   # print(packed_input)
  #   pdo.unpack_input(packed_input)
    
  print(f"Slot Command: {pdo.slot_command_in}")
  print(f"Slot data: {pdo.slot_data_in}")
  print(f"Slot Aux: {pdo.slot_aux_in}")


  # Read INPUT PDO
      
  time.sleep(.5)
    
ec.close_ec()