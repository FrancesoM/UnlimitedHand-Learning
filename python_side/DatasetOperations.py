# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:01:00 2017

@author: Francesco
@title: Open the dataset, save values in a numpy matrix
"""
import numpy as np

global SAMPLE_PER_MOVEMENT
SAMPLE_PER_MOVEMENT = 200
global N_CHANNELS
N_CHANNELS = 8
global BYTES_PER_CHANNEL
BYTES_PER_CHANNEL = 2

HEADERLENGTH = 100
NAMEOFFSET = 0
NAMELENGTH = 50
SIZEOFFSET = 50
SIZELENGHT = 50
DATAOFFSET = 100

def printHeader(H):
    for b in H[NAMEOFFSET:NAMEOFFSET+NAMELENGHT]:
        if b == 0:
            pass
        else:
            print(chr(b), end='')

def sizeofDataset(H):
    nmov = int(H[SIZEOFFSET] | 
              (H[SIZEOFFSET+1]<<8) | 
              (H[SIZEOFFSET+2]<<16) | 
              (H[SIZEOFFSET+2]<<24) )
    
    print("Number of movements: ",nmov)
    return nmov*SAMPLE_PER_MOVEMENT*N_CHANNELS*BYTES_PER_CHANNEL

if __name__ == "__main__":
    
    f = f = open("..\C++_side\SerialTutorial\Serial_Chapter3_tutorial\BinaryDataset.bin","rb")
    H = f.read(HEADERLENGTH)
    
    f.seek(DATAOFFSET)
    
    


