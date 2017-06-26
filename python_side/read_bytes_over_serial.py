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

graph_data = open('test_100Hz.txt','w')

print("Gathering recordings for dataset")


movement_time = 2 #2.5 seconds for each movement
sample_time = 0.01 # 100Hz sample frequency
num_samples = int(movement_time/sample_time)
#num_samples = 300
counter = 0
while(START):
    try:
        #print("Flushing")
        #port.flushInput()
        
        movement = input("\n\
                          0: wrist up\n\
                          1: wrist down\n\
                          2: wrist rotation out\n\
                          3: wrist rotation inside\n\
                          4: hand open\n\
                          5: hand closed\n")
        if(movement == 's'):
            graph_data.close()
            print(port.inWaiting())
            port.close()
            break
        
        #start communication, for some reason with utf-8 it works
        
        
        #start_time = time.time()
        elapsed = 0
        counter = 0
        starttime = time.time()
        
        while(elapsed < 2):
            port.write('s'.encode('utf-8'))
            a = port.read(END_BUNDLE_BYTE)
            #print(a)
            if(a.decode("raw_unicode_escape") == '!!!'):
                temp = port.read(BUNDLE_LENGTH)

                #unpack values and put them in "data"
                for channel in range(0,NUM_CHANNELS):
                    value = (temp[channel*BYTE_PER_CHANNEL]<<8)|(temp[channel*BYTE_PER_CHANNEL + 1 ])
                    graph_data.write(str(value))
                    graph_data.write(',')
                    #print(value)
                    
                #start a new line in the file
                graph_data.write(movement+'\n')
            
                #wait the sample time to get a new value
                #time.sleep(sample_time) 
                elapsed = time.time() - starttime
                #è allineato con l'if
                #perchè deve aumentare il counter solo quando scrive
                #counter += 1
                #port.write('o'.encode('utf-8'))
                #print(port.inWaiting())
        
        #write the separator between one movement and the other
        graph_data.write('-\n')
        #any character except 's' is ok to stop the communication
        #port.write('o'.encode('utf-8')) 
        print("Movement Acquired - Elapsed Time: %d"%movement_time)
                
    except KeyboardInterrupt:
        print("Closing")
        port.close()
        graph_data.close()
        break
    
    
        