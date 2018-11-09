# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

from flask_restful import Resource

from aida.api.provider import Provider, get_value_from_config
from flask import render_template, request
from aida.media.video import getReferenceFrames
from aida.media.key_frame_extractor import ExtractorFactory
import os
import cv2
from .provider import IndexStore


"""
Indexer
"""
class IndexItem(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        extractor = kwargs.pop('extractor')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.extractor = extractor

    def config(self, external_config={}):
        self.location = get_value_from_config(external_config, 'MEDIA_LOCATION', '.')
        self.extractor_directory = get_value_from_config(external_config, 'EXTRACTOR_LOCATION', '.')
        return {
            'MEDIA_LOCATION': self.location,
            'EXTRACTOR_LOCATION': self.extractor_directory
        }

    """
    Probably sufficient to use one method to do both index and check.
    """
    def post(self):
        import copy
        #TODO need to consider audio as well
        vidfile = request.files['video'] if 'video' in request.files else None
        imgfile = request.files['image'] if 'image' in request.files else None
        file = imgfile if imgfile is not None else vidfile
        f = os.path.join(self.provider.index_dir, file.filename)
        cleanup = []
        file.save(f)
        cleanup.append(f)
        try:
            matches = {}
            # peel apart reference frames
            if vidfile is not None:
                """
                With videos, the id will have to consider the reference frame
                Does it matter that one video is a snippet from another?
                """
                for ref in getReferenceFrames(f, extractor=self.extractor):
                    d = copy.copy(ref.__dict__)
                    d.pop('sample_img')
                    self.provider.metaindex[ref.frame_file_name] = d
                    d['file_name'] = os.path.basename(d['file_name'])
                    for m in self.provider.indexer.find(ref.frame_file_name, ref.sample_img, index_if_not_found=True):
                        v = self.provider.metaindex[m]
                        matches[m]= '' if v is None else v
                    cleanup.append(ref.frame_file_name)
            else:
                img = cv2.imread(f)
                for m in self.provider.indexer.find(f, img, index_if_not_found=True):
                    v = self.provider.metaindex[m]
                    matches[m] = '' if v is None else v
        finally:
            for item in cleanup:
                try:
                    os.remove(item)
                except:
                    pass
        return {'matches': matches}

    def get(self):
        """
        See not in the last method, to return a media item by id
        :return:
        """
        return  {'nothing':'yet'}

class AIDAIndex(Provider):

    def __init(self):
        Provider.__init__(self, name=AIDAIndex.__name__)

    def init(self, app=None,api=None):
        """

        :param app:
        :param api:
        :return:
        @type app: FlaskAppWrapper
        """
        provider = app.get_provider_by_name(IndexStore.__name__)
        extractor = ExtractorFactory.build(**get_value_from_config(app.external_config,'INDEX_KEY_FRAME_EXTRACTOR',
                                          {
                                               "name":"SingleFrameKeyFrameExtractor",
                                               "parameters":{}
                                          }))
        api.add_resource(IndexItem, '/index', resource_class_kwargs={'provider':provider, 'extractor':extractor})

    def dependencies(self):
        return [IndexStore]



