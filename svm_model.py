#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import numpy as np
from sklearn import svm, preprocessing, decomposition
from etool import queue, args


COUNTRz = ['Argentina']
COUNTRY = ['Argentina', 'Brazil', 'Chile', 'Colombia',
           'Costa Rica', 'Mexico', 'Panama', 'Peru',
           'Venezuela']


class SVM_Twitter:
    def __init__(self, nu, gamma, kernel):
        self.clf = svm.OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)

    def load_data(self, train_file, test_file):
        train_features = []
        test_features = []
        test_days = []
        with open(train_file, "r") as r:
            for l in r:
                vec = map(float, l.strip().split(" ")[1:])
                train_features.append(vec)

        self.train_data = np.array(train_features)

        with open(test_file, "r") as r:
            for l in r:
                vec = l.strip().split(" ")
                date = vec[0]
                vec = map(float, vec[1:])
                test_days.append(date)
                test_features.append(vec)

        self.test_data = np.array(test_features)
        self.test_days = np.array(test_days)

        self.norm_train = self.train_data
        self.norm_test = self.test_data

    def fit(self):
        #print "Traning: ", self.norm_train
        self.clf.fit(self.norm_train)

    def predict(self):
        #print "Test: ", self.norm_test
        self.test_pred = self.clf.predict(self.norm_test)
        self.novel_days = self.test_days[self.test_pred == -1]

    def normalize(self):
        self.scaler = preprocessing.StandardScaler().fit(self.train_data)
        self.norm_train = self.scaler.transform(self.train_data)
        self.norm_test = self.scaler.transform(self.test_data)

    def min_max_scale(self):
        min_max_scaler = preprocessing.MinMaxScaler()
        self.norm_train = min_max_scaler.fit_transform(self.train_data)
        self.norm_test = min_max_scaler.transform(self.test_data)

    def pca(self, num):
        pca = decomposition.PCA(n_components=num)
        pca.fit(self.norm_train)
        self.norm_train = pca.transform(self.norm_train)
        self.norm_test = pca.transform(self.norm_test)


def main():
    svm_twitter = SVM_Twitter(0.1, 0.125, 'rbf')
    ap = args.get_parser()
    ap.add_argument("--pca_num", type=int)
    ap.add_argument("--net", type=str)
    ap.add_argument("--k", type=int)
    arg = ap.parse_args()
    folder = {"t": "content", "c": "comprehend", "u": "user2user"}

    assert arg.pub, "Please input a queue to publish surrogate"
    queue.init(arg)
    send_queue = queue.open(arg.pub, "w")
    for country in COUNTRY:
        train_file = "/media/datastorage/experiment/" + folder[arg.net] \
            + "/%s_train_%d" % (country.replace(" ", ""), arg.k)
        test_file = "/media/datastorage/experiment/" + folder[arg.net] \
            + "/%s_test_%d" % (country.replace(" ", ""), arg.k)
        svm_twitter.load_data(train_file, test_file)
        svm_twitter.min_max_scale()
        #svm_twitter.normalize()
        #svm_twitter.pca(arg.pca_num)
        svm_twitter.fit()
        svm_twitter.predict()

        for day in svm_twitter.novel_days:
            surrogate = {"country": country, "date": day}
            send_queue.write(surrogate)

        print "prediction result: %s " % country
        print svm_twitter.novel_days
    send_queue.close()

if __name__ == "__main__":
    main()
