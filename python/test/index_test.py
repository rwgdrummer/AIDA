# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import time
import math
import unittest
import pickle

import cv2
import numpy as np

from aida.index import index

"""
Install notes: pillow==5.0.0
"""


def graph_accums_trp(name,accums):
    import numpy as np


    time_d = np.asarray([accum.duration() for accum in accums])
    recall_d = np.asarray([accum.recall() for accum in accums])
    precision_d = np.asarray([accum.precision() for accum in accums])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(time_d, recall_d, precision_d, alpha=0.5)

    ax.set_xlabel(r'Time', fontsize=15)
    ax.set_ylabel(r'Recall', fontsize=15)
    ax.set_zlabel(r'Precision', fontsize=15)

    for i in range(len(accums)):
        accum = accums[i]
        ax.text(accum.duration(),accum.recall(),accum.precision(), '%s' % (str(i)), size=20, zorder=1,
                color='k')

    ax.grid(True)
    fig.tight_layout()

    plt.savefig(name + '_trp.png')

def graph_accums_tmcc(name,accums):
    import numpy as np


    time_d = np.asarray([accum.duration() for accum in accums])
    mcc_d = np.asarray([accum.mcc() for accum in accums])
    fig, ax = plt.subplots()

    ax.scatter(time_d, mcc_d, alpha=0.5)

    ax.set_xlabel(r'Time', fontsize=15)
    ax.set_ylabel(r'MCC', fontsize=15)

    for i in range(len(accums)):
        accum = accums[i]
        ax.annotate(str(i), (accum.duration(),accum.mcc()))
    ax.grid(True)
    fig.tight_layout()

    plt.savefig(name + '_tmcc.png')

def raw(img):
    return img

def resize80(img):
    return  cv2.resize(img, (int(0.8 * img.shape[1]), int(0.8 * img.shape[0])))

def resize60(img):
    return cv2.resize(img, (int(0.6 * img.shape[1]), int(0.8 * img.shape[0])))

def rotate90(img):
    return np.rot90(img,1)

def resize60rotate90(img):
    return np.rot90(resize60(img),1)

def equalizeHist60(img):
    return index.equalizeHist(resize60(img))

class Accum:

    def __init__(self,name):
        self.name = name
        self.total = 0
        self.tp = 0.0
        self.fp = 0.0
        self.tn = 0.0
        self.fn = 0.0
        self.relevant = 0.0
        self.start_time = time.time()

    def start(self):
        self.start_time = time.time()

    def precision(self):
        return self.tp / (self.tp + self.fp)

    def accuracy(self):
        return (self.tp + self.tn) / self.total

    def stop(self):
        self.end_time = time.time()

    def duration(self):
        return self.end_time - self.start_time

    def recall(self):
        return self.tp / self.relevant

    def mcc(self):
        return self.tp*self.tn - self.fp*self.fn / math.sqrt((self.tp + self.fp) *
                                                             (self.tp + self.fn) *
                                                             (self.tn + self.tp) *
                                                             (self.tn + self.fn))

class AccumCache:

    def __init__(self,picklefilename):
        self.picklefilename = picklefilename
        self.cache = {}
        if os.path.exists(picklefilename):
            with open(self.picklefilename, 'rb') as fp:
               self.cache = pickle.load(fp)

    def __getitem__(self, key):
        return self.cache[key] if key in self.cache else None

    def __setitem__(self,key,value):
        self.cache[key] = value
        with open(self.picklefilename,'wb') as fp:
            pickle.dump(self.cache,fp)


class AccumTest(unittest.TestCase):

    def test_pickle(self):
        if os.path.exists('test.dat'):
            os.remove('test.dat')
        cache = AccumCache('test.dat')
        key = (index.LSHIndex(index.HISTHasher(), match_thresh=1.0).name, 2)
        cache[key] = Accum(key[0])
        self.assertTrue(cache[key] is not None)
        cache = AccumCache('test.dat')
        self.assertTrue(cache[key] is not None)
        if os.path.exists('test.dat'):
            os.remove('test.dat')


