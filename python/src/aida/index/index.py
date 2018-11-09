# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from hashlib import sha256

import cv2
import numpy as np
from image_match.goldberg import ImageSignature
from klsh import KernelLSH
from nearpy import Engine
from nearpy.filters import VectorFilter
from nearpy.hashes import RandomBinaryProjections, RandomDiscretizedProjections
from skimage.feature import greycomatrix, greycoprops
from sklearn.neighbors import KDTree
from redis import Redis
from nearpy.storage import RedisStorage, MemoryStorage

"""
Install notes: pillow==5.0.0
Test notes:  raw,resize80,resize60,equalizeHist,equalizeHist60,rotate90
"""

def __flannMatcher(d1, d2, args=None):
    FLANN_INDEX_KDTREE = 0
    TREES = 16
    CHECKS = 50
    index_params = {'algorithm':FLANN_INDEX_KDTREE, 'trees':TREES}
    search_params = {'checks':CHECKS}
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    return flann.knnMatch(d1, d2, k=2) if d1 is not None and d2 is not None else []

def l2norm(a,b,normalized=False):
    #b = b.astype(int)
    #a = a.astype(int)
    norm_diff = np.linalg.norm(b - a)
    if normalized:
        norm1 = np.linalg.norm(b)
        norm2 = np.linalg.norm(a)
        return norm_diff / (norm1 + norm2)
    else:
        return norm_diff



def resizeToWidth(img,target_width=512):
    h = img.shape[0]
    w = img.shape[1]
    per = float(target_width)/w
    new_height = int(per*h)
    new_height = new_height + 8 - new_height % 8
    return cv2.resize(img,(target_width,new_height))

def equalizeHist(img, color='bgr'):
    if color == 'bgr':
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    else:
        img_yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)

    # equalize the histogram of the Y channel
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    #img_yuv[:, :, 1] = cv2.equalizeHist(img_yuv[:, :, 1])
    #img_yuv[:, :, 2] = cv2.equalizeHist(img_yuv[:, :, 2])

    # convert the YUV image back to RGB format
    if color == 'bgr':
        img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    else:
        img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)

    return img_output

def resizeAndEquaHist(img):
    return equalizeHist(resizeToWidth(img))

def match_items(item1, item2, matcher=__flannMatcher):
    import functools
    d1 =  np.asarray(item1.descriptors)
    kp1 = item1.keypoints
    d2 = np.asarray(item2.descriptors)
    kp2 = item2.keypoints
    d1 /= (d1.sum(axis=1, keepdims=True) + 1e-7)
    d1 = np.sqrt(d1)

    d2 /= (d2.sum(axis=1, keepdims=True) + 1e-7)
    d2 = np.sqrt(d2)

    matches = matcher(d1,d2)

    maxmatches = 10000
    # store all the good matches as per Lowe's ratio test.
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    good = sorted(good, key=functools.cmp_to_key(lambda g1, g2: -int(max(g1.distance, g2.distance) * 1000)))
    good = good[0:min(maxmatches, len(good))]

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    return (src_pts, dst_pts) if src_pts is not None else None

def toGray(rgbaimg, type='uint8'):
    a = (rgbaimg[:, :, 3]) if rgbaimg.shape[2] == 4 else np.ones((rgbaimg.shape[0], rgbaimg.shape[1]))
    r, g, b = rgbaimg[:, :, 0], rgbaimg[:, :, 1], rgbaimg[:, :, 2]
    gray = ((0.2126 * r + 0.7152 * g + 0.0722  * b) * a)
    return gray.astype(type)

def normHist(img):
    hist = np.histogram(img, bins=255)[0]
    norm_hist = hist/sum(hist)
    return np.round(norm_hist* 256.0/max(norm_hist) - min(hist))

siftcache = {}

def computeSIFT(id, img):
    global siftcache
    if id in siftcache:
        return siftcache[id]
    detector = cv2.xfeatures2d.SIFT_create()#edgeThreshold=10,nOctaveLayers=3,sigma=1.3)
    (kps, descs) = detector.detectAndCompute(toGray(img),None)
    siftcache[id] = (kps, descs)
    return (kps, descs)

def computeSURF(img):
    detector = cv2.xfeatures2d.SURF_create()
    (kps, descs) = detector.detectAndCompute(toGray(img),None)
    return (kps, descs)

def computeORB(img):
    detector = cv2.ORB_create()
    (kps, descs) = detector.detectAndCompute(toGray(img),None)
    return (kps, descs)

