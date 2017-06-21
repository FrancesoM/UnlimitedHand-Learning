# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 18:10:27 2017

@author: Francesco
"""
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

def moving_average(data,samp_for_average):
    n_windows = int(len(data)/samp_for_average)
    for i in range(n_windows):
        data[i*samp_for_average:(i+1)*samp_for_average] = np.average(data[i*samp_for_average:(i+1)*samp_for_average])

def grad(data):
    der = np.zeros((len(data),4))
    for i in range(1,len(data)):
        der[i,:] = data[i,:]-data[i-1,:]
    return der
        
int_channel = [0,1,6,7]

graph_data = open('model_updown.txt','r').read()

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

data = data[:,int_channel]

ustart = 3000
dstart = 7100
up = data[ustart:ustart+500,:] #truncate values that may be corrupted by the initialization of the serial port
down = data[dstart:dstart+500,:]

data = np.vstack((up,down))

fig2, ax2 = plt.subplots(1,1)
for p in range(len(int_channel)):
    
    y = data[:,p]
    moving_average(y,30)
    ax2.plot(y)
    
data = grad(data)

#Now we have our data stored into a numpy matrix

std = StandardScaler()
X_std = std.fit_transform(data)

cov_m = np.cov(X_std.T)
eig_val,eig_vec = np.linalg.eig(cov_m)

tot = sum(eig_val)

var_exp = [(i/tot) for i in sorted(eig_val,reverse=True)]

#plt.bar(range(0,8),var_exp,alpha=0.5,align='center',label='explained variance')  

#create sorted pairs eigval-eigvect according to the greatest eigval

eigen_pairs = [(abs(eig_val[i]),eig_vec[:,i]) for i in range(len(eig_val))]
eigen_pairs.sort(reverse=True)

#we choose only the first two, to be able to plot in 2D
#we create the matrix W by joining the two eigvectors

W = np.hstack((eigen_pairs[0][1][:,np.newaxis],
               eigen_pairs[1][1][:,np.newaxis],
               eigen_pairs[2][1][:,np.newaxis]))

#and we project the entire dataset into this new space of lower dimension
#remember that I want to discriminate the movement

X_PCA = X_std.dot(W)

print(X_PCA)

#2D

#fig, ax = plt.subplots(1,1)
#
#ax.scatter(X_PCA[0:500,0],X_PCA[0:500,1])
#ax.scatter(X_PCA[500:1000,0],X_PCA[500:1000,1])

#3D
fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')

xd = X_PCA[0:500,0]
yd = X_PCA[0:500,1]
zd = X_PCA[0:500,2]

xu = X_PCA[500:1000,0]
yu = X_PCA[500:1000,1]
zu = X_PCA[500:1000,2]

ax.scatter(xd, yd, zd,'o')
ax.scatter(xu, yu, zu,'*')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')


plt.show()
