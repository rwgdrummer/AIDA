# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import sys
import os
from json import loads, dumps
import unittest
from aida.media.key_frame_extractor import SegmentLoader,FixedLocationKeyFrameExtractor
from aida.media.video import getReferenceFrames
import shutil


class TestKeyFrameExtractor(unittest.TestCase):

    def setUp(self):
       pass

    def test_extractor(self):
        if os.path.exists('extract_test_data'):
            shutil.rmtree('extract_test_data')
        os.mkdir('extract_test_data')
        extractor = FixedLocationKeyFrameExtractor(os.environ['EXTRACTOR'],'extract_test_data')
        #TODO...well, this file does not work with the extractor WHY?
        segments = extractor.extract_from_file('test/data/IMG_2379.MOV')
        self.assertTrue(len(segments)>0)
        self.assertIsNotNone(segments[0].frame_file_name)
        shutil.rmtree('extract_test_data')

    def test_segment_loader(self):
        loader = SegmentLoader('test/data/sample/json/cineast_multimediaobject.json')
        segments = loader.load_segments()
        self.assertTrue(len(segments)>=157)
        self.assertEqual(1,segments[0].start)
        self.assertEqual(194, segments[0].end)
        self.assertTrue(segments[0].representative_frame_number > 1 and segments[0].representative_frame_number < 194)


