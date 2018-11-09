import math
import numpy as np
import random
from cv2 import filter2D

def _build_path(positions, length=0 , kern_size=8, start=0):
    """ Calculate the route for traversal between NxN kernels.
       Roughly follows a diagonal pattern starting from the top-left.
    """
    if length == 0:
        return positions
    last_pos = positions[start]
    if last_pos[0] == 0 and last_pos[1] < kern_size:
        new_y = last_pos[1]+ 1
        positions = positions + [(0, new_y)]
        length = length - 1
        if length == 0:
            return positions
    if last_pos[0] >= kern_size:
        return _build_path(positions, length=length, kern_size=kern_size, start=start+1)
    else:
        new_y = last_pos[1]
        new_x = last_pos[0] + 1
        return _build_path(positions + [(new_x, new_y)], length=length-1, kern_size=kern_size, start=start + 1)


def bindot(i,j):
    ib = bin(i)[2:]
    jb = bin(j)[2:]
    maxl = max(len(ib),len(jb))
    ib = '0' * (maxl - len(ib)) + ib
    jb = '0' * (maxl - len(jb)) + jb
    r = 0
    for pos in range(maxl):
        r += int(ib[pos]) * int(jb[pos])
    return r

"""https://en.wikipedia.org/wiki/Hadamard_transform"""
def gen_wh( kernel_size):
    full = np.zeros((kernel_size * kernel_size, kernel_size * kernel_size))
    n = math.log2(full.shape[0])
    for i in range(full.shape[0]):
        for j in range(full.shape[0]):
            full[i,j] = math.pow(-1,bindot(i,j))
    return full

class WH:
    matrix = None

    def __init__(self, matrix):

        self.matrix = matrix
        self.box = (int(math.sqrt(matrix.shape[0])),int(math.sqrt(matrix.shape[1])))

    def dot(self, position, img):
        """

        :param position:
        :param image:
        :return:
        @type patch: numpy.array
        """
        x = position[0]*self.box[0]
        y = position[1]*self.box[1]
        WHbox = self.matrix[x:x+self.box[0],y:y+self.box[1]]
        return filter2D(img, -1, WHbox) #,mode='constant')

class LHashTable:

    sequence = None
    format = ''


    def __init__(self,sequence, shifts=None, width=4):
        self.sequence = sequence
        self.width = float(width)
        for i in range(len(sequence)):
            self.format = self.format + 's16'
        if shifts is not None:
            self.shifts = np.asarray(shifts)
        else:
            self.shifts = np.zeros((len(self.sequence)))
            for i in range(len(self.sequence)):
                self.shifts[i] = random.uniform(0,width-1)

    def __eq__(self, other):
        return self.sequence == other.sequence

    def __repr__(self):
        return str(self.sequence)

    def __str__(self):
        return str(self.sequence)

    def composePixelCode(self,codes, i,j):
        from bitstruct import pack
        codelist = [code[i,j] for code in codes]
        return pack(self.format, *codelist)

    def hash(self, img, wh):
        code = np.zeros(img.shape).astype('int64')
        for i in range(len(self.sequence)):
            out = wh.dot(self.sequence[i], img)
            code = np.left_shift(code,8) +  ((out + self.shifts[i])/self.width).astype(int)
        return code

def _pickNextMove(position, visited=set()):
    moves = [(1, 0), (0, 1)]
    if position[0] > 0:
        moves.append((-1, 0))
    if position[1] > 0:
        moves.append((0, -1))
    moves = [move for move in moves if _addPosition(position,move) not in visited]
    if len(moves) == 0:
        return None
    return random.choice(moves)

def _addPosition(positiona, positionb):
    return (positiona[0] + positionb[0],positiona[1] + positionb[1])

def _perturbPositions(positions):
    move= None
    while True:
        try:
            while move is None:
                position = random.randint(1,len(positions)-1)
                newpositions = list(positions[0:position])
                move =_pickNextMove(positions[position - 1], visited=set(positions[0:position + 1]))
            newpositions.append(_addPosition(positions[position-1],move))
            return _computePositionSet(newpositions,length=len(positions)-len(newpositions))
        except:
            pass

