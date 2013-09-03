#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from sklearn import cluster
import pandas as pa
import numpy as np

def corr_cluster(corr_file):
    corr_frame = pa.DataFrame.from_csv(corr_file)
    _, labels = cluster.affinity_propagation(corr_frame)
    n_label = labels.max()
    names = corr_frame.index
    for i in range(n_label + 1):
        print "Cluster %d: %s" % (i + 1, names[labels == i])
        #compute the average correlation between cluster and out-cluster
        clus = np.array(names[labels == i])
        in_cluster = corr_frame[clus].ix[clus]
        up_index = np.triu_indices(len(clus), 1)
        aver_corr = np.array(in_cluster)[up_index].mean()
        print aver_corr

        out_clus = np.array(names[labels != i])
        out_cluster = corr_frame[clus].ix[out_clus]
        out_aver_corr = np.array(out_cluster).mean()
        print out_aver_corr

        #compute the variance of the entity

def main():
    corr_file = '/media/datastorage/filter/corr/Argentina/Argentina_2013-07-03_entity_matrix_corr'
    corr_cluster(corr_file)

if __name__ == "__main__":
    main()
