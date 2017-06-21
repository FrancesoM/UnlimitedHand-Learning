import numpy as np
import matplotlib.pyplot as plt
import utilities as ut

def moving_average(data,samp_for_average):
    n_windows = int(len(data)/samp_for_average)
    for i in range(n_windows):
        data[i*samp_for_average:(i+1)*samp_for_average] = np.average(data[i*samp_for_average:(i+1)*samp_for_average])

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

#graph_data = open('03up_down.txt','r').read()
#activity_data = open(thread_dataup-down.txt).read()


colorarray = ['b','g','r','c','m','y','k','0.75']

mode = {'polso_piegato_alto':[0,1,4],   #estensori
        'polso_piegato_basso':[2,3,7],   #flessori
        'polso_ruotato_esterno':[0,3],  #ulnari
        'polso_ruotato_interno':[1,2],  #radiali
        'updown':[0,1],
        'intest':[2,3],
        'tutto':range(8)}

""" *************************** load data ***************************** """
up = 1
if(up):
    active_channels = mode['tutto']
    number_channels = len(active_channels)
    
    data = ut.load_data_into_matrix('model_updown.txt',19,-1,8)
    data_for_activity = ut.load_data_into_matrix('thread_dataupdown.txt',0,-1,4)
else:
    active_channels = mode['tutto']
    number_channels = len(active_channels)
    
    data = ut.load_data_into_matrix('model_intest.txt',19,-1,8)
    data_for_activity = ut.load_data_into_matrix('thread_dataintest.txt',0,-1,4)

""" **************************** graph data **************************** """

#lines = graph_data.split('\n')
#lines_act = activity_data.split('\n')
#
#
#n_lines = (len(lines))
#data = np.zeros((n_lines-20,8),dtype=float)
#
#i=0
#j=0
#
#for line in lines[19:-1]: #the last acquisition may be corrupted, sudden termination of serial comm
#    if(len(line)>1):
#        
#        t = line.split(',')
#        for value in t:
#            
#            data[i,j] = t[j]
#            j+=1
#        j=0
#        i+=1


#low pass - mobile average
 
x = np.arange(0,data.shape[0])

fig, ax = plt.subplots(number_channels)
ax_counter = 0
for col in active_channels:

    y = data[:,col]
    moving_average(y,1)
    ax[ax_counter].plot(x,y)
    ax_counter += 1
        
fig2, ax2 = plt.subplots(1,1)
for p in active_channels:
    
    y = data[:,p]
    moving_average(y,30)
    ax2.plot(x,y,color=colorarray[p],label='ch'+str(p))

legend = ax2.legend(loc='upper left', shadow=True)
    
ya=[]
ym=[]
for line in data_for_activity:
    #x = np.arange(line[0],line[1])
    for i in range(int(line[1]-line[0])):
        ya.append(line[2])
        ym.append(line[3])
    
ax2.plot(ya,color='black')
ax2.plot(ym,color='c')
    

plt.show()
    