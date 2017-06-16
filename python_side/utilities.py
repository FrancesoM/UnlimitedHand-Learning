# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 09:32:16 2017

@author: Francesco
"""

from sklearn.cluster import AffinityPropagation
import numpy as np
import threading as th
import time
import re

def open_outfile(file,rep):
    f = open(file,'r').read()
    lines = f.split('\n')
    first_matrix = lines[rep].split('\t')[:-1]
    matrix = np.array(re.findall("\d+\.\d+",first_matrix[0]),dtype='f')
    
    for row in first_matrix[1:]: #the first has alread been taken
        try:
            temp = np.array(re.findall("\d+\.\d+",row),dtype='f')
            matrix = np.vstack((matrix,temp))
        except ValueError:
            print(row)
    
    return matrix

#load data
def load_data_into_matrix(file):
    graph_data = open(file,'r').read()
    
    lines = graph_data.split('\n')
    n_channels = 8
    n_lines = (len(lines))
    data = np.zeros((n_lines - 20,n_channels)) #read all channels (8), plot only the desired
    i=0
    j=0
    
    #the last acquisition may be corrupted, sudden termination of serial comm
    #the first lines may be corrupted by giggering of the sensors/serial reads garbage
    for line in lines[19:-1]: 
        if(len(line)>1):
            t = line.split(',')
            for value in t:
                data[i,j] = t[j]
                j+=1
            j=0
            i+=1
    
    return data
    
def unsigned_derivative(x_t,x_tmen1):
    return np.abs((x_t - x_tmen1)/x_t)

colorarray = ['b','g','r','c','m','y','k','0.75']

mode = {'polso_piegato_alto':[0,1,4],   #estensori
        'polso_piegato_basso':[2,3,7],   #flessori
        'polso_ruotato_esterno':[0,3],  #ulnari
        'polso_ruotato_interno':[1,2]}  #radiali
        
class track(object):
    def __init__(self,data):
        self.data = data
        self.channels = data.shape[1] #number of channels
        self.samples = data.shape[0] #number of samples
        
    def set_baseline(self,number_of_samples = 30):
        #define the baseline for each channel, with this code we
        #don't care about how many channels are there, 2 or 3 or n
        #the shape of baseline will be 1xn
        #basically this code is doing this: for each column sum the first
        #30 values and do the average, the subtract this value from
        #all the values
        self.baseline = np.sum(self.data[0:number_of_samples,:],axis=0)/number_of_samples
        self.data -= self.baseline
        
    def __getitem__(self,index):
        return self.data[index[0]][index[1]]
    
    def read_channel(self,channel):
        return self.data[:,channel]
    
    def shape(self):
        return self.data.shape
        

class computation(th.Thread):
    def __init__(self,name,track_agonist,track_antagonist):
        th.Thread.__init__(self)
        self.track_agonist = track_agonist
        self.track_antagonist = track_antagonist
        self.name = name
        
    def run(self):
        #we use alto/basso together with esterno/interno since
        #they aren't mutual exclusive movements, the wirst can 
        #in fact go up while it may be extern/intern, but cannot go
        #up while it is down
        
        #we somehow simulate the fact that we are reading a stream of data
        #so we don't use all the data together, but once more at each step
        
        #feature extraction: position: baseline and movement: derivative
        
        #t represents time that goes by
        
        windows_length = 100
        n_chann = self.track_agonist.shape()[1]
        position = 0
        line = 0
        
        outfile = open('thread_data'+self.name+'.txt','w')
        #outfilerrr = open('prova_pos'+self.name+'.txt','w')
        
        print("%s: samples %d, channels %d"%(self.name,self.track_agonist.shape()[0],self.track_agonist.shape()[1]) )
        while(position <= self.track_agonist.shape()[0] - windows_length):
            #start_time = time.time()
            #print(t)
            
            #obtain the features, position and movement
            #axis = 0 is used to have the mean for the columns, aka during the 50 samples
            temp_agonist = (self.track_agonist[position:position+windows_length,:])
            temp_antagonist = (self.track_antagonist[position:windows_length,:])

            
            #separation in the plane/space
            #assume we have 2 channels
            #we should plot win1_position[0] against win1_position[1]
            #and win2_position[0] against win2_position[2] since they
            #represent a point into the "channel spanned space"
            
            X_pos = np.vstack((temp_agonist,temp_antagonist))
            #X_mov = np.concatenate((win1_movement,win2_movement),axis=0)
#            if (position == 0 and self.name=='up-down'):
#                print(X_pos)
#                print(temp_agonist)
#                print(temp_antagonist)
#            
            try:            
                af_pos = AffinityPropagation(preference=-2).fit(X_pos)
                cluster_centers_indices_pos = af_pos.cluster_centers_indices_
                #labels = af.labels_
            except ValueError:
                
                print("X_POS:\n",X_pos)
                print("Position:\n",position)
            #af_mov = AffinityPropagation(preference=-2).fit(X_mov)
            #cluster_centers_indices_mov = af_mov.cluster_centers_indices_
            for val in X_pos:
                outfile.write(str(val)+'\t')
                
            try:
                n_clusters_pos = len(cluster_centers_indices_pos)
                outfile.write(str(n_clusters_pos))
            except TypeError:
                #print("%s: Cannot find any suitable cluster. Cluster number = 0\n"%self.name)
                outfile.write(str(0))
                
#            outfile.write(',')
#            
#            try:
#                n_clusters_mov = len(cluster_centers_indices_mov)
#                outfile.write(str(n_clusters_mov))
#            except TypeError:
#                outfile.write(str(0))
                
                
#                if (n_clusters_pos > 1 ):
#                    print("%s: Position is discriminated. Cluster number = %d"%(self.name,n_clusters_pos))
#                else:
#                    print("%s: Only one cluster for position"%self.name)
#                if (n_clusters_mov > 1):
#                    print("%s: Movement is discriminated. Cluster number = %d"%(self.name,n_clusters_mov))
#                else:
#                    print("%s: Only one cluster for movement"%self.name)
             

#            if ( t > 50 and t < 100):
#                
#                for r in X_pos:
#                    for c in r:
#                        outfilerrr.write(str(c))
#                        outfilerrr.write(',')
#                    outfilerrr.write('\n')
#                outfilerrr.write(str(n_clusters_pos))
#                outfilerrr.close()

            #slide window
            position += windows_length
            print(line)
            line += 1
            outfile.write('\n')
            #print(time.time()-start_time)
            
        outfile.close()
        
        
"""
*********************** MAIN **********************

