# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

import os, json
from subprocess import Popen, PIPE
from aida.ldctools.textloader import format_value, log
from logging import INFO, ERROR

class VideoSegment:

    def __init__(self,
                 file_name,
                 segment_number,
                 start,
                 end,
                 start_abs,
                 end_abs,
                 representative_frame_number,
                 frame_file_name):
        """

        :param file_name:
        :param segment_number: int
        :param start: frame int
        :param end: frame int
        :param start_abs: time in float seconds
        :param end_abs: time in float seconds
        :param representative_frame_number: frame in the segment
        @type start: int
        @type end: int
        @type start_abs: float
        @type end_abs: float
        @type representative_frame_number: int
        @type frame_file_name: str
        """
        self.file_name = file_name
        self.segment_number = segment_number
        self.start = start
        self.end = end
        self.start_abs = start_abs
        self.end_abs = end_abs
        self.representative_frame_number = representative_frame_number
        self.frame_file_name=frame_file_name
        self.sample_img = None

    def set_sample_img(self, img, filename):
        self.sample_img = img
        self.frame_file_name = filename


def loadKeyFrames(object_file, client_file, frame_file, abspath=True):
    from aida.media.video import getReferencedFramesGivenSegments
    """
    Load key frames from the output of the NIST extractor
    :param object_file: cineast_multimediaobject.json
    :param client_file: cineast_segment.json
    :return:
    @rtype list of VideoSegment
    """
    import json
    objs = {}
    frames = {}
    media_root = os.path.split(os.path.dirname(object_file))[0]
    rep_frame_root = os.path.join(media_root,'representative_frames')
    if not os.path.exists(object_file):
        return []
    with open(object_file) as fp:
        data = json.load(fp)
        for object in data:
            filename = os.path.abspath(os.path.join(media_root,object['path']))
            if not os.path.exists(filename):
                filename = os.path.normpath(os.path.join(media_root, os.path.basename(filename)))
            objs[object['objectid']] = filename
    with open(frame_file) as fp:
        data = json.load(fp)
        for frame in data:
            frames[frame['id']] = frame['frame']
    with open(os.path.normpath(client_file)) as fp:
        data = json.load(fp)
        results =[]
        for segment in data:
            rep_frame_file = os.path.abspath(os.path.join(rep_frame_root,
                                          segment['objectid'],
                                          segment['segmentid'] + '.png'))
            if abspath:
                base_path = rep_frame_file
            else:
                base_path = os.path.join('representative_frames',
                                             segment['objectid'],
                                              segment['segmentid'] + '.png')
            values = [objs[segment['objectid']],
                      segment['segmentnumber'],
                      segment['segmentstart'],
                      segment['segmentend'],
                      segment['segmentstartabs'],
                      segment['segmentendabs'],
                      frames[segment['segmentid']] if segment['segmentid'] in frames else segment['segmentstart'],
                      base_path if os.path.exists(rep_frame_file) else None]
            vid_segment = VideoSegment(*values)
            if vid_segment.frame_file_name is None:
                for vid_segment in getReferencedFramesGivenSegments(filename,
                                                                    segments=[vid_segment],
                                                                    alternate_directory=os.path.dirname(base_path)):
                    vid_segment.sample_img = None
            results.append(vid_segment)
    return results

