# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 14:02:58 2017

@author: Francesco
"""
import matplotlib.pyplot as plt
import time
import numpy as np
plt.ion()

global ROWS
global COLS
ROWS = 4
COLS = 2

class DynamicUpdate():
    #Suppose we know the x range
    min_x = 0
    max_x = 19

    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots(4,2)
        self.lines = []
        for i in range(ROWS):
            for j in range(COLS):
                temp, = self.ax[i][j].plot([],[])
                self.lines.append(temp)
                #Autoscale on unknown axis and known lims on the other
                self.ax[i][j].set_autoscaley_on(True)
                self.ax[i][j].set_xlim(self.min_x, self.max_x)
                #Other stuff
                self.ax[i][j].grid()
                self.lines[i*COLS+j].set_xdata([np.arange(0,20,1)])

    def on_running(self, ydata):
        #Update data (with the new _and_ the old points)
        for i in range(ROWS):
            for j in range(COLS):
                self.lines[i*COLS+j].set_ydata(ydata)
                #Need both of these in order to rescale
                self.ax[i][j].relim()
                self.ax[i][j].autoscale_view()
                #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    #Example
    def __call__(self):
        
        self.on_launch()
        ys = np.zeros(20)
        
        graph_data = open('samplefile.txt','r').read()
        lines = graph_data.split('\n')
        for line in lines:
            if(len(line)>1):
                self.on_running(ys)
                x,y = line.split(',')
                ys = np.roll(ys,-1) #shift left numbers
                ys[-1] = y   #change only the last
                time.sleep(0.1)
                
        
        #return x, y
if __name__ == "__main__":
    
    d = DynamicUpdate()
    d()
    