import numpy as np

STRIDE = 3

def sliding_window(index_start,stride,data):
	Y = data[index_start:index_start+stride-1,:] 

rfile = open('test.txt','r').read()

lines = rfile.split('\n')

NUMBER_OF_ACQUISITIONS = len(lines)

data = np.zeros((NUMBER_OF_ACQUISITIONS,8))

rep = 0
for line in lines:
	if(len(line) > 1 ):
		temp = line.split(',')
		for ch in range(8):
			data[rep,ch] = int(temp[ch])
			
		rep += 1

#I take three rows each time, representing, for each channel, the x(t),x(t-1),x(t-2)

Y = lambda data,start,stride: data[start:start+stride,:]
X = [1,2,3]

#creating dataset with X,Y for each channel

for i in range(len())


