# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 09:32:16 2017

@author: Francesco
"""

from sklearn.preprocessing import StandardScaler
import numpy as np
import threading as th
import time
import re
import matplotlib.pyplot as plt

def load_dataset(file):
    
    n_channels = 8
    
    f = open(file,'r')
    #jump to the second block(the first is corrupted)
    while(1):
        if(f.read(1) == '-'):
            start = f.tell()+2
            break
    f.seek(start)
    #now we are ready to read the first block, which is the first feature actually
    #understand the block length, must be equal for each block
    dataset = f.read()
    n_linee = 0
    
    for line in dataset.split('\n'):
        n_linee+=1
        if(line == '-'):
            n_linee -= 1
            break
    len_blocco = n_linee+1
    
    #create the structure that will hold the features
    #each feature is a matrix n_linee*9 (n_channels + classe movimento)
    
    n_blocks = (len(dataset.split('\n'))-1)/len_blocco
    
    features = np.zeros((n_linee,n_channels+1,int(n_blocks)+1))
    
    i = 0
    j = 0
    block = 0
    for line in dataset.split('\n'):
        if(len(line)<5):
            block+=1
            i = 0
            #print(line)
        else:
            for value in line.split(','):
                features[i,j,block] = value
                j+=1
            #print(line)
            j=0
            i+=1
    
    return features
    
    
def gradient(data,channels):
    der = np.zeros((len(data),channels))
    for i in range(1,len(data)):
        der[i,:] = data[i,:]-data[i-1,:]
    return der

def moving_average(data,samp_for_average):
    n_windows = int(len(data)/samp_for_average)
    for i in range(n_windows):
        data[i*samp_for_average:(i+1)*samp_for_average] = np.average(data[i*samp_for_average:(i+1)*samp_for_average])


def open_outfile(file,rep):
    f = open(file,'r').read()
    lines = f.split('\n')
    info_decoded = lines[rep].split('\t')
    first_matrix = info_decoded[:-1]
    n_cluster = int(info_decoded[-1])
    #this code fails when there is a number without decimals, because 2. doesn't match the pattern
    #since it searches for another number after the dot, that's the reason why the second "try"
    #to catch this behaviour we say that two possible patterns may exist, 3.0 is recognized as well as 3.
    patterns=re.compile(r'-\d+\.\d+|\d+\.\d+|-\d+\.|\d+\.')
    #as a note: we search for both positive or negative(minus sign) but the order is important,
    #because if -\d+\. was before -\d+\.\d+, the number -2.3 would be recognized as -2.
    matrix = np.array(patterns.findall(first_matrix[0]),dtype='f')
    
    for row in first_matrix[1:]: #the first has alread been taken
        try:
            temp = np.array(patterns.findall(row),dtype='f')
            matrix = np.vstack((matrix,temp))
        except ValueError:
            print("Error:",row)
    
    return (matrix,n_cluster)

#load data
def load_data_into_matrix(file,startline=0,endline=-1,cols=8,mode="signal"):
    graph_data = open(file,'r').read()
    
    lines = graph_data.split('\n')
    n_channels = cols
    n_lines = (len(lines))
    vertical_lines = len(lines[startline:endline])
    data = np.zeros((vertical_lines,n_channels)) #read all channels (8), plot only the desired

    
    #the last acquisition may be corrupted, sudden termination of serial comm
    #the first lines may be corrupted by giggering of the sensors/serial reads garbage
    if mode == "signal":
        i=0
        j=0
        for line in lines[startline:endline]: 
            if(len(line)>1):
                t = line.split(',')
                for value in t:
                    data[i,j] = t[j]
                    j+=1
                j=0
                i+=1
        
        return data
    
    if mode == "encoded":
        i=0
        j=0
        data = np.chararray((n_lines - (startline-endline),n_channels))
        for line in lines[startline:endline]: 
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
        'polso_ruotato_interno':[1,2],  #radiali
        'updown':[0,1],
        'intest':[2,3],
        'tutti':range(8)}
        
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
        
    def moving_avg(self,samp_for_average):
        n_windows = int(len(self.data)/samp_for_average)
        for s in range(self.channels):
            for i in range(n_windows):
                self.data[i*samp_for_average:(i+1)*samp_for_average,s] = np.average(self.data[i*samp_for_average:(i+1)*samp_for_average,s])
        
    def __getitem__(self,index):
        return self.data[index[0]][index[1]]
    
    def read_channel(self,channel):
        return self.data[:,channel]
    
    def shape(self):
        return self.data.shape
        

class computation(th.Thread):
    def __init__(self,name,signal):
        th.Thread.__init__(self)
        self.signal = signal
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
        """ !!!! MUST BE A MULTIPLE OF 10 !!!! """
        windows_length = 10
        n_chann = self.signal.shape()[1]
        encoder = (lambda Y: 'a' if Y > windows_length/100 else 'b' if Y > -windows_length/100 else 'c')
        
        encoded = ['x']*8
                         
        t = 0
        
        outfile = open('thread_data'+self.name+'.txt','w')
        #outfilerrr = open('prova_pos'+self.name+'.txt','w')
        
        
        flag = 1
        
        print("%s: samples %d, channels %d"%(self.name,self.signal.shape()[0],self.signal.shape()[1]) )
        try:
            while(1):
      
                der_ = self.signal[t,:] - self.signal[t+windows_length,:]
                #print(der_[0], self.signal[t,0], self.signal[t+windows_length,0] )
                #se deltaY > deltaX .... calcoli sul quaderno,
                #qua aggiungo solo deltaX è sempre "window length" perchè è la distanza alla quale sono presi i punti
                
                i=0
                encoded[0] = encoder(der_[0])
                outfile.write("%c"%encoded[0])
                for i in range(1,8):
                    encoded[i] = encoder(der_[i])
                    outfile.write(',')
                    outfile.write("%c"%encoded[i])  
                    
     
                #slide window
                t += windows_length #deve essere almeno superiore alla media mobile
                
                #print(line)
                flag+=1
                outfile.write('\n')
                #print(time.time()-start_time)
        
        except IndexError:
                
            outfile.close()
            print(flag)
        
"""
*********************** MAIN **********************

