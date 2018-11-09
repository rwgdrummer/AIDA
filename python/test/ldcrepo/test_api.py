# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import sys
import unittest
from aida.api.provider import FlaskAppWrapper, app
from aida.ldcrepo.api import LDCDBProvider
from aida.ldcrepo.textloader import create_db_app
from initdb import init_db

class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = init_db()

    def setUp(self):
        self.client = LDCDBProvider()

    def _run_test(self, method):
        self.app = create_db_app('aida', external_config=TestApi.config)
        with app.app_context():
            self.client.init(app=self)
            return method()

    def xtest_root(self):
        def work():
            return self.client.entities()
        mentions =self._run_test(work)
        self.assertTrue(len(mentions) > 0)
        self._run_test()




