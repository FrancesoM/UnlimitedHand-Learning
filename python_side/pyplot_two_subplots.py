import numpy as np
import matplotlib.pyplot as plt

graph_data = open('samplefile.txt','r').read()

colorarray = ['b','g','r','c','m','y','k','0.75']

lines = graph_data.split('\n')

n = (len(lines))
data = np.zeros((n,8))
i=0
j=0

x = np.arange(0,n-25)

for line in lines[:-1]: #the last acquisition may be corrupted, sudden termination of serial comm
    if(len(line)>1):
        t = line.split(',')
        for value in t:
            data[i,j] = t[j]
            j+=1
        j=0
        i+=1
        
fig, ax = plt.subplots(4,2)
for row in range(4):
    for col in range(2):
        #filter out the first 20 values and the last 5, which can be corrupted
        y = data[20:-5,row*2+col]
        ax[row][col].plot(x,y)
        
fig2, ax2 = plt.subplots(1,1)
for p in range(8):
    y = data[20:-5,p]
    ax2.plot(x,y,color=colorarray[p])
    
    
legend = ax2.legend(['ch1','ch2','ch3','ch4','ch5','ch6','ch7','ch8' ], loc='upper left')
    
for label in legend.get_texts():
    label.set_fontsize('x-large')

plt.show()
    