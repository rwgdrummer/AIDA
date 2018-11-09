# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import unittest
from unittest.mock import patch

from aida.api.api import UserRepo
from aida.api.provider import FlaskAppWrapper
from initdb import init_db
from json import dumps

class TestServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = init_db()
        global client_app
        wrapper = FlaskAppWrapper(providers=[UserRepo()], external_config=config)
        wrapper.create_app()
        client_app = wrapper.test_app()

    def _get_headers(self):
        return {'Authorization':'Bearer %s' % self.token}

    def _get_refresh_headers(self):
        return {'Authorization': 'Bearer %s' % self.refresh}

    def setUp(self):
        self.client = client_app
        response =  self.client.post('/api/v1/login',
                                     data=dumps({'username':'admin','password':'pass123'}),
                                     content_type='application/json')
        self.token = response.json['access_token']
        self.refresh = response.json['refresh_token']


    def test_refresh(self):
        response = self.client.post('/api/v1/refresh',headers=self._get_refresh_headers())
        self.assertEqual(200, response.status_code)
        self.token = response.json['access_token']

    def test_users(self):
        response = self.client.get('/api/v1/users', headers=self._get_headers())
        self.assertEqual (200,response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        self.assertTrue('admin' in json["users"] )

    def test_failure(self):
        self.client = client_app
        response = self.client.post('/api/v1/login',
                                    data=dumps({'username': 'admin', 'password': 'badpass'}),
                                    content_type='application/json')
        self.assertEqual(401, response.status_code)
