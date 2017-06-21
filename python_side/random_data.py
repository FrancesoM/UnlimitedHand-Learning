"""
GENERATE A RANDOM DATASET

"""

import numpy as np

out_file = open("test.txt","w")
for rep in range(10):
	out_file.write(str(np.random.randint(500)))
	
	for channel in range(7):
		out_file.write(',')
		out_file.write(str(np.random.randint(500))) #only to avoid printing a coma
		
	out_file.write('\n')
