# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 13:11:44 2017

@author: Francesco
"""

import serial
import numpy as np
import time


PORT = "COM10"
BAUD = 115200
port = serial.Serial(PORT,BAUD,timeout=1)

START = 1
#BUNDLE SHAPE: |!|!|!|CH0_msb|CH0_lsb|ch1_msb|ch1_lsb|......|ch7_lsb|!|!|!|

NUM_CHANNELS = 8
END_BUNDLE_BYTE = 3
BYTE_PER_CHANNEL = 2 #two bytes to represent int
BUNDLE_LENGTH = NUM_CHANNELS*BYTE_PER_CHANNEL

data = np.zeros(NUM_CHANNELS)

graph_data = open('dataset.txt','w')

print("Gathering recordings for dataset")


movement_time = 2.5 #2.5 seconds for each movement
counter = 0
while(START):
    try:
        
        movement = input("\n\
                          0: wristle up\n\
                          1: wristle down\n\
                          2: wristle rotation out\n\
                          3: wristle rotation inside\n\
                          4: hand open\n\
                          5: hand closed\n")
        if(movement == 's'):
            graph_data.close()
            port.close()
            break
        
        start_time = time.time()
        elapsed = 0
        while(elapsed < movement_time):
            if(port.read(END_BUNDLE_BYTE).decode("raw_unicode_escape") == '!!!'):
                temp = port.read(BUNDLE_LENGTH)
                
                for channel in range(0,NUM_CHANNELS):
                    data[channel] = (temp[channel*BYTE_PER_CHANNEL]<<8)|(temp[channel*BYTE_PER_CHANNEL + 1 ])
                    #print(data)
                    for value in data:
                        graph_data.write(str(value))
                        graph_data.write(',')
                    graph_data.write(movement+'\n')
                    time.sleep(0.01) #constant sampling time
            elapsed = time.time() - start_time         
            graph_data.write('-\n')
                
    except KeyboardInterrupt:
        print("Closing")
        port.close()
        graph_data.close()
        break
    
    
        