# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 19:28:43 2017

@author: Francesco
"""
import utilities as ut
import numpy as np
import matplotlib.pyplot as plt

def moving_average(data,samp_for_average):
    n_windows = int(len(data)/samp_for_average)
    for i in range(n_windows):
        data[i*samp_for_average:(i+1)*samp_for_average] = np.average(data[i*samp_for_average:(i+1)*samp_for_average])


#D = ut.load_dataset('
#movement_kind = ["wrist up",
#                 "wrist down",test_100Hz.txt')
#
#                 "wrist rotation out",
#                 "wrist rotation inside",
#                 "hand open",
#                 "hand closed"]                      
#
#active_channels = ut.mode['tutti']
#
#X = D[:,:-1,:]
#classification = D[-1,-1,:]

X,classification = ut.load_from_C_formatting('test.txt')

figures = []
double = 1
for movement in np.unique(classification):
    
    #questa sintassi strana prende gli indici per i quali 
    #il movimento è "movement" ma dato che voglio plottare
    #solo un movimento per tipo, prendo il primo della lista
    
    
    figures.append(plt.subplots(1,1))
    for p in active_channels:
        y = X[:,p,(classification==movement)]
        y = y[:,0]
        moving_average(y,10)
        
        #figures è una tupla (fig,axes) e noi dobbiamo
        #plottare su axes
        movement = int(movement)
        figures[movement][1].plot(y,color=ut.colorarray[p],label='ch'+str(p))
        
    legend = figures[movement][1].legend(loc='upper left', shadow=True)
    figures[movement][0].suptitle(movement_kind[movement])
    
if double:
    
    ddfigures = []
    for movement in np.unique(classification):
        
        #questa sintassi strana prende gli indici per i quali 
        #il movimento è "movement" ma dato che voglio plottare
        #solo un movimento per tipo, prendo il primo della lista
        
        
        ddfigures.append(plt.subplots(1,1))
        for p in active_channels:
            y = X[:,p,(classification==movement)]
            y = y[:,1]
            moving_average(y,10)
            #ddfigures è una tupla (fig,axes) e noi dobbiamo
            #plottare su axes
            movement = int(movement)
            ddfigures[movement][1].plot(y,color=ut.colorarray[p],label='ch'+str(p))
            
        legend = ddfigures[movement][1].legend(loc='upper left', shadow=True)
        ddfigures[movement][0].suptitle(movement_kind[movement])

plt.show()