class IndexTest(unittest.TestCase):
    modifiers = [raw, resize80, resize60, index.equalizeHist, equalizeHist60] #, rotate90, resize60rotate90]

    def setUp(self):
        self.cache = AccumCache('accum_1.dat')

    def _get_images(self):
        images = []
        for root, dirs, files in os.walk('../../data'):
            for name in files:
                full = os.path.abspath(os.path.join(root,name))
                with open(full,'rb') as fp:
                  r = os.fstat(fp.fileno())
                if name.endswith('jpg') and r.st_size < 1300000:
                    images.append(full)
        return images


    def calibrate_distance(self, hasher, round=0, skip=20):
        image_selection_raw = self._get_images()
        image_selection = [(os.path.basename(image_selection_raw[x]), cv2.imread(image_selection_raw[x]))
                           for x in range(round, len(image_selection_raw), skip)]
        items = {}
        for img_tuple in image_selection:
            for f in self.modifiers:
                img_mod = f(img_tuple[1])
                id = os.path.splitext(img_tuple[0])[0]
                img_name = os.path.splitext(img_tuple[0])[0] + '_' + f.__name__
                item = hasher.hash(img_name, img_mod)
                if id not in items:
                    items[id] = []
                for d in item.descriptors:
                    found = False
                    for x in items[id]:
                        found |= np.all(d == x)
                        if found:
                            break
                    if not found:
                        items[id].append(d)
        maxdist = 0
        dists = []
        for k,v in items.items():
            for x in v:
                for y in v:
                    dist = index.l2norm(x, y)
                    dists.append(dist)
                    if dist > maxdist:
                        maxdist = dist
        print ('{} {} {}'.format(index.__name__, maxdist, np.mean(np.asarray(dists))))
        return maxdist

    def test_get_calibrations(self):
        #self.calibrate_distance(index.SIFTSigHasher())
        self.calibrate_distance(index.SIFTReducedHasher())
        self.calibrate_distance(index.ImageMatchHasher())
        self.calibrate_distance(index.HISTHasher())


    def run_exp(self, mem_index,rounds=1, skip=25, override=None):#['4861957083_6a79616620_o.jpg']):
        accum =  self.cache[(mem_index.name,rounds)]
        if accum is not None and override is None:
            return accum
        accum = Accum(mem_index.name)
        print('-------------------{}----------------------'.format(mem_index.name))
        allvariantscounts = 0
        image_selection_raw= self._get_images()
        for round in range(rounds):
            if override is None:
                image_selection = [(os.path.basename(image_selection_raw[x]),cv2.imread(image_selection_raw[x]))
                                   for x in range(round,len(image_selection_raw),skip)]
            else:
                image_selection = [(os.path.basename(image_selection_raw[x]),cv2.imread(image_selection_raw[x]))
                                   for x in range(len(image_selection_raw)) if os.path.basename(image_selection_raw[x]) in override]
            for img_tuple in image_selection:
               for f in self.modifiers:
                    img_mod = f(img_tuple[1])
                    img_name = os.path.splitext(img_tuple[0])[0] + '_' + f.__name__
                    mem_index.index(img_name, img_mod)
                    allvariantscounts+=1

            for img_tuple in image_selection:
                id = os.path.splitext(img_tuple[0])[0]
                matches = set([x for x in mem_index.find(id, img_tuple[1])])
                pre = id[0:23]
                match_total = len(matches)
                found = [x for x in matches if x[0:23] == pre]
                correct = len(found)
                tp = correct
                fp = (match_total - correct)
                fn = (len(self.modifiers) - correct)
                accum.fp += fp
                accum.fn += fn
                accum.tp += correct
                accum.tn += (allvariantscounts - tp - fp - fn)
                accum.total += allvariantscounts
                accum.relevant += len(self.modifiers)
                print("%s => %f %f %s" % (id, float(correct), float(correct) / float(match_total) if match_total >0 else 0, ', '.join(found)))
            accum.stop()
        if override is None:
            self.cache[(mem_index.name,rounds)] = accum
        return accum


    def dump(self,name,accums):
        for i in range(len(accums)):
            accum = accums[i]
            print('%d: %s = {ac: %f, pr: %f, re: %f, du: %f}' % (i,
                                                    accum.name,
                                                    accum.accuracy(),
                                                    accum.precision(),
                                                    accum.recall(),
                                                    accum.duration()))
        graph_accums_tmcc(name,accums)
        graph_accums_trp(name,accums)



    hist_thresh = 300
    sift_thresh = 300
    match_thresh = 300
    def sift_index_bulk(self, rounds=2):

        accums = []
        accums.append(self.run_exp(index.NNIndex(index.HISTHasher(), match_thresh=self.hist_thresh), rounds=rounds))
        accums.append(self.run_exp(
            index.LSHIndex(index.HISTHasher(), match_thresh=self.hist_thresh, number_of_tables=12),
            rounds=rounds))
        accums.append(self.run_exp(
            index.LSHIndex(index.HISTHasher(), match_thresh=self.hist_thresh, length_of_tables=24),
            rounds=rounds))
        accums.append(self.run_exp(
                index.LSHIndex(index.HISTHasher(), number_of_tables=24, length_of_tables=24, match_thresh=self.hist_thresh),
                rounds=rounds))

        accums.append(self.run_exp(index.KLSHIndex(index.HISTHasher(), match_thresh=self.hist_thresh), rounds=rounds))

        accums.append(
            self.run_exp(index.NNIndex(index.SIFTReducedHasher(), match_thresh=self.sift_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.SIFTReducedHasher(), match_thresh=self.sift_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.SIFTReducedHasher(), match_thresh=self.sift_thresh,
                                        number_of_tables=24, length_of_tables=24),
                         rounds=rounds))
        accums.append(
            self.run_exp(index.KLSHIndex(index.SIFTReducedHasher(), match_thresh=self.sift_thresh), rounds=rounds))

        accums.append(
            self.run_exp(index.KLSHIndex(index.ImageMatchHasher(), match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.NNIndex(index.ImageMatchHasher(), match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(), match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(), length_of_tables=24, match_thresh=self.match_thresh),
                         rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(), number_of_tables=12, match_thresh=self.match_thresh),
                         rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(), number_of_tables=24,
                                        length_of_tables=24, match_thresh=self.match_thresh), rounds=rounds))

        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(equalize=True), match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(equalize=True), length_of_tables=24,
                                        match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(index.LSHIndex(index.ImageMatchHasher(equalize=True),
                                        number_of_tables=12, match_thresh=self.match_thresh), rounds=rounds))
        accums.append(
            self.run_exp(
                index.LSHIndex(index.ImageMatchHasher(equalize=True), number_of_tables=24,
                               length_of_tables=24, match_thresh=self.match_thresh),rounds=rounds))


        self.dump(str('test'),accums)

    def sift_index_hashers(self, rounds=2):

        accums = []

        hashers = [index.NormalizeHash(index.ImageMatchHasher(), index.resizeToWidth),
                   index.NormalizeHash(index.ImageMatchHasher(), index.resizeAndEquaHist),
                   index.NormalizeHash(index.HISTHasher(), index.resizeAndEquaHist),
                   index.NormalizeHash(index.HISTHasher(), index.resizeToWidth)]
        for hasher in hashers:
            accums.append(
                self.run_exp(index.LSHIndex(hasher, match_thresh=self.match_thresh),
                             rounds=rounds))
            accums.append(
                self.run_exp(index.LSHIndex(hasher, length_of_tables=24,
                                            match_thresh=self.match_thresh), rounds=rounds))
            accums.append(
                self.run_exp(index.LSHIndex(hasher,
                                            number_of_tables=12, match_thresh=self.match_thresh), rounds=rounds))
            accums.append(
                self.run_exp(
                    index.LSHIndex(hasher, number_of_tables=24,
                                   length_of_tables=24, match_thresh=self.match_thresh), rounds=rounds))
            accums.append(
                self.run_exp(index.KLSHIndex(hasher, match_thresh=self.match_thresh), rounds=rounds))


        self.dump(str('hasher_test'), accums)

    def test_sift_index_hashers(self):
        self.sift_index_hashers()


