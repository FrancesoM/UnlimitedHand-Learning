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


while(START):
    try:
        start_time = time.time()
        if(port.read(END_BUNDLE_BYTE).decode("raw_unicode_escape") == '!!!'):
            temp = port.read(BUNDLE_LENGTH)
            
            for channel in range(0,NUM_CHANNELS):
                data[channel] = (temp[channel*BYTE_PER_CHANNEL]<<8)|(temp[channel*BYTE_PER_CHANNEL + 1 ])
                print(data)
    except KeyboardInterrupt:
        port.close()
        break
    
    
        