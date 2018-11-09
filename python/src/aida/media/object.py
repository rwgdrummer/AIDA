# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
import json

class MediaObject:

    def __init__(self,id, bounding_box, object_type, relationships=[]):
        """

        :param id:
        :param bounding_box:
        :param object_type:
        :param relationships: list of id, similarity
        @type relationships: list (str,float)
        """
        self.id = id
        self.bounding_box = bounding_box
        self.object_type = object_type
        self.relationships=relationships

    def text_bounding_box(self):
        return ','.join([str(self.bounding_box[0]),
                         str(self.bounding_box[1]),
                         str(self.bounding_box[0] + self.bounding_box[2]),
                         str(self.bounding_box[1] + self.bounding_box[3])])

class MediaObjectIdentifier:

    def extract(self, dirs, destination):
        pass

    def load(self, filename, object_type):
        """

        :param filename:
        :param object_type:
        :return:
        @rtype dict str:MediaObject
        """
        with open(filename,'r') as fp:
            d = json.load(fp)
            media = {node['ID']:MediaObject(node['imagePath'], node['faceRect'],object_type) for node in d['nodes']}
            for edge in d['edges']:
                media[edge['IDs'][0]].relationships.append((media[edge['IDs'][1]].id,edge['similarity']))
        return media

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Directories to search.')
    parser.add_argument('--dirs', nargs='+', help='directories to search')
    parser.add_argument('--destination', help='where to explode the files')
    args = parser.parse_args()
    MediaObjectIdentifier().extract(args.dirs, args.destination)
