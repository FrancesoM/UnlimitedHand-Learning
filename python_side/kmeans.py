# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 12:15:20 2017

@author: Francesco
"""
import numpy as np
import matplotlib.pyplot as plt

graph_data = open('test.txt','r').read()
data = np.empty(8)

figure, ax = plt.subplots(4,2)

lines = graph_data.split('\n')
for line in lines:
    if(len(line)>1):
        
        data = line.split(',')
        ys = np.roll(ys,-1) #shift left numbers
        ys[-1] = y   #change only the last
        time.sleep(0.1)
        
        
def take_delay(matrix,maxlines,delay=3):
    