def gclm(img, position, angle, kernel=32,levels=256):
    import math
    patch = np.zeros((kernel,kernel)).astype('uint16')
    ux = int(max(0, int(round(position[1])) - kernel/2))
    uy = int(max(0, int(round(position[0])) - kernel/2))
    lx = int(min(img.shape[0], int(round(position[1])) + kernel/2))
    ly = int(min(img.shape[1], int(round(position[0])) + kernel/2))
    patch[:lx-ux,:ly-uy] = toGray(img)[ux:lx,uy:ly]
    glcm = greycomatrix(patch, [1], [math.radians(angle)], levels, symmetric=True, normed=False)
    summary = np.sum(glcm[:, :, 0, 0], axis=1)
    summary = np.insert(summary, 0, greycoprops(glcm, 'correlation')[0, 0]*100000.0)
    summary = np.insert(summary, 0, greycoprops(glcm, 'dissimilarity')[0, 0])
    return summary

def rotate(angle, vector):
    theta = np.radians(angle)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    return np.dot(vector,R)

class IndexItem:
    """
    An indexed image.
    Descriptors represent signatures of the image or components of the image
    """
    def __init__(self,id, descriptors,keypoints ):
        self.descriptors = descriptors
        self.keypoints = keypoints
        self.id = id

    def toDict(self):
        return {'keys': self.key,
                'descriptors': self.descriptor,
                'id':self.id}

class Hasher:
    """
    Produce signatures for an image
    """
    def __init__(self,name=None):
        self.name = self.__class__.__name__ if name is None else name

    def hash(self, id, img):
        """

        :param id:
        :param img:
        :return:
        @type id: str
        @type img: np.ndarray
        @rtype: IndexItem
        """
        pass

    def dims(self):
        return 1

class SIFTHasher(Hasher):
    """
    TOO Slow.  Uses to many descriptors.
    """
    def __init__(self):
        Hasher.__init__(self)

    def hash(self, id, img):
        (kps, descs) = computeSIFT(id, img)
        return IndexItem(id, descs, kps)

    def dims(self):
        return 128

class  NormalizeHash(Hasher):
    def __init__(self, hasher, normalizer=None):
        Hasher.__init__(self, name=('Adorned[%s](%s)' % (hasher.name, normalizer.__name__)))
        self.hasher = hasher
        self.normalizer = normalizer

    def hash(self, id, img):
        return self.hasher.hash(id, self.normalizer(img))

    def dims(self):
        return self.hasher.dims()


class SIFTReducedHasher(Hasher):
    """
    Select descriptors to reduce the search space.
    Effective. With LSH. 100% hit rate.
    Problem: with LSH FP is 96%
    Also tested with some rotation
    """
    def __init__(self, size = 32, angle = 45):
        """
        Create a sizeXsizeX(350/angle) block.
        Pick one SIFT descriptor per block.
        At the moment, the pick is first come, first serve.
        However, there maybe use in adding a qualifier such as smallest magnitude
        as bigger blobs are less interesting.
        :param size:
        :param angle:
        """
        Hasher.__init__(self, name=self.__class__.__name__ + ('(size=%d, angle=%d)' % (size, angle)))
        self.size = size
        self.angle = angle
        pass

    def hash(self, id, img):
        (kps, descs) = computeSIFT(id, img)
        factor = img.shape[0] / self.size, img.shape[1] / self.size
        grid = np.zeros((self.size,self. size, int(360/self.angle))).astype(np.int32)
        vals = np.zeros((self.size, self.size, int(360 / self.angle)))

        for i in range(len(kps)):
            kp = kps[i]
            pos = int(kp.pt[0] / factor[1]), int(kp.pt[1] / factor[0]), int(kp.angle / self.angle)
            val = kp.response*kp.size
            if vals[pos] < val:
                vals[pos] = val
                grid[pos] = i + 1
        keeps = grid[grid>0] - 1
        return IndexItem(id, [descs[i] for i in keeps], [kps[i] for i in keeps])

    def dims(self):
        return 128


class ImageMatchHasher(Hasher):
    def __init__(self, n_levels=5, crop_percentiles=(10, 90), equalize=False):
        Hasher.__init__(self, name=self.__class__.__name__ + (
            '(n_levels=%d,low_percentile=%d,equalize=%s)' % (
                n_levels, crop_percentiles[0], str(equalize))))

        self.gis = ImageSignature(n_levels=n_levels, crop_percentiles=crop_percentiles)
        self.equalize = equalize
        self.n_levels = n_levels

    def hash(self, id, img):
        sig = self.gis.generate_signature(img)
        return IndexItem(id, [sig], [1])

    def dims(self):
        return 648

