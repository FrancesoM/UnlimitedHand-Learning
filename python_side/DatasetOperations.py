# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 16:01:00 2017

@author: Francesco
@title: Open the dataset, save values in a numpy matrix
"""
import numpy as np
import matplotlib.pyplot as plt

global SAMPLE_PER_MOVEMENT
SAMPLE_PER_MOVEMENT = 200
global N_CHANNELS
N_CHANNELS = 8
global BYTES_PER_SHORT
BYTES_PER_SHORT = 2

BYTES_PER_MOVEMENT = SAMPLE_PER_MOVEMENT*N_CHANNELS*BYTES_PER_SHORT

HEADERLENGTH = 100
NAMEOFFSET = 0
NAMELENGTH = 50
SIZEOFFSET = 50
SIZELENGHT = 50
DATAOFFSET = 100

class definitions(object):
    def __init__(self):
        self.movement_kind = ["wrist up",
                 "wrist down",
                 "wrist rotation out",
                 "wrist rotation inside",
                 "hand open",
                 "hand closed"]
        
        self.colorarray = ['b','g','r','c','m','y','k','0.75']
        
        self.mode = {'polso_piegato_alto':[0,1,4],   #estensori
                     'polso_piegato_basso':[2,3,7],   #flessori
                     'polso_ruotato_esterno':[0,3],  #ulnari
                     'polso_ruotato_interno':[1,2],  #radiali
                     'updown':[0,1],
                     'intest':[2,3],
                     'tutti':range(8)}
        
def moving_average(data,samp_for_average):
    n_windows = int(len(data)/samp_for_average)
    for i in range(n_windows):
        data[i*samp_for_average:(i+1)*samp_for_average] = np.average(data[i*samp_for_average:(i+1)*samp_for_average])


def sizeofDataset(H):
    
    for b in H[NAMEOFFSET:NAMEOFFSET+NAMELENGTH]:
        if b == 0:
            pass
        else:
            print(chr(b), end='')
    
    print("\n")
    
    nmov = int(H[SIZEOFFSET] | 
              (H[SIZEOFFSET+1]<<8) | 
              (H[SIZEOFFSET+2]<<16) | 
              (H[SIZEOFFSET+3]<<24) )
    
    print("Number of movements: ",nmov)
    return DATAOFFSET + nmov*(BYTES_PER_MOVEMENT+1),nmov

def processData(D_mov):
        
    #D_mov è il movimento in byte, già pulito di tutto il resto, rimane solo
    #da mettere insieme i byte a coppie, ovviamente D_mov deve essere di 400 byte
    temp = np.zeros(SAMPLE_PER_MOVEMENT*N_CHANNELS,dtype='float')
    offset,pos = 0,0
    
    while(offset<BYTES_PER_MOVEMENT):
        temp[pos] = float( (D_mov[offset+1]<<8) | (D_mov[offset]) )
        offset+=BYTES_PER_SHORT
        pos+=1
        #remember that each value in temp corresponds to 2 bytes
        
    temp = temp.reshape((SAMPLE_PER_MOVEMENT,N_CHANNELS))
    
    return temp   
   

if __name__ == "__main__":
    
    """ ************************* OPEN DATASET ********************* """
    
    #by convention Y are the true values of the dataset X, what we are
    #trying to understand is a relationship between Y and X and we are 
    #trying to estimate a certain f:R^(n*m)->R^p -> f(X) = Y
    
    f = f = open("..\C++_side\SerialTutorial\Serial_Chapter3_tutorial\FrancescoDataset.bin","rb")
    H = f.read(HEADERLENGTH)
    
    S,lenY = sizeofDataset(H)
    
    f.seek(DATAOFFSET)
    
    D = f.read()
    
    #assert that we calculated well the end of file
    assert(S == f.tell() )
    
    Y = np.zeros(lenY,dtype='int');
    #+1 because of the adidtional byte due to the movement
    #the files has a regular scheme, so it is easy to address and find the
    #bytes that explain the movement
    pos = 0
    YPlaces = np.arange(0,lenY*(BYTES_PER_MOVEMENT+1),(BYTES_PER_MOVEMENT+1),dtype='int')
    for Yp in YPlaces:
        Y[pos] = D[Yp]
        pos+=1
        
    print(Y)
    
    #z,x,y intesi come assi
    X = np.zeros((lenY,SAMPLE_PER_MOVEMENT,N_CHANNELS))
    
    #check on the quaderno for the explanation
    start_index = 1
    for i in range(lenY):
        end_index = start_index + BYTES_PER_MOVEMENT
        #end index is excluded, but it is done automatically by the 
        #python way of indexing things
        X_raw = D[start_index:end_index]
        X[i,:,:] = processData(X_raw)
        start_index += BYTES_PER_MOVEMENT +1
    
    """ *********************** PLOT DATA ************************ """
    
    ut = definitions()
    active_channels = ut.mode['tutti']
    
    
    figures = []
    double = 1
    for movement in np.unique(Y):
        
        #questa sintassi strana prende gli indici per i quali 
        #il movimento è "movement" ma dato che voglio plottare
        #solo un movimento per tipo, prendo il primo della lista
        
        figures.append(plt.subplots(1,1))
        for p in active_channels:
            #notare che Y==movement mi da l'indice della matrice 
            #riferita a quel movimento
            #poi plotto un array alla volta, cioè il canale p e tutte le righe
            y = X[(Y==movement),:,p]
            
            #dato che Y==movement può dare più matrici (in effetti da 
            #tutte le matrici che hanno movimento == movement), ne prendiamo
            #solo la prima, a campione
            y = y[0,:]
            
            #se i dati sono rumorosi si può applicare un easy LP
            #moving_average(y,10)
            
            #figures è una tupla (fig,axes) e noi dobbiamo
            #plottare su axes, per questo il " [1]
            figures[movement][1].plot(y,color=ut.colorarray[p],label='ch'+str(p))
        
        #mettiamo la legenda usando movement_kind 
        legend = figures[movement][1].legend(loc='upper left', shadow=True)
        figures[movement][0].suptitle(ut.movement_kind[movement])
    
    
plt.show()



