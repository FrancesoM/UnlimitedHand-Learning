# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 20:29:42 2017

@author: Francesco
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import utilities

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d') 

for i in range(16):
    a = utilities.open_outfile('thread_dataup-down.txt',i)

    
    xs = a[:,0]
    ys = a[:,1]
    zs = a[:,2]
    
    ax.scatter(xs, ys, zs)
    
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')


plt.show()