"""
        
class offline_process(object):
    
    def __init__(self,filename):
        """ LOAD DATA """
        data = load_data_into_matrix(filename,0,-1,8)
        
        """ DIVIDE INTO MEANINGFUL CHANNELS """
        self.polso_updown = track(data[:,mode['tutti']])
        #self.polso_intest = track(data[:,mode['intest']])
        
        """ REMOVE BASELINE """
#        self.polso_alto_track.set_baseline()
#        self.polso_basso_track.set_baseline()
#        self.polso_esterno_track.set_baseline()
#        self.polso_interno_track.set_baseline()

        """ LOW PASS FILTER """
        self.polso_updown.moving_avg(10)
        #self.polso_intest.moving_avg(30)        
        
        
        """ START TWO THREADS TO COMPUTE"""

        self.thread_updown = computation("-encoding",self.polso_updown)
        #self.thread_leftright = computation("intest",self.polso_updown)

        
    def __call__(self):
        #start a thread for each computation, which is left-right or
        #up down
        
        try:
            self.thread_updown.start()
            #self.thread_leftright.start()
        
            self.thread_updown.join()
            #self.thread_leftright.join()
        except KeyboardInterrupt:
            
            self.thread_updown.join()
            #self.thread_leftright.join()        

class occurrence_table(object):
    def __init__(self):
        self.items = []
        self.number_of_occurrence = []
        self.l = 0
        self.total = 0
    def __repr__(self):
        return "Object filled with %d items"%self.l
    def __str__(self):
        for i in range(self.l):
            print("%s: %d"%(self.items[i],self.number_of_occurrence[i]))
        return "----- End ------ "
    def append(self,item):
        j=0
        for occurrence in self.items:
            if occurrence != item:
                j=j+1
            else:
                self.number_of_occurrence[j]+=1
                self.total += 1
                return
        #se hai fatto tutto il for senza entrare nell'else vuol
        #dire che è nuovo, quindi lo appendo
        self.items.append(item)
        #ovviamente metto nel conteggio che ne ho aggiunto uno
        self.number_of_occurrence.append(1)
        self.l += 1
        self.total += 1
        #conteggio e item sono due liste separate ma l'elemento
        #j esimo di number_of.. indica quante volte l'elemento
        #j esimo di items è presente
    
    def get(self):
        return (self.items,self.number_of_occurrence)
    
    def prob(self):
        temp = [1]*self.l
        for i in range(self.l):
            temp[i] = self.number_of_occurrence[i]/self.total
        
        return temp

if __name__ == "__main__":
    
    
    p = offline_process("model_updown.txt")
    p()
    
    encoded_signal = load_data_into_matrix("thread_data-encoding.txt",mode="encoded")

    entropy = lambda p: 0 if p==0 else -p*np.log2(p)
    
    symbols_taken = 3
    n_samples = encoded_signal.shape[0]
    window_len = 30
    start = 0
    start_for_plot = 0
    
    channel = encoded_signal.shape[1]
    
    
    n_steps= window_len - symbols_taken + 1
    
    print("n_steps:",n_steps)
    

    ch = np.zeros((n_samples - window_len,channel),dtype='f')
    
    outfile = open('entropy.txt','w')

    while(start < n_samples - window_len):
        table = []
        for i in range(channel):
            table.append(occurrence_table())
        
        window = encoded_signal[start:start+window_len,:]
        for i in range(n_steps):
            for j in range(channel):
                table[j].append(window[i:i+symbols_taken,j].tostring())
        
        entropy_per_channel = [0]*channel #il massimo dell'entropia quando ho tutto uguale, 3**3 perchè ho 3 simboli per 3 posizioni
        
        for j in range(channel):
            list_of_prob = table[j].prob()
            #print(list_of_prob)
            for i in range(len(list_of_prob)):
                entropy_per_channel[j] += entropy(list_of_prob[i])
            
            ch[start_for_plot,j] = entropy_per_channel[j]
            outfile.write(str(entropy_per_channel[j]))
            outfile.write('\t')
            
        start += 1
        start_for_plot += 1
        outfile.write('\n')
        #print(table[0])
            
    outfile.close()
    
    fig2, ax2 = plt.subplots(1,1)
    for p in range(channel):
        
        y = ch[:,p]
        ax2.plot(y,color=colorarray[p],label='ch'+str(p))
    
    legend = ax2.legend(loc='upper left', shadow=True)
    
    plt.show()
    
    
    
    #
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
