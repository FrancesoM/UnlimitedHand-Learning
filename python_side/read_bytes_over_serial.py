# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 13:11:44 2017

@author: Francesco
"""

import serial
import numpy as np
import time


PORT = "COM3"
BAUD = 115200
port = serial.Serial(PORT,BAUD,timeout=1)

START = 1
#BUNDLE SHAPE: |!|!|!|CH0_msb|CH0_lsb|ch1_msb|ch1_lsb|......|ch7_lsb|!|!|!|

NUM_CHANNELS = 8
END_BUNDLE_BYTE = 3
BYTE_PER_CHANNEL = 2 #two bytes to represent int
BUNDLE_LENGTH = NUM_CHANNELS*BYTE_PER_CHANNEL

data = np.zeros(NUM_CHANNELS)

graph_data = open('samplefile.txt','w')
print("3..")
time.sleep(0.5)
print("2..")
time.sleep(0.5)
print("1..")
time.sleep(0.5)
print("Starting")

while(START):
    try:
        start_time = time.time()
        if(port.read(END_BUNDLE_BYTE).decode("raw_unicode_escape") == '!!!'):
            temp = port.read(BUNDLE_LENGTH)
            
            for channel in range(0,NUM_CHANNELS):
                data[channel] = (temp[channel*BYTE_PER_CHANNEL]<<8)|(temp[channel*BYTE_PER_CHANNEL + 1 ])
                #print(data)
                graph_data.write(str(data[0]))
                for value in data[1:]:
                    graph_data.write(',')
                    graph_data.write(str(value))
                graph_data.write('\n')
                #time.sleep(0.1)
    except KeyboardInterrupt:
        print("Closing")
        port.close()
        graph_data.close()
        break
    
    
        