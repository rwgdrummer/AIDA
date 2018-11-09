# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import sys
from json import loads, dumps
import unittest
from aida.media.key_frame_extractor import VideoSegment
from aida.media.video import getReferenceFrames


class SomeFrameExtractor:
    def extract_from_file(self, filename):
        """
        Extract data from file.  Do not retain the results.
        :param filename:
        :return: list of segments for the file
        @rtype: VideoSegment
        """
        return [VideoSegment(file_name=filename, segment_number=1, start=1, end=2, start_abs=0, end_abs=0.033,
                             representative_frame_number=1,frame_file_name=None),
                VideoSegment(file_name=filename, segment_number=2, start=20, end=21,start_abs=0.606, end_abs=0.642,
                             representative_frame_number=5,frame_file_name=None)]

class TestVideo(unittest.TestCase):

    def setUp(self):
       pass

    def test_reference(self):
        segments = [x for x in getReferenceFrames('test/data/IMG_2379.MOV',SomeFrameExtractor())]
        self.assertEqual(2,len(segments))
        for segment in segments:
            self.assertIsNotNone(segment.sample_img)

