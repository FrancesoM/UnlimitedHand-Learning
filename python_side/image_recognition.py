# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 11:45:02 2017

@author: Francesco
"""

import scipy.misc as im
import numpy as np
import matplotlib.pyplot as plt
import utilities as ut

#x = im.imread("test/%d.jpg"%(1),mode='F',flatten=True)
#n = x.shape[0]
#m = x.shape[1]

def distance(Y1,Y2):
    
    try:
        assert(Y1.shape == Y2.shape)
    except AssertionError:
        input(str(Y1.shape)+str(Y2.shape))
        
    d = Y1.shape[1]
    temp = 0
    for i in range(d):
        temp += np.linalg.norm(Y1[:,i] - Y2[:,i])
        
    return temp

""" *************************** TRAINING ***************************** """

D = ut.load_dataset('dataset_100Hz.txt')

X = D[:,:-1,:]
classification = D[-1,-1,:]

m = X.shape[0]
n = X.shape[1]
M = X.shape[2]
L = len(np.unique(classification))
d = 6 #<---- I want to reduce to 4 dimensions parameter of the algorithm

re = im.toimage(X[:,:,0])
plt.imshow(re)
plt.show()

mean_all = np.average(X,axis=2)
mean_class = []
for i in range(L):
    mean_class.append(np.average(X[:,:,classification==i],axis=2))

print(mean_all.shape)
print(mean_class[0].shape)

#calculating Sb
Sb = np.zeros((n,n))
for i in range(L):
    Am = mean_class[i]-mean_all
    Sb += np.dot(Am.T,Am)
    
#print(np.allclose(Sb, Sb.T))

Sw = np.zeros((n,n))

for i in range(M):
    Ak = X[:,:,i] - mean_class[int(classification[i])] #use y to address the correct class
    Sw += np.dot(Ak.T,Ak)


print(Sw.shape)
#print(np.allclose(Sw,Sw.T))

#print(np.linalg.det(Sw))

#Sw is non singular when M >= L + 3/(min(m,n)) where M dimension dataset, L number of classes, mn dimension of matrixes

SSwb = np.dot(np.linalg.inv(Sw),Sb)

w, v = np.linalg.eig(SSwb)

#print("Eigenvalues:\n",w)
#print("Eigenvectors:\n",v)

eigen_pairs = [(np.abs(w[i]),v[i]) for i in range(len(w))]
eigen_pairs.sort(reverse=True)

W = eigen_pairs[0][1][:,np.newaxis]
for d in range(1,d):
    W = np.hstack((W,eigen_pairs[d][1][:,np.newaxis]))

print("Shape:",W.shape)

#try to reconstruct an image

y = np.dot(X[:,:,0],W)

X_rec = np.dot(y,W.T)
    
re = im.toimage(X_rec)
plt.imshow(re)
plt.show()

#Y will be the projected data set
Y = []
for i in range(M):
    Y.append(np.dot(X[:,:,i],W))

print(Y[0].shape)
    
""" **************************** TEST ************************** """

test = ut.load_dataset('test_100Hz.txt')

X_test = test[:,:-1,:]
classification_test = test[-1,-1,:]

M_test = len(classification_test)

print("***************** Test begins ***********************")

print("Number of movements: ", M_test)

for i in range(M_test):
    y_test = np.dot(X_test[:,:,i],W)
    #scan the database
    minimum_dist = np.inf #start from the highest possible
    predicted_mov = None
    for j in range(M):
        dist = distance(y_test,Y[j])
        
        if(dist <= minimum_dist):
            #se è migliore predico quel movimento
            minimum_dist = dist
            predicted_mov = classification[j]
    print("Minumum distance: %d"%minimum_dist)
            
    print("Prediction: %d, Correct: %d"%(predicted_mov,classification_test[i]) )


    
    
    
    
    
    