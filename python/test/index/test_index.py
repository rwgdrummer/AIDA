# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import sys
import unittest
from aida.api.provider import FlaskAppWrapper
from aida.index.api import AIDAIndex
from initdb import init_db

def noneCheck(item,default_value=''):
    return default_value if item is None else item

class TestIndex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = init_db()
        global client_app
        wrapper = FlaskAppWrapper(providers=[AIDAIndex()], external_config=config)
        wrapper.create_app()
        client_app = wrapper.test_app()

    def setUp(self):
        self.client = client_app

    def test_root(self):
        response = self.client.get('/api/v1/')
        self.assertEqual (200,response.status_code)

    def test_index(self):
        import os
        video = 'test/data/IMG_2379.MOV'
        video = os.path.join(os.getcwd(), video)
        data = dict(
            video=(open(video, "rb"), "IMG_2379.MOV"),
        )
        response = self.client.post('api/v1/index',content_type='multipart/form-data', data=data)
        self.assertEqual (200,response.status_code)
        json = response.json
        data['video'][0].close()
        data = dict(
            video=(open(video, "rb"), "IMG_2379.MOV"),
        )

        response = self.client.post('api/v1/index',content_type='multipart/form-data', data=data)
        self.assertEqual (200,response.status_code)
        json = response.json
        data['video'][0].close()
        self.assertEqual(1,len(json['matches']))
