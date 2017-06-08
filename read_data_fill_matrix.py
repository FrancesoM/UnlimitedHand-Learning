# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import math



def read(channels,duration,name="Default",port="COM3",baud=115200,message=None):
    
    ser = serial.Serial(port,baud,timeout=1)
    #we hypothesize that each rep takes 0.28 seconds, this is the lowest time recorder from actual measurements
    #to be as pessimistic as possible, therefore if we want a duration D, the matrix dim will be ceil(D/0.28)
    estimated_measure_time = 0.283
    repetitions = math.ceil(duration/estimated_measure_time)
    print(repetitions)
    data_matrix = np.zeros([repetitions+1,len(channels)])
    
    col = 0
    for i in channels:
        data_matrix[0][col] = i
        col=col+1
    
    print("############",name)
    print("############","reading channels: ",channels)
    if(message): print("############",message)

    rep = 1
    total_time = 0
    
    #start receiving values
    ser.write(b'v')
    print("\n","*****************","start","*****************")
    
    while(total_time<duration):
        
        start_time = time.time()
        
        #print("Channel: ",)
        data = str(ser.readline())
        if(len(data) > 30):
             #print( data )
             data = data.split("-")
             ch = 0
             channel_col = 0
             for d in data: #iterates over elements splitteed
                 #print( d,ch )
                 #this may be tricky,consider this:
#                a
#                Out[26]: array([ 11,  12,  12,  14,  15,  16,  21, 141])
#                
#                12 == a
#                Out[27]: array([False,  True,  True, False, False, False, False, False], dtype=bool)
#                
#                any(12==a)
#                Out[28]: True
#                
#                any(1==a)
#                Out[29]: False    
                 #we just want the ch in channels
                 
                 if(any(ch == channels)):
                     
                     try:
                         #if the data contains a letter it could be the first
                         #and therefore it is b'xxx, so we have to remove b' or
                         #it could be the last: xxx\n' ", so we have to remove
                         #the last three unwanted characters, that's exactly what this
                         #try - except chain does.
                         data_matrix[rep][channel_col] = int(d)
                         #print("dato: ",int(d),"element: ",i,ch)
        #                break
                     except ValueError:
                         try:
                             #print("dato: ",int(d[2:]),"element: ",i,ch)
                             data_matrix[rep][channel_col] = int(d[2:])
                         except ValueError:
                             #print("dato: ",int(d[:-3]),"element: ",i,ch)
                             data_matrix[rep][channel_col] = int(d[:-3])
                     channel_col = channel_col +1
                    
                 ch = ch+1
                    
        
        rep = rep+1
        elapsed_time = time.time()-start_time
        print("time for this measure: ",elapsed_time)
        total_time = total_time + elapsed_time
    
    print("\n","*****************","End at:",total_time,"*****************")
    ser.close()
    
    #print(data_matrix)
    
    return(data_matrix)

def atob(a,b):
    r = np.zeros(b-a+1,dtype='int_')
    x = 0
    for i in range(a,b+1):
        r[x] = i 
        x=x+1
    return r

if __name__ == "__main__":
    
    
    duration = 20
    #show the entire matrix when printing 
    np.set_printoptions(threshold=1000)
    channels = atob(0,7)
    mat = read(channels,duration,name="Up-Down",message="move wrist up and down for 30 seconds" )
    print(mat)

    plt.figure(1)
    for ch in range(0,len(channels)):
        plt.subplot(4,2,ch+1)
        plt.tight_layout()
        plt.xlabel('time [s]',fontsize=5)
        plt.ylabel("ch: "+str(ch),fontsize=5)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)
        plt.plot(atob(0,len(mat[:,0])-1), mat[:,ch] , 'k')
    
    plt.savefig('a.png',dpi=500)
