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
from aida.api.provider import FlaskAppWrapper
from aida.api.api import UserRepo
from aida.ldcrepo.api import AIDARepo
from initdb import init_db
from unittest.mock import patch
from aida.api.model import UserProxy

def noneCheck(item,default_value=''):
    return default_value if item is None else item

def mock_jwt_required(realm):
    return


class TestServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = init_db()
        global client_app
        wrapper = FlaskAppWrapper(providers=[AIDARepo(),UserRepo()], external_config=config)
        wrapper.create_app()
        client_app = wrapper.test_app()

    def setUp(self):
        self.client = client_app
        response =  self.client.post('/api/v1/login',
                                     data=dumps({'username':'admin','password':'pass123'}),
                                     content_type='application/json')
        self.token = response.json['access_token']
        self.refresh = response.json['refresh_token']

    def _get_headers(self):
        return {'Authorization':'Bearer %s' % self.token}

    def test_root(self):
        response = self.client.get('/api/v1/')
        self.assertEqual (200,response.status_code)

    def test_entity_(self):
        response = self.client.get('/api/v1/entities')
        self.assertEqual (200,response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        self.assertTrue(json[0]["id"][0] == 'E')
        select_id = json[0]['id']
        response = self.client.get('/api/v1/entities/id/%s' % select_id)
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        self.assertTrue(json["id"] == select_id)

    def test_media(self):
        response = self.client.get('/api/v1/media?file_id=IC0011SL2.mp4.ldcc&frame_number=1')
        self.assertEqual(200, response.status_code)
        self.assertTrue('image' in response.content_type)
        response.stream.close()


    def test_entity_mentions(self):
        response = self.client.get('/api/v1/entities_without_canonical')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        self.assertTrue(json[0]["id"][0] == 'E')
        select_id = json[0]["id"]

        response = self.client.get('/api/v1/entity_mentions?entity_id={}'.format (select_id))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        for item in json:
            self.assertEqual(select_id,item['entity_id'])

        response = self.client.get('/api/v1/entity_mentions?status={}'.format('Approved'))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) >= 0)

        response = self.client.get('/api/v1/entity_mentions?status={}'.format('Recommend'))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 0)

        response = self.client.get('/api/v1/media')
        self.assertEqual(200, response.status_code)
        json = response.json

        data = {"entity_id":select_id, "provenance": json[0]['id']}
        response = self.client.post('/api/v1/entity_mentions',
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        json = response.json
        new_mention_id = json['id']

        response = self.client.get('/api/v1/entity_mentions?status={}'.format('Recommended'))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 1)
        for item in json:
            self.assertEqual(select_id, item['entity_id'])

        data = {"id": new_mention_id, "status": 'Approved'}
        response = self.client.post('/api/v1/entity_mentions',
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
        self.assertEqual(200, response.status_code)


        response = self.client.delete('/api/v1/entity_mentions?id={}'.format(new_mention_id),
                                       headers = self._get_headers())
        self.assertEqual(400, response.status_code)
        json = response.json

        data = {"id": new_mention_id, "status": 'Recommended'}
        response = self.client.post('/api/v1/entity_mentions',
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/api/v1/entity_mentions?id={}'.format(new_mention_id),
                                      headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        json = response.json

        response = self.client.get('/api/v1/entity_mentions?status={}'.format('Recommended'))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 0)

    def test_segments(self):
        response = self.client.get('/api/v1/segments/IC0011SL2.mp4.ldcc')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json)>0)
        selected = [item for item in json if noneCheck(item['frame_file_name'],'').endswith('v_2WrJ79KLbMbIZsGv_22.png')][0]
        self.assertEqual('Strobe Talbet Blames Russia',selected['segment_texts'][0]['text'])
        self.assertEqual('inf', selected['segment_texts'][0]['text_type'])

        response = self.client.get('/api/v1/segments_text/Talbet Blames')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual('Strobe Talbet Blames Russia', json[0]['segment_texts'][0]['text'])
        self.assertEqual('fac', json[0]['segment_objects'][0]['object_type'])

        response = self.client.get('/api/v1/segments_object/{}'.format(json[0]['segment_objects'][0]['id']))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json[0])>0)

        response = self.client.get('/api/v1/entity_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        for entity in json:
            if entity['media']['media_type'] == 'mp4':
                break

        data = {"entity_mention_id": entity['id'],
                "segment_id":selected['id'],
                "comment": 'Recommended Test'}
        response = self.client.post('/api/v1/comment',
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        json = response.json
        comment_id = json['id']

        response = self.client.get('/api/v1/segment?segment_id=%s' % selected['id'])
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual('IC0011SL2.mp4.ldcc', json['file_id'])

        response = self.client.get('/api/v1/segment?file_id=IC0011SL2.mp4.ldcc&frame_no=200')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual('IC0011SL2.mp4.ldcc', json['file_id'])

        response = self.client.get('/api/v1/comment?segment_id=%s' % selected['id'])
        self.assertEqual(200, response.status_code)
        json = response.json[0]
        self.assertEqual('admin',json['user_id'])
        self.assertEqual('Recommended Test', json['comment'])

        response = self.client.get('/api/v1/entity_mentions?id={}'.format(entity['id']))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json['segment_comments']) == 1)

        response = self.client.delete('/api/v1/comment?id=%s' % comment_id,
                                      headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        json = response.json

        response = self.client.get('/api/v1/entity_mentions?id={}'.format(entity['id']))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue('segment_comments' not in json or len(json['segment_comments']) == 0)

    def test_canonicals(self):
        response = self.client.get('/api/v1/entities_without_canonical')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)
        self.assertTrue(json[0]["id"][0] == 'E')
        entity_count = len(json)

        response = self.client.get('/api/v1/entity_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        entities = []
        for entity in json:
            if entity['media']['media_type'] == 'mp4':
                entities.append(entity)
            if len(entities)>1:
                break
        media= []
        for entity in entities:
            response = self.client.get('/api/v1/parent_child_detail/provenance/{}'.format(entity['media']['id']))
            json = response.json
            media_file = json[0]['child_file']
            media.append(media_file)
            self.assertEqual(156,json[0]['segment_count'])

            data = {"entity_mention_id":entity['id'],
                    "child_file":media_file,"frame_number":100,
                    "frame_time":4.333,
                    "is_text":False}
            response = self.client.post('/api/v1/canonical_mentions',
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
            self.assertEqual(200, response.status_code)

        # check
        response = self.client.get('/api/v1/canonical_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2)

        entity_ids = [entity['entity_id'] for entity in entities]
        entity_mention_ids = [entity['id'] for entity in entities]

        for i in range(len(entities)):
            media_item = media[i]
            entity = entities[i]
            response = self.client.get('/api/v1/canonical_mentions/media/{}'.format(media_item))
            self.assertEqual(200, response.status_code)
            json = response.json
            self.assertTrue(len(json) > 0)
            self.assertTrue(json[0]['entity_mention_id'] in entity_mention_ids)
            mention_id = json[0]['id']

            response = self.client.get('/api/v1/canonical_mentions/entity/{}'.format(entity['entity_id']))
            self.assertEqual(200, response.status_code)
            json = response.json
            self.assertTrue(len(json) == 1)
            self.assertTrue(json[0]['entity_mention_id'] == entity['id'])
            mention_id = json[0]['id']

            response = self.client.get('/api/v1/canonical_mentions/entity_mention/{}'.format(entity['id']))
            self.assertEqual(200, response.status_code)
            json = response.json
            self.assertTrue(len(json) > 0)
            self.assertTrue(json[0]['entity_mention_id'] == entity['id'])
            mention_id = json[0]['id']

        response = self.client.get('/api/v1/entity_mentions_with_canonical')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2)
        self.assertTrue(len(json[0]) == 2)
        self.assertTrue(json[0][0]['entity_id'] in entity_ids)

        response = self.client.get('/api/v1/entity_mentions_with_canonical_count')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2543)
        self.assertTrue('per' in [p[2] for p in json])
        position = [p[4] for p in json].index(1)
        self.assertTrue(position >= 0)
        self.assertTrue(json[position][0] in entity_mention_ids)
        self.assertEqual(1, json[position][3])

        response = self.client.get('/api/v1/entities_with_canonical_count')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2327)
        position = [p[5] for p in json].index(1)
        self.assertTrue(json[position][0] in entity_ids)
        self.assertTrue('Igor' in json[position][1])
        self.assertTrue('per' in json[position][2])
        self.assertEqual(1, json[position][3])
        self.assertEqual(1, json[position][4])

        entity = entities[0]
        media_item = media[0]
        data = {"entity_mention_id": entity['id'], "child_file": media_item, "frame_number": 130}
        response = self.client.post('/api/v1/canonical_mentions'.format(entity['media']['id']),
                                    data=dumps(data),
                                    content_type='application/json',
                                    headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        response = self.client.get('/api/v1/canonical_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) > 0)

        response = self.client.get('/api/v1/entities_with_canonical_count?upper_bound=1')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) ==2326)

        response = self.client.get('/api/v1/entities_with_canonical_count?upper_bound=3')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2327)

        response = self.client.get('/api/v1/entities_without_canonical'.format(entity['media']['id']))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(entity['entity_id'] not in [d['id'] for d in json])

        response = self.client.delete('/api/v1/canonical_mentions/{}'.format(mention_id),
                                      headers=self._get_headers())
        self.assertEqual(200, response.status_code)
        response = self.client.get('/api/v1/canonical_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json)== 2)

        response = self.client.delete('/api/v1/canonical_mentions/{}'.format(json[0]['id']),
                                      headers=self._get_headers())
        self.assertEqual(200, response.status_code)

        response = self.client.get('/api/v1/canonical_mentions')
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 1)

        response = self.client.get('/api/v1/entities_without_canonical'.format(entity['media']['id']))
        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertTrue(len(json) == 2326)


