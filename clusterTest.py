# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 16:16:25 2019

@author: Charly
"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.cluster.hierarchy as hcluster



def findClusters(data,thresh):
    # clustering
    clusters = hcluster.fclusterdata(data, thresh, criterion="distance")
    nbCluster = len(set(clusters))
    
    return nbCluster
    
    
# generate 3 clusters of each around 100 points and one orphan point
N=100
data = np.random.randn(3*N,2)
data[:N] += 5
data[-N:] += 10
data[-1:] -= 20
thresh = 1

nbCluster = findClusters(data,thresh)

print(nbCluster)

# plotting
# plt.scatter(*np.transpose(data), c=clusters)
# plt.axis("equal")
# title = "threshold: %f, number of clusters: %d" % (thresh, len(set(clusters)))
# plt.title(title)
# plt.show()