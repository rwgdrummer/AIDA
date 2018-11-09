import random
import unittest

import cv2
import numpy as np

from aida.index.csh import gen_wh, generateTableSet, WH


class TestToolSet(unittest.TestCase):

    def _disturb(self, patch):
        for x in range(4):
            i = random.randint(0,7)
            j = random.randint(0, 7)
            patch[i,j] = patch[i,j] + random.randint(-30,30)

    def test_wh_generation(self):
        seq2 = gen_wh(4).astype(int)
        self.assertEqual(seq2.shape[0], 16)
        im = np.copy(seq2)
        im[im < 0 ]= 0
        im[im > 0] =255
        cv2.imwrite('foo.png',im.astype('uint8'))
#        for i in range(4):
#            for j in range(4):
#                quadsum = sum(sum(seq2[i*4:i*4+4,j*4:j*4+4]))
#                if (i,j)==(0,0):
#                    self.assertEqual(4,quadsum, msg=str((i,j)))
#                else:
#                    self.assertEqual(4, quadsum,msg=str((i,j)))
        #print seq2

    def test_hash(self):
        length_of_tables = 6
        tables= generateTableSet(number_of_tables=4, length_of_tables=length_of_tables)
        wh = WH(gen_wh(8))
        codes= {}
        patch = np.random.randint(0, 128, (8, 8))
        print ("test uniqueness within table set")
        for table in tables:
            code_m = table.hash(patch,wh)
            code_00 = code_m[0,0]
            self.assertTrue(code_00 not in codes)
            codes[code_00] = 1
        print ("test repeatability")
        for table in tables:
            code_m = table.hash(patch, wh)
            code_00 = code_m[0, 0]
            self.assertTrue(code_00 in codes)
        print ("test proximity")
        patch[0, 0] = patch[0, 0] - 1
        matches = 0
        for table in tables:
            code_m = table.hash(patch, wh)
            code_00 = code_m[0, 0]
            matches += 1 if code_00 in codes else 0
        self.assertTrue(matches <= length_of_tables/2,msg='proximity and precision')
        print ("test uniqueness across table set")
        self._disturb(patch)
        for table in tables:
            code_m = table.hash(patch, wh)
            code_00 = code_m[0, 0]
            self.assertTrue(code_00 not in codes)

    def plot_mega(self,a):
        import matplotlib.pyplot as plt
        plt.imshow(a)
        plt.show()

    def plot_match(self,a,b,posA, posB):
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.imshow(a)
        rect = patches.Rectangle(posA, 8, 8, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        ax.add_patch(rect)
        ax.set_title('Before')
        ax = fig.add_subplot(1, 2, 2)
        ax.imshow(b)
        rect = patches.Rectangle(posB, 8, 8, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        ax.add_patch(rect)
        ax.set_title('After')
        plt.show()

    def plot_label(self,a,b):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.imshow(a)
        #rect = patches.Rectangle(posA, 8, 8, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        #ax.add_patch(rect)
        ax.set_title('Before')
        ax = fig.add_subplot(1, 2, 2)
        ax.imshow(b)
        #rect = patches.Rectangle(posB, 8, 8, linewidth=1, edgecolor='r', facecolor='none')
        # Add the patch to the Axes
        #ax.add_patch(rect)
        ax.set_title('After')
        plt.show()

    """def xtest_two_images_si(self):
        from maskgen import tool_set
        from maskgen.image_wrap import ImageWrapper
        aorig = image_wrap.openImageFile ('tests/images/0c5a0bed2548b1d77717b1fb4d5bbf5a-TGT-17-CLONE.png')
        a = aorig.convert('YCbCr')
        borig = image_wrap.openImageFile('tests/images/0c5a0bed2548b1d77717b1fb4d5bbf5a-TGT-18-CARVE.png')
        b = borig.convert('YCbCr')
        index = CSHSingleIndexer()
        index.init(number_of_tables=2, length_of_tables=6)
        collector = ImageLabel()
        analysis={}
        src_dst_pts = tool_set.getMatchedSIFeatures(ImageWrapper(a.to_array()[:, :, 0]),
                                                    ImageWrapper(b.to_array()[:, :, 0]))
        data_set,labels = find_lines(src_dst_pts[0],src_dst_pts[1])

        label_set = set(np.unique(labels))
        label_set = set(label_set).difference(set([0,1]))
        dist = 125 / len(label_set)
        label_map = {}
        i=0
        for label in np.unique(labels):
            if label >= 0:
                label_map[label] = 124 + i*dist
                i+=1
        amask = np.zeros(a.to_array().shape,dtype=np.uint8)
        bmask = np.zeros(b.to_array().shape, dtype=np.uint8)

        for i in range(len(data_set)):
            result  = data_set[i]
            if labels[i] >= 0:
                amask[max(int(result[2][0][0])-5,0):min(int(result[2][0][0])+5,amask.shape[0]),
                      max(int(result[2][0][1])-5,0):min(int(result[2][0][1])+5,amask.shape[1]),:] = label_map[labels[i]]
                bmask[max(int(result[3][0][0]) - 5,0):min(int(result[3][0][0]) + 5,amask.shape[0]),
                      max(int(result[3][0][1]) - 5,0):min(int(result[3][0][1]) + 5,amask.shape[1]),:] = label_map[labels[i]]
        ImageWrapper(amask).save('amask.png')
        ImageWrapper(bmask).save('bmask.png')


        #index.hash_images(a.to_array()[:, :, 0], b.to_array()[:, :, 0], collector)
        #self.plot_mega(collector.create_mega_image())
        #resultA, resultB = collector.create_label_images()
        #self.plot_label(resultA,resultB)


def test_two_images(self):
    from maskgen import tool_set
    from maskgen.image_wrap import ImageWrapper
    aorig = image_wrap.openImageFile('tests/images/0c5a0bed2548b1d77717b1fb4d5bbf5a-TGT-17-CLONE.png')
    a = aorig.convert('YCbCr')
    borig = image_wrap.openImageFile('tests/images/0c5a0bed2548b1d77717b1fb4d5bbf5a-TGT-18-CARVE.png')
    b = borig.convert('YCbCr')
    index = CSHSingleIndexer()
    index.init(number_of_tables=2, length_of_tables=6)
    index.hash_images(ImageWrapper(a.to_array()[:, :, 0]),
                                                ImageWrapper(b.to_array()[:, :, 0]))

    collector = ImageLabel()
    analysis = {}
    src_dst_pts = tool_set.getMatchedSIFeatures()
    data_set, labels = find_lines(src_dst_pts[0], src_dst_pts[1])

    label_set = set(np.unique(labels))
    label_set = set(label_set).difference(set([0, 1]))
    dist = 125 / len(label_set)
    label_map = {}
    i = 0
    for label in np.unique(labels):
        if label >= 0:
            label_map[label] = 124 + i * dist
            i += 1
    amask = np.zeros(a.to_array().shape, dtype=np.uint8)
    bmask = np.zeros(b.to_array().shape, dtype=np.uint8)

    for i in range(len(data_set)):
        result = data_set[i]
        if labels[i] >= 0:
            amask[max(int(result[2][0][0]) - 5, 0):min(int(result[2][0][0]) + 5, amask.shape[0]),
            max(int(result[2][0][1]) - 5, 0):min(int(result[2][0][1]) + 5, amask.shape[1]), :] = label_map[labels[i]]
            bmask[max(int(result[3][0][0]) - 5, 0):min(int(result[3][0][0]) + 5, amask.shape[0]),
            max(int(result[3][0][1]) - 5, 0):min(int(result[3][0][1]) + 5, amask.shape[1]), :] = label_map[labels[i]]
    ImageWrapper(amask).save('amask.png')
    ImageWrapper(bmask).save('bmask.png')


    # index.hash_images(a.to_array()[:, :, 0], b.to_array()[:, :, 0], collector)
    # self.plot_mega(collector.create_mega_image())
    # resultA, resultB = collector.create_label_images()
    # self.plot_label(resultA,resultB)
    """