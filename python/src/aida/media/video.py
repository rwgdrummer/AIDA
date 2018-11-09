# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import cv2
import os
from aida.media.key_frame_extractor import KeyFrameExtractor
from subprocess import Popen, PIPE
from aida.ldctools.textloader import log
from aida.ldctools import ldc
from logging import INFO, ERROR

def getReferenceFile(filename):
    return cv2.imread(filename)

def findFFMPEG():
    try:
        p = Popen('ffmpeg', stderr=PIPE)
        p.communicate()
        return 'ffmpeg'
    except FileNotFoundError as e:
        try:
            return os.environ['FFMPEG_BIN']
        except KeyError:
            log(ERROR,'Cannot find ffmpeg.  Environment variable FFMPEG_BIN not set')

ffmpeg_command = findFFMPEG()

def getReferencedFramesGivenSegments(filename, segments=[], chunk_size=20, alternate_directory=None):
    """

    :param filename:
    :param segments:
    :param chunk_size:
    :return:
    @rtype: list (VideoSegment)
    """
    chunks = [segments[i:i + chunk_size] for i in range(0, len(segments), chunk_size)]
    frames_done = 0
    for chunk in chunks:
        expression = ['eq(n\,%d)' % (segment.representative_frame_number) for segment in chunk]
        base = os.path.splitext(filename)[0]
        if alternate_directory is not None:
            base = os.path.join(alternate_directory,os.path.basename(base))
        expression_str = '+'.join(expression)
        if ffmpeg_command is None or len(ffmpeg_command) == 0:
            log(ERROR,'FFMPEG COMMAND NOT FOUND')
        command = [ffmpeg_command, '-i', filename, '-vf', 'select=' + expression_str, '-vsync', '0', '-start_number',
                   str(frames_done), '{}_%06d.png'.format(base)]
        log(INFO, ' '.join(command))
        p = Popen(command, stderr=PIPE)
        stderr = p.communicate()
        if p.returncode == 0:
            for i in range(len(chunk)):
                segment = segments[frames_done]
                segment_file = '%s%06d.png' % (base + '_', frames_done)
                segment.set_sample_img(cv2.imread(segment_file), segment_file)
                yield segment
        else:
            log(ERROR, stderr)

def getReferenceFrames(filename,extractor=KeyFrameExtractor(),chunk_size=20):
    """
    :param filename:
    :param extractor:
    :return:
    @rtype: list of Segment
    """
    segments = extractor.extract_from_file(filename)
    if len(segments) > 0:
        if segments[0].frame_file_name is not None:
            for segment in segments:
                if segment.frame_file_name is not None:
                    # TODO...well this sucks.  Not sure why this occurs.
                    segment.set_sample_img(cv2.imread(segment.frame_file_name), os.path.basename(segment.frame_file_name))
                    yield segment
        else:
            return getReferencedFramesGivenSegments(filename, segments, chunk_size=chunk_size)

class VideoMediaExtractor:

    def __init__(self,cineast):
        self.cineast = cineast

    def extract(self, dirs, destination):
        extractor = KeyFrameExtractor(self.cineast)
        for dir in dirs:
            ldc.unZipAll(dir, filters=['mp4'], location=destination, unwrap_files=True, cleanup=True)
        object_json = os.path.join(destination, 'json', 'cineast_multimediaobject.json')
        segment_json = os.path.join(destination, 'json', 'cineast_segment.json')
        representative_json = os.path.join(destination, 'json', 'cineast_representativeframes.json')
        if not os.path.exists(object_json) or not os.path.exists(segment_json):
            extractor.extract_all(job_path=destination, results_dir=destination)
        if not os.path.exists(object_json) or not os.path.exists(segment_json) or not os.path.exists(representative_json):
            log(ERROR,'key frame extraction failed')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directories to search.')
    parser.add_argument('--dirs', nargs='+', help='directories to search')
    parser.add_argument('--cineast', help='root directory of cineast')
    parser.add_argument('--destination', help='where to explode the files')
    args = parser.parse_args()
    VideoMediaExtractor(args.cineast).extract(args.dirs, args.destination)


if __name__ == '__main__':
    main()