def _computePositionSet(positions, length=0):
    if length == 0:
        return positions
    positions.append(_addPosition(positions[-1], _pickNextMove(positions[-1],visited=set(positions))))
    return _computePositionSet(positions,length=length-1)


def generateTableSet(number_of_tables = 2, length_of_tables=16, width=None):
    """
    :param number_of_tables:
    :param length_of_tables:
    :param width:
    :return:
    @rtype: list of LHashTable
    """
    tables = []
    if (number_of_tables >= length_of_tables):
        raise ValueError("number of tables cannot exceed length of tables")
    if width is None:
        width = length_of_tables
    base = _build_path([(0, 0)], length=length_of_tables-1, kern_size=width)
    while len(tables) < number_of_tables:
        table = LHashTable(base,width=width)
        base = _perturbPositions(base)
        if table in tables:
            continue
        tables.append(table)
    return tables

class IndexProcess:

    def __init__(self):
        pass

    def init(self,imgA, imgB, patch_size):
        pass

    def process(self, coordsA, coordsB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coordsB:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordsB : list of numpy.ndarray
        @rtype: bool
        """
        return False

    def process_single(self, coordsA, coordB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coords:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordB : numpy.ndarray
        @rtype: bool
        """
        return False

class IndexProcessCollector(IndexProcess):
    count = 0
    coordinates = []

    def __init__(self, maxCount = 0):
        self.count  = maxCount
        IndexProcess.__init__(self)

    def process_single(self, coordsA, coordB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coords:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordB : numpy.ndarray
        @rtype: bool
        """
        self.coordinates.append((coordsA, [coordB]))
        self.count -= 1
        return self.count > 0

    def process(self, coordsA, coordsB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coordsB:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordsB : list of numpy.ndarray
        @rtype: bool
        """
        self.coordinates.append((coordsA, coordsB))
        self.count-=1
        return self.count > 0

class DensityLabeler:

    blocks = 16
    patch_size =8
    maxes = (0,0)

    def __init__(self, shape,blocks=16):
        self.blocks = blocks
        self.grid = {} #dok_matrix((shape[0] / self.blocks, shape[1] / self.blocks))

    def increment(self, x,y):
        row = x/self.blocks
        col = y/self.blocks
        i = self.grid.get((row, col),0)
        self.maxes = (max(row,self.maxes[0]),max(col,self.maxes[1]))
        next = i+1
        self.grid[(row, col)] = next
        #self.grid.update({(row, col): next})

class LabelAssigner:
    label = 0
    imgA = None
    imgB = None


    def __init__(self,imgA,imgB,patch_size):
        self.imgA = imgA
        self.imgB = imgB
        self.patch_size = patch_size

    def next(self):
        self.label+=1
        return self.label

    def set_label_image(self,tree, x,y,label):
        start = tree.blocks*x,tree.blocks*y
        acoord_start = (int(start[0] / self.imgA.shape[0]), start[0] % self.imgA.shape[0])
        acoord_stop = (acoord_start[0]+self.patch_size,acoord_start[1]+self.patch_size)
        bcoord_start = (int(start[1] / self.imgB.shape[0]), start[1] % self.imgB.shape[0])
        bcoord_stop = (bcoord_start[0]+self.patch_size,bcoord_start[1]+self.patch_size)
        self.imgA[acoord_start[0]:min(acoord_stop[0],self.imgA.shape[0]),
                  acoord_start[1]::min(acoord_stop[1],self.imgA.shape[1])] = label
        self.imgB[bcoord_start[0]:min(bcoord_stop[0],self.imgB.shape[0]),
                  bcoord_start[1]:min(bcoord_stop[1],self.imgB.shape[1])] = label

    def get_image_label(self, tree,x,y):
        tree_coord = tree.blocks * x, tree.blocks * y
        acoord = (int(tree_coord[0] / self.imgA.shape[0]), tree_coord[0] % self.imgA.shape[0])
        return self.imgA[acoord]

    def find_neighbor_label(self,tree,x,y):
        """

        :param tree:
        :param x:
        :param y:
        :return:
        @type tree : DensityLabeler
        """
        if x > 0:
            label = self.get_image_label(tree,x-1,y)
            if label > 0:
                return label
            if y > 0:
                label = self.get_image_label(tree, x-1, y-1)
                if label > 0:
                    return label
        elif y > 0:
            label = self.get_image_label(tree, x, y - 1)
            if label > 0:
                return label
        return self.get_image_label(tree, x, y)

class DensityLabelerTree:

    trees = []
    """
    @type trees: list of DensityLabeler
    """

    def __init__(self, shape):
        self.trees = [0]
        for i in range(1):
            self.trees[i] = DensityLabeler(shape,blocks=int(math.pow(2,i*2+4)))

    def increment(self, x,y):
        for tree in self.trees:
            tree.increment(x,y)

    def _label_block(self, coord, tree_id, assigner,threshold=5):
        tree = self.trees[tree_id]
        if tree_id > 0:
            next_tree = tree = self.trees[tree_id-1]
            ratio = tree.blocks/next_tree.blocks
            for x in range(ratio):
                for y in range(ratio):
                    newx, newy = coord[0]*ratio + x, coord[1]*ratio + y
                    v = tree.grid.get((newx, newy), 0)
                    if v == 0 or v < threshold:
                        continue
                    self._label_block((newx,newy),tree_id-1, assigner,threshold=max(2,threshold /2))
        else:
            neighbor_label = assigner.find_neighbor_label(tree,coord[0],coord[1])
            neighbor_label = neighbor_label if neighbor_label > 0 else assigner.next()
            assigner.set_label_image(tree, coord[0],coord[1], neighbor_label)

    def xlabel_images(self,assigner,threshold=4):
        tree = self.trees[0]
        for k, v in tree.grid.iteritems():
            if v >= threshold:
                self._label_block(k, 0 ,assigner, threshold=threshold)

    def create_image(self,threshold=2):
        tree = self.trees[0]
        img = np.zeros((tree.maxes[0]/2+1,tree.maxes[1]/2+1))
        for k, v in tree.grid.iteritems():
            if v >= threshold:
                img[(k[0]/2,k[1]/2)] = v
        return img

    def label_images(self,assigner,threshold=1):
        from sklearn.cluster import DBSCAN
        d = DBSCAN(eps=500)
        tree = self.trees[0]
        coords = [k for k, v in tree.grid.iteritems() if v >= threshold]
        labels = d.fit_predict(coords)
        for i in range(len(coords)):
            label = labels[i]
            if label < 0:
                continue
            coord = coords[i]
            assigner.set_label_image(tree,coord[0],coord[1], label+1)


class ImageLabel(IndexProcess):

    ashape = (0,0)
    bshape = (0, 0)
    density_labeler = None

    def __init__(self):
        IndexProcess.__init__(self)

    def init(self, imgA, imgB, patch_size):
        """

        :param imgA:
        :param imgB:
        :return:
        @type imgA : ndarray
        @type imgB : ndarray
        """
        shape = (imgA.shape[0]*imgA.shape[1],imgB.shape[0]*imgB.shape[1])
        self.ashape = imgA.shape
        self.bshape = imgB.shape
        self.density_labeler = DensityLabelerTree(shape)
        self.patch_size = patch_size

    def process(self, coordsA, coordsB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coordsB:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordsB : list of numpy.ndarray
        @rtype: bool
        """
        for coordA in coordsA:
            for coordB in coordsB:
                self.density_labeler.increment(coordA[0]*self.ashape[0]+coordA[1],coordB[0]*self.bshape[0]+coordB[1])
        return True

    def process_single(self, coordsA, coordB):
        """

        :param imgA:
        :param imgB:
        :param coordsA:
        :param coords:
        :return:
        @type imgA : numpy.ndarray
        @type imgB : numpy.ndarray
        @type coordsA : list of numpy.ndarray
        @type coordB : numpy.ndarray
        @rtype: bool
        """
        for coordA in coordsA:
            self.density_labeler.increment(coordA[0] * self.ashape[0] + coordA[1],
                                           coordB[0] * self.bshape[0] + coordB[1])
        return True

    def create_mega_image(self):
        return self.density_labeler.create_image()

    def create_label_images(self):
        imgA = np.zeros(self.ashape)
        imgB = np.zeros(self.bshape)
        assigner = LabelAssigner(imgA,imgB,self.patch_size)
        self.density_labeler.label_images(assigner)
        return imgA, imgB


class CSHIndexer:

    def __init__(self):
        pass

    def init(self, number_of_tables=4, length_of_tables=6, patch_size=8):
        if length_of_tables > patch_size:
            raise ValueError("Precision is too high; length of tables > patch size")
        self.patch_size = patch_size
        self.tables = generateTableSet(number_of_tables=number_of_tables, length_of_tables=length_of_tables)
        self.wh = WH(gen_wh(patch_size))

    def hash_images(self,imgA,imgB,index_process):
        """

        :param imgA:
        :param imgB:
        :param index_process:
        :return:
        @type imgA: ndarray
        @type imgB: ndarray
        @type index_process: IndexProcess
        """
        pass

class CSHSingleIndexer(CSHIndexer):

    def __init__(self):
        CSHIndexer.__init__(self)

    def hash_images(self,imgA,imgB,index_process):
        """

        :param imgA:
        :param imgB:
        :param index_process:
        :return:
        @type imgA: ndarray
        @type imgB: ndarray
        @type index_process: IndexProcess
        """
        index = {}
        index_process.init(imgA, imgB,  self.patch_size)
        for table in self.tables:
            codeA =  table.hash(imgA, self.wh)
            codeB =  table.hash(imgB, self.wh)
            codeSetA = set(np.unique(codeA))
            codeSetB = set(np.unique(codeB))
            matchSet = codeSetA.intersection(codeSetB)
            matchDict={}
            for i in np.ndindex(codeA.shape):
                if codeA[i[0],i[1]] in matchSet:
                    matchDict[codeA[i[0],i[1]]] = imgA[i[0],i[1]]
            for i in np.ndindex(codeB.shape):
                if codeB[i[0],i[1]] in matchSet:
                    matchDict[imgB[i[0],i[1]]] = i

            for match in matchSet:
                for pair in zip(*np.where(codeA==match)):
                    if match not in index:
                        index[match] = [pair]
                    else:
                        index[match].append(pair)
                for pair in zip(*np.where(codeB==match)):
                    index_process.process_single(index[match], pair)

def compose_descriptor(src_pt,dst_pt):
    dist = math.sqrt(math.pow(dst_pt[0][0] - src_pt[0][0], 2) + math.pow(dst_pt[0][1] - src_pt[0][1], 2))
    m = (dst_pt[0][1] - src_pt[0][1]) / (dst_pt[0][0] - src_pt[0][0])
    return (dist,m, src_pt, dst_pt)

def find_lines(src, dst):
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import pairwise
    data_set = [compose_descriptor(src[i], dst[i]) for i in range(len(src))]
    data_set = [item for item in data_set if not (math.isnan(item[0]) or math.isinf(item[0])) and
                not (math.isnan(item[1]) or math.isinf(item[1])) and abs(item[1]) < 4]
    mean2 = np.median([item[0] for item in data_set])
    std2 = np.std([item[0] for item in data_set])
    data_set = [item for item in data_set if abs(item[0] - mean2) <0.5*std2]
    dist_slope =  [(item[0],item[1]) for item in data_set]
    distances = pairwise.euclidean_distances(dist_slope)
    mean2 = np.median(distances)
    ms = DBSCAN(eps=mean2)
    labels = ms.fit_predict(dist_slope)
    return data_set,labels