class HISTHasher(Hasher):
    """
    Super fast and effieicent.
    Does not work with equahists.
    100% Effective with rotation without resize.
    75% with resize (no rotation).
    20% resise and rotation.
    """
    def __init__(self):
        Hasher.__init__(self)

    def hash(self, id, img):
        a = (img[:, :, 3]) if img.shape[2] == 4 else np.ones((img.shape[0], img.shape[1]))
        imgMeanCrCb = np.mean(np.asarray([0.168736 * img[:,:,0] + 0.331264 * img[:,:,1] + 0.5 * img[:,:,2],
                               0.5 * img[:, :, 0] + 0.418688 * img[:, :, 1] + 0.081312 * img[:, :, 2]]),
                               axis=0)
        img_Y = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
        series_y = [x.astype('uint8') for x in [np.round(img_Y + 0.4), np.round(img_Y - 0.4), np.round(img_Y)]]
        series_CrCb = [x.astype('uint8') for x in [np.round(imgMeanCrCb + 0.4), np.round(imgMeanCrCb - 0.4), np.round(imgMeanCrCb)]]
        series_y = [normHist(x) for x in series_y]
        series_CrCb = [normHist(x) for x in series_CrCb]
        series = series_y #[np.hstack(x) for x in itertools.product(series_y,series_CrCb)]
        return IndexItem(id, series, range(len(series)))

    def dims(self):
        return 255

class SIFTSigHasher(Hasher):
    """
    Select descriptors to reduce the search space.
    Effective. With LSH. 100% hit rate.
    Problem: with LSH FP is 96%
    Also tested with some rotation
    """
    def __init__(self, size = 32, angle = 45):
        """
        Create a sizeXsizeX(350/angle) block.
        Pick one SIFT descriptor per block.
        At the moment, the pick is first come, first serve.
        However, there maybe use in adding a qualifier such as smallest magnitude
        as bigger blobs are less interesting.
        :param size:
        :param angle:
        """
        Hasher.__init__(self, name=self.__class__.__name__ + ('(size=%d, angle=%d)' % (size, angle)))
        self.size = size
        self.angle = angle
        self.gis = ImageSignature(n_levels=5, crop_percentiles=(5, 95))
        pass

    def avg_mean(self,img,x,y):
        P = max([2.0, int(0.5 + min(img.shape) / 20.)])/2.0
        return np.mean(img[x-P:x+P,
                                 y-P:y+P])

    def hash(self, id, img):
        (kps, descs) = computeSIFT(id, img)
        img_Y = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
        kps = sorted(kps,key=lambda kp: kp.response)
        means = [self.avg_mean(img_Y,int(kp.pt[0]),int(kp.pt[1])) for kp in kps]

        factor = img.shape[0] / self.size, img.shape[1] / self.size
        grid = np.zeros((self.size,self. size, int(360/self.angle)))
        keep = []
        for i in range(len(kps)):
            kp = kps[i]
            pos = int(kp.pt[0] / factor[1]), int(kp.pt[1] / factor[0]), int(kp.angle / self.angle)
            if grid[pos] < 1:
                grid[pos] = 1
                keep.append(i)
        return IndexItem(id, [descs[i] for i in keep], [kps[i] for i in keep])

    def dims(self):
        return 128

class ORBHasher(Hasher):

    def __init__(self):
        Hasher.__init__(self)

    def hash(self, id, img):
        (kps, descs) = computeORB(img)
        return IndexItem(id, descs, kps)

    def dims(self):
        return 128

class SURFHasher(Hasher):

    def __init__(self):
        Hasher.__init__(self)

    def hash(self, id, img):
        (kps, descs) = computeSURF(img)
        return IndexItem(id, descs, kps)

    def dims(self):
        return 256

class GCLMAdornmentHasher(Hasher):
    def __init__(self,indexer):
        Hasher.__init__(self)
        self.indexer=indexer

    def _replaceDescriptor(self,img,item):
        item.descriptor = gclm(img,item.keypoint.pt,item.keypoint.angle)
        return item

    def hash(self, id, img):
        items = self.indexer.hash(id, img)
        return [self._replaceDescriptor(img,item) for item in items]


