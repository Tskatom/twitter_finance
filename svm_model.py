#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import numpy as np
from sklearn import svm, preprocessing


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

    def fit(self):
        self.clf.fit(self.norm_train)

    def predict(self):
        self.test_pred = self.clf.predict(self.norm_test)
        self.novel_days = self.test_days[self.test_pred == -1]

    def normalize(self):
        self.scaler = preprocessing.StandardScaler().fit(self.train_data)
        self.norm_train = self.scaler.transform(self.train_data)
        self.norm_test = self.scaler.transform(self.test_data)


def main():
    svm_twitter = SVM_Twitter(0.05, 0.125, 'rbf')
    train_file = '/home/vic/work/data/svm/Argentina_train.txt'
    test_file = '/home/vic/work/data/svm/Argentina_test.txt'

    for country in COUNTRY:
        train_file = "/home/vic/work/data/svm/%s_train.txt" % country
        test_file = "/home/vic/work/data/svm/%s_test.txt" % country
        svm_twitter.load_data(train_file, test_file)
        svm_twitter.normalize()
        svm_twitter.fit()
        svm_twitter.predict()

        print "prediction result: %s " % country
        print svm_twitter.novel_days


if __name__ == "__main__":
    main()