"""
        
class offline_process(object):
    
    def __init__(self,filename):
        """ LOAD DATA """
        data = load_data_into_matrix(filename)
        
        """ DIVIDE INTO MEANINGFUL CHANNELS """
        self.polso_alto_track = track(data[:,mode['polso_piegato_alto']])
        self.polso_basso_track = track(data[:,mode['polso_piegato_basso']])
        self.polso_esterno_track = track(data[:,mode['polso_ruotato_esterno']])
        self.polso_interno_track = track(data[:,mode['polso_ruotato_interno']])
        
        """ REMOVE BASELINE """
        self.polso_alto_track.set_baseline()
        self.polso_basso_track.set_baseline()
        self.polso_esterno_track.set_baseline()
        self.polso_interno_track.set_baseline()
        
        """ START TWO THREADS TO COMPUTE"""

        self.thread_updown = computation("up-down",self.polso_alto_track,self.polso_basso_track)
        self.thread_leftright = computation("left-right",self.polso_esterno_track,self.polso_interno_track)

        
    def __call__(self):
        #start a thread for each computation, which is left-right or
        #up down
        
        try:
            self.thread_updown.start()
            self.thread_leftright.start()
        
            self.thread_updown.join()
            self.thread_leftright.join()
        except KeyboardInterrupt:
            
            self.thread_leftright.join()
            self.thread_updown.join()
        

if __name__ == "__main__":
    
    p = offline_process("still_poisitions.txt")
    p()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
