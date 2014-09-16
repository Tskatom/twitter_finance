#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from sklearn import cluster
import pandas as pa
import numpy as np
import json
import codecs


def corr_cluster(corr_file, matrix_file, cluster_dir):
    corr_frame = pa.DataFrame.from_csv(corr_file).abs()
    #use the abs value of corr to cluster
    freq_matrix = pa.DataFrame.from_csv(matrix_file)

    _, labels = cluster.affinity_propagation(corr_frame)
    n_label = labels.max()
    names = corr_frame.index
    #output cluster file
    if corr_file[-1] == "/":
        cluster_file = corr_file.split("/")[-2] + "_cluster"
    else:
        cluster_file = corr_file.split("/")[-1] + "_cluster"

    cluster_file = codecs.open(os.path.join(cluster_dir, cluster_file),
                               "w",
                               encoding="utf-8")

    for i in range(n_label + 1):
        #compute the average correlation between cluster and out-cluster
        clus = np.array(names[labels == i])
        in_cluster = corr_frame[clus].ix[clus]
        up_index = np.triu_indices(len(clus), 1)
        aver_corr = np.array(in_cluster)[up_index].mean()

        out_clus = np.array(names[labels != i])
        out_cluster = corr_frame[clus].ix[out_clus]
        out_aver_corr = np.array(out_cluster).mean()

        #compute the variance of the entity
        in_aver_var = freq_matrix[clus].var(axis=1).mean()

        obj = {"cluster": map(str, clus), "in_aver_corr": aver_corr,
               "out_aver_corr": out_aver_corr,
               "in_aver_var": in_aver_var}
        cluster_file.write(json.dumps(obj, ensure_ascii=False) + "\n")

    cluster_file.flush()
    cluster_file.close()


def handle_dir(corr_dir, cluster_dir):
    if not os.path.exists(cluster_dir):
        os.mkdir(cluster_dir)

    files = os.listdir(corr_dir)
    for f in files:
        #construct matrix filename
        country = f.split("_")[0]
        day = f.split("_")[1]
        matrix_dir = "/media/datastorage/filter/matrix/%s" % country
        matrix_file = "%s_%s_entity_matrix" % (country, day)
        full_corr_f = os.path.join(corr_dir, f)
        full_matrix_f = os.path.join(matrix_dir, matrix_file)
        try:
            corr_cluster(full_corr_f, full_matrix_f, cluster_dir)
        except:
            continue
        print f


def main():
    corr_dir = '/media/datastorage/filter/corr/Argentina/'
    corr_dir = sys.argv[1]
    cluster_dir = sys.argv[2]
    handle_dir(corr_dir, cluster_dir)
if __name__ == "__main__":
    main()
