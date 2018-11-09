# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
from aida.api.textloader import loadUsers,create_db_app
from aida.ldcrepo.textloader import load
from aida.api.model import db
import tempfile

def init_db():
    import shutil
    import platform
    dbfile = os.path.join(os.getcwd(), 'test', 'test_db_dir', 'test.db')
    testdir = os.path.join(os.getcwd(), 'test', 'test_db_dir')
    if os.path.exists(testdir):
        shutil.rmtree(testdir)
    os.makedirs(testdir)
    if platform.system().lower()[0:3] == 'win':
       dbfile = dbfile[3:],
    config = {'SQLALCHEMY_DATABASE_URI': 'sqlite:////' + dbfile,
              'TESTING': True,
              'MEDIA_LOCATION':'test/data/sample',
              'SQLALCHEMY_TRACK_MODIFICATIONS':False
              #'REDIS_HOST':'localhost'
             }
    app = create_db_app('aida', external_config=config)
    with app.app_context():
        db.init_app(app)
        db.create_all()
        loadUsers('test/data/users.txt')
        load(app, dirs=['test/data/sample'])
    return config