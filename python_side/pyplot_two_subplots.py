import numpy as np
import matplotlib.pyplot as plt

def split_file(file,n):
    lines = file.split('\n')
    
    n_lines = (len(lines))
    data = np.zeros((n_lines-20,n))
    
    i=0
    j=0
    
    for line in lines[19:-1]: #the last acquisition may be corrupted, sudden termination of serial comm
        if(len(line)>1):
            print(line)
            t = line.split(',')
            for value in t:
                print(t)
                data[i,j] = t[j]
                j+=1
            j=0
            i+=1
        
        return data

graph_data = open('still_poisitions.txt','r').read()
lefrig = open('thread_dataleft-right.txt','r').read()
updown = open('thread_dataup-down.txt','r').read()


colorarray = ['b','g','r','c','m','y','k','0.75']

mode = {'polso_piegato_alto':[0,1,4],   #estensori
        'polso_piegato_alto':[2,3,7],   #flessori
        'polso_ruotato_esterno':[0,3],  #ulnari
        'polso_ruotato_interno':[1,2],  #radiali
        'tutto':range(8)}

active_channels = mode['polso_ruotato_esterno']
number_channels = len(active_channels)


""" **************************** graph data **************************** """

lines = graph_data.split('\n')

n_lines = (len(lines))
data = np.zeros((n_lines-20,8))

i=0
j=0

for line in lines[19:-1]: #the last acquisition may be corrupted, sudden termination of serial comm
    if(len(line)>1):
        
        t = line.split(',')
        for value in t:
            
            data[i,j] = t[j]
            j+=1
        j=0
        i+=1

        
x = np.arange(0,data.shape[0])

fig, ax = plt.subplots(number_channels)

ax_counter = 0
for row in active_channels:
    #for col in range(2):
        #filter out the first 20 values and the last 5, which can be corrupted
        #take data only from the cols
    y = data[:,row]
    ax[ax_counter].plot(x,y)
    ax_counter += 1
        
fig2, ax2 = plt.subplots(1,1)
for p in active_channels:
    y = data[:,p]
    ax2.plot(x,y,color=colorarray[p])
    

plt.show()
    