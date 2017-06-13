# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 18:10:27 2017

@author: Francesco
"""
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt

graph_data = open('00left_right.txt','r').read()

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

data = data[20:,:] #truncate values that may be corrupted by the initialization of the serial port
        
#Now we have our data stored into a numpy matrix

std = StandardScaler()
X_std = std.fit_transform(data)

cov_m = np.cov(X_std.T)
eig_val,eig_vec = np.linalg.eig(cov_m)

tot = sum(eig_val)

var_exp = [(i/tot) for i in sorted(eig_val,reverse=True)]

plt.bar(range(1,8),var_exp,alpha=0.5,align='center',label='explained variance')  
print("cacaca")
plt.show()
        
        