class KeyFrameExtractor:

    def __init__(self, extractor_location=None):
        """
        :param extractor_location: director location of extractor (if not in the PATH)
        """
        self.extractor_location = extractor_location
        settings = None
        try:
            settings_file = os.path.join(extractor_location, 'cineast.json')
            with open(settings_file, 'r') as fp:
                settings = json.load(fp)
        except:
            pass
        self.settings = settings

    def _compose_job_definition(self, path):
        return {
            "type": "VIDEO",
            "input": {
                "path": path,
                "depth": 2,
                "skip": 0,
                "id": {
                    "name": "UniqueObjectIdGenerator",
                    "properties": {}
                }
            },
            "extractors": [
                {
                    "name": "AverageColor"
                }
            ],
            "exporters": [
                {
                    "name": "ShotThumbNails",
                    "properties": {
                        "destination": "thumbnails/"
                    }
                },
                {
                    "name": "RepresentativeFrameExporter"
                }
            ],
            "database": {
                "writer": "JSON",
                "selector": "NONE"
            }
        }

    def extract_all(self, job_path='', results_dir ='.'):
        """
        Extract all videos found in dir and below.

        :param job_path: path of a
        :param results_dir: store the results in the given directory
        :return: True if success, if not, the output_dir content should NOT be changed (clean up)
        """
        import shutil
        job_path = os.path.abspath(job_path)
        data = self._compose_job_definition(job_path)
        str_ = json.dumps(data, indent=4, sort_keys=False, separators=(',', ': '), ensure_ascii=False)
        with open(os.path.join(results_dir, 'job.json'), 'w') as new_file:
            new_file.write(str_)
        shutil.copy(os.path.join(str(self.extractor_location),'mime.types'),'.')
        with open(os.path.join(results_dir, 'cineast.json'), 'w') as new_file:
            with open(os.path.join(self.extractor_location, 'cineast.json'), 'r') as fp:
                data = json.load(fp)
                data["extractor"]["outputLocation"] = results_dir
                str_ = json.dumps(data, indent=4, sort_keys=False, separators=(',', ': '), ensure_ascii=False)
                new_file.write(str_)
        command = ['java', '-Xmx6G', '-Xms6G', '-jar', os.path.join(str(self.extractor_location),'cineast.jar'),
                   '--job', os.path.abspath(os.path.join(results_dir, 'job.json')), '--config', os.path.abspath(os.path.join(results_dir, 'cineast.json'))]
        p = Popen(command, stderr=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate()
        log(INFO,stdout)
        log(ERROR,stderr)
        if p.returncode == 0:
            try:
                os.remove(os.path.abspath(os.path.join(results_dir, 'job.json')))
                os.remove( os.path.abspath(os.path.join(results_dir, 'cineast.json')))
            except:
                pass
        return p.returncode == 0

    def _load_segments(self, dir, abspath=False):
        loader = SegmentLoader(os.path.join(dir,'json','cineast_multimediaobject.json'))
        return loader.load_segments(abspath=abspath)

    def extract_from_file(self, filename):
        """
        Extract data from  media file.
        :param filename:
        :return: list of segments for the file
        @rtype: list of VideoSegment
        """
        if self.extract_all(filename, os.path.dirname(filename)):
            return self._load_segments( os.path.dirname(filename))


class FixedLocationKeyFrameExtractor(KeyFrameExtractor):

    def __init__(self,extractor_location=None,results_location='.'):
        KeyFrameExtractor.__init__(self,extractor_location=extractor_location)
        self.results_location = results_location

    def extract_from_file(self, filename):
        """
        Extract data from  media file.
        :param filename:
        :return: list of segments for the file
        @rtype: list of VideoSegment
        """

        if self.extract_all(filename, self.results_location):
            return self._load_segments(self.results_location, abspath=True)

class SingleFrameKeyFrameExtractor(KeyFrameExtractor):

    def __init__(self,frame=1):
        self.frame = frame

    def extract_all(self,dir, output_dir='.',):
        """
        Extract all videos found in dir and below.

        :param dir:
        :param output_dir: store the results in the given directory
        :return: True if success, if not, the output_dir content should NOT be changed (clean up)
        """
        pass

    def extract_from_file(self, filename):
        """
        Extract data from file.  Do not retain the results.
        :param filename:
        :return: list of segments for the file
        @rtype: VideoSegment
        """
        return [VideoSegment(file_name=filename,
                             segment_number=1,
                             start=self.frame,
                             end=self.frame+1,
                             start_abs=0,
                             end_abs=0.033,
                             representative_frame_number=self.frame,
                             frame_file_name=None)]

class ExtractorFactory:

    names = {
        "SingleFrameKeyFrameExtractor": SingleFrameKeyFrameExtractor,
        "KeyFrameExtractor":KeyFrameExtractor,
        "FixedLocationKeyFrameExtractor":FixedLocationKeyFrameExtractor
    }

    @staticmethod
    def build(name="",parameters={}):
        return ExtractorFactory.names[name](**parameters)

class SegmentLoader:

    def __init__(self, object_file="cineast_multimediaobject.json"):
        """
        Given the directry, look existing extact frames
        :param object_file:Full path name of the object_file
        """
        self.client_file = object_file.replace('multimediaobject','segment')
        self.frame_file = object_file.replace('multimediaobject', 'representativeframes')
        self.object_file = object_file

    def load_segments(self, abspath=False):
        """
        Look up in the results to find the specific file
        :param filename:
        :return: list of segments for the file
        @rtype: VideoSegment
        """
        return loadKeyFrames(self.object_file, self.client_file, self.frame_file, abspath=abspath)