def formName(index, indexer, **kwargs):
    pairs = ['{}={}'.format(k,v) for k,v in kwargs.items()]
    return '{}[{}]({})'.format(index.__class__.__name__,indexer.name, ', '.join(pairs))

class Index:

    def __init__(self, hasher, **kwargs):
        """
        :param indexer:
        @type hasher: Hasher
        """
        self.indexer =hasher
        self.name = formName(self, hasher, **kwargs)

    def setName(self,**kwargs):
        self.name = formName(self, self.hasher, **kwargs)

    def index(self, id, img):
        return self.hasher.hash(id, img)

    def find(self, id, img):
        """
        :param id:
        :param img:
        :return:
        @rtype: list of IndexItem
        """
        return []

    def keys(self):
        return []

class NoVectorFilter(VectorFilter):

    def __init__(self):
        VectorFilter.__init__(self)

    def filter_vectors(self, input_list):
        return input_list

def memoryStorage():
    return MemoryStorage()

def redisStorage(host='localhost'):
    return RedisStorage(Redis(host=host, port=6379, db=0))

class LSHIndex(Index):

    def __init__(self, hasher, number_of_tables=6, length_of_tables=12, match_thresh=0.2, association_thresh=0.1, storage=memoryStorage):
        """
        :param hasher:
        @type hasher: Hasher
        """
        Index.__init__(self, hasher,
                       number_of_tables=number_of_tables,
                       length_of_tables=length_of_tables,
                       match_thresh=match_thresh,
                       association_thresh=association_thresh)
        self.hasher = hasher
        self.match_thresh = match_thresh
        self.association_thresh = association_thresh
        self.tables = [None]*number_of_tables
        for i in range(number_of_tables):
            self.tables[i] = RandomBinaryProjections(str(i), length_of_tables)
        self.engine = Engine(self.hasher.dims(),
                             lshashes=self.tables,
                             storage=storage(),
                             fetch_vector_filters=[NoVectorFilter()])

    def index(self, id, img):
        item = self.hasher.hash(id, img)
        for i in range(len(item.descriptors)):
            self.engine.store_vector(item.descriptors[i],data=(id, item.keypoints[i], item.descriptors[i]))
        return item

    def find(self, id, img, index_if_not_found=False):
        item = self.hasher.hash(id, img)
        matches = {}
        #count_min =self.association_thresh * float(len(item.descriptors))
        for x in item.descriptors:
            for neighbour in self.engine.neighbours(x):
                if neighbour[1][0] in matches:
                    continue
                y = neighbour[1][2]
                dist = l2norm(x, y)
                key = neighbour[1][0]
                if dist < self.match_thresh:
                    #if dist > 0.0001:
                    #    print('{} {} {}'.format(id, neighbour[1][0], dist))
                    matches[key] = (matches[key] + 1) if key in matches else 1
        if id not in matches and index_if_not_found:
            for i in range(len(item.descriptors)):
                self.engine.store_vector(item.descriptors[i], data=(id, item.keypoints[i], item.descriptors[i]))
        #for id, count in matches.items():
        #    #if count >= count_min:
        #    yield id
        return list(matches.keys())


class LSHDiscreteIndex(LSHIndex):

    def __init__(self, hasher, number_of_tables=8, length_of_tables=32, bin_width= 1.0, match_thresh=0.2):
        """
        :param hasher:
        @type hasher: Hasher
        """
        LSHIndex.__init__(self, hasher, match_thresh=match_thresh)
        self.setName(number_of_tables=number_of_tables,length_of_tables=length_of_tables,match_thresh=match_thresh,bin_width=bin_width)
        self.tables = [None]*number_of_tables
        for i in range(number_of_tables):
            self.tables[i] = RandomDiscretizedProjections(str(i), length_of_tables,  bin_width)
        self.engine = Engine(self.hasher.dims(), lshashes=self.tables, fetch_vector_filters=[NoVectorFilter()])

class MemoryHashIndex(Index):
    """
    Hash the descriptors
    """
    def __init__(self, hasher):
        """
        :param hasher:
        @type hasher: Hasher
        """
        Index.__init__(self, hasher)
        self.hasher = hasher
        self.index_data = {}
        self.hasher = lambda x: sha256(x).hexdigest()

    def index(self, id, img):
        item = self.hasher.hash(id, img)
        for i in range(len(item.descriptors)):
            sig = self.hasher(item.descriptors[i])
            if sig not in self.index_data:
                self.index_data[sig] = []
            self.index_data[sig].append(item)
        return item

    def find(self, id, img):
        item = self.hasher.hash(id, img)
        for x in item.descriptors:
            sig = self.hasher(x)
            if sig in self.index_data:
                for item in self.index_data[sig]:
                    yield item.id

