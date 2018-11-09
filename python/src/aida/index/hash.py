# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import numpy as np
from sklearn.datasets import load_iris
from sklearn.cross_validation import train_test_split
from klsh import KernelLSH
from .index import Index

class KLSHIndex(Index):

    def __init__(self, hasher):
        Index.__init__(self, hasher)
        data = []

    def index(self, id, img):
        item = self.indexer.hash(id, img)
        for i in range(len(item.descriptors)):
            self.engine.store_vector(item.descriptors[i], data=(id, item.keypoints[i], item.descriptors[i]))

    def find(self, id, img):
        """
        :param id:
        :param img:
        :return:
        @rtype: list of IndexItem
        """
        items = self.indexer.hash(id, img)
        c = 0
        X = np.zeros((len(items),len(items[0].descriptor)))
        for i in items:
            X[c, :] = i.descriptor
            c += 1
        return self.klsh.query(X, 3)

    def _train(self):
        training_data = self.index.keys()
        X = None
        c = 0
        for i in training_data:
            if c >= 100000:
                break
            if X is None:
                X = np.zeros((100000,len(i),))
            X[c,:] = i
            c += 1
        X = X[0:c-1,:]
        self.klsh = KernelLSH(nbits=16, kernel='rbf', random_state=42)
        self.klsh.fit(X)
