# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 20:29:42 2017

@author: Francesco
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import utilities

fig2d, ax2d = plt.subplots(1)

fig3d = plt.figure()
ax3d = fig3d.add_subplot(111, projection='3d') 

for i in range(20,25):
    
    file = utilities.open_outfile('thread_dataleft-right.txt',i)
    X = file[0]
    N_cluster = file[1] 
    
    if N_cluster <= 1:
        c = (0,0,0)
    else:
        c = utilities.colorarray[i-20]
        
    if X.shape[1] == 3: #3D plot

        xs = X[:,0]
        ys = X[:,1]
        zs = X[:,2]
        
        ax.scatter(xs, ys, zs,color=c)
        
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        
    if X.shape[1] == 2:
        
        ax2d.scatter(X[:,0],X[:,1],label="#: "+str(N_cluster)+"Interval"+str(i*100)+':'+str((i+1)*100),color = c)
        
        #ax.scatter(cluster_centers[:,0],cluster_centers[:,1])

legend = ax2d.legend(loc='upper left', shadow=True)
plt.show()