class NNIndex(Index):
    """
    NN search
    """

    def __init__(self, hasher, match_thresh=37.0):
        """
        :param hasher:
        @type hasher: Hasher
        """
        Index.__init__(self, hasher, match_thresh=match_thresh)
        self.hasher = hasher
        self.index_data = []
        self.kdt = None
        self.count = 0
        self.match_thresh = match_thresh

    def index(self, id, img):
        item = self.hasher.hash(id, img)
        for desc in item.descriptors:
            self.index_data.append((item.id,desc))
        return item

    def _messageData(self):
        X = np.zeros((len(self.index_data),self.hasher.dims()))
        pos = 0
        for id,desc in self.index_data:
            X[pos,:] = desc
            pos+=1
        return X


    def find(self, id, img):
        if self.kdt is None:
            self.kdt = KDTree(self._messageData(), leaf_size=24, metric='euclidean')
        item = self.hasher.hash(id, img)
        for x in item.descriptors:
                distances, indices = self.kdt.query(np.reshape(x, (1, len(x))),k=10)
                for p in range(len(indices[0])):
                    if distances[0][p] < self.match_thresh:
                        yield self.index_data[indices[0][p]][0]

class MemoryIndex(Index):
    """
     Linear search
    """
    def __init__(self, hasher, match_thresh=0.1):
        """
        :param hasher:
        @type hasher: Hasher
        """
        Index.__init__(self, hasher, match_thresh=match_thresh)
        self.hasher = hasher
        self.index_data = []
        self.match_thresh=match_thresh

    def index(self, id, img):
        item = self.hasher.hash(id, img)
        self.index_data.append(item)
        return item

    def find(self, id, img):
        item = self.hasher.hash(id, img)
        for x in item.descriptors:
            for indexed_item in self.index_data:
                for y in indexed_item.descriptors:
                    dist = l2norm(x,y)
                    if dist < self.match_thresh:
                        yield indexed_item.id

class KLSHIndex(Index):

    def __init__(self, hasher, match_thresh=37.0):
        """
        :param hasher:
        @type hasher: Hasher
        """
        Index.__init__(self, hasher, match_thresh=match_thresh)
        self.hasher = hasher
        self.index_data = []
        self.klsh = None
        self.count = 0
        self.match_thresh = match_thresh

    def index(self, id, img):
        item = self.hasher.hash(id, img)
        for desc in item.descriptors:
            self.index_data.append((item.id, desc))
        return item

    def _messageData(self):
        X = np.zeros((len(self.index_data), self.hasher.dims()))
        pos = 0
        for id, desc in self.index_data:
            X[pos, :] = desc
            pos += 1
        return X

    def build(self):
        self.klsh = KernelLSH(nbits=8, kernel='rbf', random_state=42)
        self.klsh.fit(self._messageData())

    def find(self, id, img):
        if self.klsh is None:
            self.build()
        item = self.hasher.hash(id, img)
        for x in item.descriptors:
            indices = self.klsh.query(np.reshape(x, (1, len(x))), k=10)
            for p in range(len(indices[0])):
                y = self.index_data[indices[0][p]][1]
                dist = l2norm(x, y)
                if dist < self.match_thresh:
                    yield self.index_data[indices[0][p]][0]

""""
class GridIndex(Index):
    def __init__(self, hasher, match_thresh=0.1):
        self.hasher = hasher
        self.hasher = {}
        self.match_thresh=match_thresh
        self.name = 'GridIndex[{}];match_thresh={}'.format(hasher.__class__.__name__,match_thresh)

    def index(self, id, img):
        item = self.hasher.index(id, img)
        for desc in item.descriptors:
            if desc not in self.index_data:
                self.index_data[desc] = []
            self.index_data[desc].append(item)
        return item

    def find(self, id, img, check_matches=False):
        item = self.hasher.index(id, img)
        for desc in item.descriptors:
            for indexed_item in self.index_data:
                for y in indexed_item.descriptors:
                    dist = l2norm(x,y)
                    if dist < self.match_thresh:
                        yield indexed_item.id

"""