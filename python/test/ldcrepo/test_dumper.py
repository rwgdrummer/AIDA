# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import sys
import unittest
from aida.api.provider import app, db
from aida.ldcrepo.model import Segment, CanonicalMention
from aida.ldcrepo.textloader import create_db_app, dumpWithinContext, loadWithinContext
from initdb import init_db
import os
from shutil import rmtree

class TestDumper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = init_db()

    def _run_test(self, method):
        self.app = create_db_app('aida', external_config=TestDumper.config)
        with app.app_context():
            db.init_app(app)
            return method()

    def test_root(self):
        def work():
            db.create_all()
            s = Segment(id = 'test_seg_1234',
                    file_id='file_id',
                    segment_number=1,
                    segment_start=1,
                    segment_end=2,
                    segment_start_abs=1,
                    segment_end_abs=2,
                    representative_frame_number=1,
                    frame_file_name='foo.png')
            db.session.add(s)
            db.session.commit()
            c = CanonicalMention(id='test_can_1234',
                                 entity_mention_id='EM779948.000070',
                                 child_file='file_id',
                                 frame_number=1,
                                 frame_time=1,
                                 bounding_box='[1,2,3,4]')
            db.session.add(c)
            db.session.commit()
            if os.path.exists('test_dump_load'):
                rmtree('test_dump_load')
            os.mkdir('test_dump_load')
            dumpWithinContext(['test_dump_load'])
            db.session.delete(c)
            db.session.delete(s)
            loadWithinContext(['test_dump_load'])
            return db.session.query(Segment).all() + db.session.query(CanonicalMention).all()
        mentions =self._run_test(work)
        if os.path.exists('test_dump_load'):
            rmtree('test_dump_load')
        self.assertTrue(len(mentions) > 0)




