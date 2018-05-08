import pickle
import csv
import os
import math
import numpy as np
import random as rd

Weight = np.ones(7)

def autoload(file):
    f=file.split('.')
    store=f[0]
    if os.path.exists(store):
        with open(store,'rb') as f:
            print('load from %s'%store)
            return pickle.load(f)
    return 0
	
def autosave(obj,file):
    f=file.split('.')
    store=f[0]
    with open(store,'wb') as f:
        print('save to %s'%store)
        pickle.dump(obj,f)
		
def input() :
	rawdata = autoload("data/historicSimData")
	if(rawdata) :
		return rawdata
	rawdata = autoload("data/feed_data")
	data = []
	for r in rawdata :
		if r != 0 :
			t = [r[0][1 : ] + r[1][2 : 4] + [r[1][-2]], r[-1][2 : 4] + [r[-1][-2]]]
			t[0][0] = int(t[0][0].split(" ")[-1].split(":")[0])
		
			data.append([np.array(t[0]), np.array(t[1])])
	return data
	
def dis(v) :
	d = 0
	n = len(v)
	for i in range(n):
		d = d + v[i] * v[i] * Weight[i]
	return d
	
def query(qw, qa, dataset) :
	data = dataset[ : ]
	n = len(data)
	for i in range(n) :
		data[i].append(dis((data[i][0][ : 6] - qw).tolist() + [data[i][0][qa[0]] - qa[1]]))
	sorted(data, key = lambda x : x[-1])
	delta = 0
	for i in range(10) :
		delta = delta + (data[i][1][qa[0]] - data[i][0][qa[0]]) * (10 - i)
	return delta / 45.0
	
	
data = input()
autosave(data, "data/historicSimData")
n = int(len(data) * 0.95)
dataset = data[ : n]
test = data[n : ]
m = len(test)
variance = 0
ai = -3
for i in range(1000) :
	x = rd.randint(0, m - 1)
	r = test[x][1][ai] - test[x][0][ai] - query(test[x][0][ : 6], [ai, test[x][0][ai]], dataset)
	variance = variance + r * r
	print(i, r * r)
	if((i + 1) % 32 == 0) :
		print(variance / (i + 1))
print(variance / 1000)
