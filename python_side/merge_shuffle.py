# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 19:56:41 2017

@author: Francesco
"""

#Join two files and shuffles

n1 = "00left_right.txt"
n2 = "03up_down.txt"

f1 = open(n1,'r').read()
f2 = open(n2,'r').read()

lines1 = f1.split('\n')
lines2 = f2.split('\n')

numberoflines1 = (len(lines1)-40)
numberoflines2 = (len(lines2)-40)

data = np.zeros((numberoflines1+numberoflines2,8))


i=0;j=0;h=0

for line in lines1[20:-20]: #the last acquisition may be corrupted, sudden termination of serial comm
    if(len(line)>1):
        t = line.split(',')
        for value in t:
            data[i,j] = t[j]
            j+=1
        j=0
        i+=1
        #print(i)
        
for line in lines2[20:-20]:
    if(len(line)>1):
        t = line.split(',')
        for value in t:
            data[i+h,j] = t[j]
            j+=1
        j=0
        h+=1

np.random.shuffle(data)

print(data)

graph_data = open('shuffled.txt','w')

for r in range(len(data[:,0])):
        graph_data.write(str(data[r,0]))
        for value in data[r,1:]:
            graph_data.write(',')
            graph_data.write(str(value))
        graph_data.write('\n')
        
graph_data.close()