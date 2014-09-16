#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import numpy as np
from sklearn import svm, preprocessing, decomposition
from etool import queue, args
import os
import json
import pandas as pd


COUNTRz = ['Argentina']
COUNTRY = ['Argentina', 'Brazil', 'Chile', 'Colombia',
           'Costa Rica', 'Mexico', 'Panama', 'Peru',
           'Venezuela']


class SVM_Twitter:
    def __init__(self, nu, gamma, kernel):
        self.clf = svm.OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)

    def load_data(self, train_file, test_file):
        self.train_data = pd.DataFrame.from_csv(train_file, header=None, sep=" ").fillna(method="bfill")
        self.test_data = pd.DataFrame.from_csv(test_file, header=None, sep=" ").fillna(method="bfill")
        self.test_days = self.test_data.index

        self.norm_train = self.train_data
        self.norm_test = self.test_data

    def fit(self):
        #print "Traning: ", self.norm_train
        self.clf.fit(self.norm_train)

    def predict(self):
        #print "Test: ", self.norm_test
        self.test_pred = self.clf.predict(self.norm_test)
        self.novel_days = self.test_days[self.test_pred == -1]

    def min_max_scale(self):
        self.scaler = preprocessing.StandardScaler().fit(self.train_data)
        self.norm_train = self.scaler.transform(self.train_data)
        self.norm_test = self.scaler.transform(self.test_data)

    def normalize(self):
        self.norm_train = (self.train_data - self.train_data.mean()) / (self.train_data.max() - self.train_data.min())
        self.norm_test = (self.test_data - self.train_data.mean()) / (self.train_data.max() - self.train_data.min())

    def pca(self, num):
        pca = decomposition.PCA(n_components=num)
        pca.fit(self.norm_train)
        self.norm_train = pca.transform(self.norm_train)
        self.norm_test = pca.transform(self.norm_test)


def main():
    svm_twitter = SVM_Twitter(0.1, 0.1, 'rbf')
    ap = args.get_parser()
    ap.add_argument("--pca_num", default=8, type=int)
    ap.add_argument("--net", type=str)
    ap.add_argument("--k", type=int)
    ap.add_argument("--inf", type=str, help="input folder")
    ap.add_argument("--o_surr", type=str, help="output surrogate file")
    arg = ap.parse_args()
    folder = {"t": "content", "c": "comprehend", "u": "user2user",
              "e": "entity"}

    assert arg.pub, "Please input a queue to publish surrogate"
    queue.init(arg)
    send_queue = queue.open(arg.pub, "w")
    surr_w = open(arg.o_surr, "w")
    for country in COUNTRY:
        train_file = os.path.join(arg.inf,
                                  "%s_train_%d" % (country.replace(" ", ""), arg.k))
        test_file = os.path.join(arg.inf,
                                 "%s_test_%d" % (country.replace(" ", ""), arg.k))
        svm_twitter.load_data(train_file, test_file)
        svm_twitter.normalize()
        #svm_twitter.normalize()
        #svm_twitter.pca(arg.pca_num)
        svm_twitter.fit()
        svm_twitter.predict()

        for day in svm_twitter.novel_days:
            surrogate = {"country": country, "date": day.strftime("%Y-%m-%d")}
            send_queue.write(surrogate)
            surr_w.write(json.dumps(surrogate)+ "\n")

        print "prediction result: %s " % country
        print [day.strftime("%Y-%m-%d") for day in svm_twitter.novel_days]
    surr_w.flush()
    surr_w.close()
    send_queue.close()

if __name__ == "__main__":
    main()
