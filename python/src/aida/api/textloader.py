# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import datetime
import os


"""
The DAO for the LDC KB model
"""

from flask import Flask
from aida.ldctools.textloader import map_column_values, FileReader
from aida.api.provider import get_value_from_config, load_config
from aida.api.model import User, db
import tempfile


def create_db_app(name, external_config):
    app = Flask(name)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_value_from_config(external_config,'SQLALCHEMY_DATABASE_URI',
                                                                  'sqlite:////{}test.db'.format(tempfile.gettempdir()))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


def loadUsers(filename, update=False):
    def processor(session, columns):
        values = map_column_values(columns,['username','password'],User)
        values['password'] = User.generate_hash(values['password'])
        if update:
            user = session.query(User).filter(User.username==values['username']).first()
            if user is not None:
                user.password = values['password']
            session.merge(user)
            return
        session.add(User(**values))
    FileReader(filename, sep=':',skip_first_line=False).read(db.session,processor)
    db.session.commit()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Load User Model.')
    parser.add_argument('--users',
                        help='user file')
    parser.add_argument('--config',
                        help='JSON config file')
    parser.add_argument('--update',action='store_true',
                        help='Update Passwords')

    args = parser.parse_args()
    config = load_config(filename=args.config)
    app = create_db_app('aida',external_config=config)
    with app.app_context():
        db.init_app(app)
        db.create_all()
        loadUsers(args.users,args.update)

if __name__ == "__main__":
    # execute only if run as a script
    main()