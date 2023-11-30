# Test Vector Box interface with windows - WORKS WITH V45_S3
import can
import time

bus = can.interface.Bus(bustype='vector',channel='0',bitrate=500000)

data_array = [1,2,3,4,5,6,7,8]

while(1):    
    for i in range(len(data_array)):
        data_array[i] = data_array[i]+1
    
    msg = can.Message(data=data_array,dlc=8,is_extended_id=False)
    msg.arbitration_id = 0x04
    bus.send(msg)
    time.sleep(1)