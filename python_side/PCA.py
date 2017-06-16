# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 18:10:27 2017

@author: Francesco
"""
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt



graph_data = open('shuffled.txt','r').read()

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

#2D

plt.scatter(X_PCA[:,0],X_PCA[:,1])

#3D
#fig = plt.figure()
#
#ax = fig.add_subplot(111, projection='3d')
#
#xs = X_PCA[:,0]
#ys = X_PCA[:,1]
#zs = X_PCA[:,2]
#
#ax.scatter(xs, ys, zs)
#
#ax.set_xlabel('X Label')
#ax.set_ylabel('Y Label')
#ax.set_zlabel('Z Label')
#
#
plt.show()
