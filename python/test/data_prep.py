# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
import cv2
for root, dirs, files in os.walk('../../data'):
    for name in files:
        if name.endswith('jpg'):
           img = cv2.imread(os.path.join(root, name))
           for size_factor in [0.8,0.6]:
               img_small = cv2.resize(img,(int(size_factor*img.shape[1]),int(size_factor*img.shape[0])))
               parts = os.path.splitext(name)
               cv2.imwrite(os.path.join(root,parts[0] + '_' + str(size_factor) + parts[1]),img_small)
