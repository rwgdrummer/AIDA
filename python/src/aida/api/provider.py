# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
from  datetime import datetime, date
from json import JSONEncoder
from logging import INFO, ERROR

from aida.ldctools.textloader import log
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import BaseQuery
from jwt import register_algorithm, unregister_algorithm
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.collections import InstrumentedList
from werkzeug.exceptions import HTTPException

from .model import User, db, UserProxy

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})

try:
    unregister_algorithm('RS256')
    register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))
except:
    pass

def load_config(filename='config.json'):
    import json
    if filename is not None and os.path.exists(filename):
        with open(filename) as fp:
            return json.load(fp)
    print ('%s not found; using default configurations' % (filename if filename is not None else 'config.json'))
    return {}

def get_value_from_config(config, id, default=None):
    return default if id not in config else config[id]

class Provider:

    def __init__(self, name='Provider'):
        self.name = name

    def init(self,app=None,api=None):
        """

        :param app:
        :return:
        @type app: FlaskAppWrapper
        @type api: Api
        """

    def config(self, external_config={}):
        return {}

    def dependencies(self):
        """
        :return: list of dependent provider classes
        """
        return []

class InvalidCredentials(HTTPException):
    status_code = 401
    code=401

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class InvalidUsage(HTTPException):
    status_code = 400
    code=400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_invalid_credentials(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class FlaskAppWrapper:

    def __init__(self,providers, external_config={}):
        """
               :param providers:
               @type providers: list of Provider
        """
        self.providers = providers
        self.external_config = external_config

    def get_provider_by_name(self, name):
        for provider in self.providers:
            if provider.__class__.__name__ == name:
                return provider
        return None

    def _load_provider(self, app, provider):
        log(INFO,"Loading %s" % (provider.__class__.__name__))
        for k, v in provider.config(external_config=self.external_config).items():
            app.config[k] = v
        for dependency in provider.dependencies():
            if self.get_provider_by_name(dependency.__name__) is None:
                self.providers.append(dependency())
                self._load_provider(app,self.providers[-1])

    def create_app(self):
        global app
        import copy
        for provider in copy.copy(self.providers):
            self._load_provider(app,provider)
        self.app = app
        self.app.register_error_handler(InvalidUsage,handle_invalid_usage)
        self.app.register_error_handler(InvalidCredentials, handle_invalid_credentials)
        self.api = Api(self.app,prefix="/api/v1")
        return app

    def run_app(self,host='127.0.0.1'):
        with self.app.app_context():
            for provider in self.providers:
                provider.init(app=self, api=self.api)
        self.app.run(debug=True,host=host)

    def test_app(self):
        with self.app.app_context():
            for provider in self.providers:
                provider.init(app=self, api=self.api)
        return self.app.test_client()


class AllSecurityProvider(Provider):

    def __init__(self):
       Provider.__init__(self,SecurityProvider.__name__)

    def init(self,app=None,api=None):
        self.jwt = JWTManager(app=app.app)
                       #.app,authentication_handler=AllSecurityProvider.check_password,
                       #identity_handler=AllSecurityProvider.identity)
        #self.jwt.jwt_decode_callback = User.jwt_handler
        """
        :param app:
        :return:
        @type app: FlaskAppWrapper
        @type api: Api
        """

    @staticmethod
    def identity(payload):
        user_id = payload['identity']
        return {"username": user_id}

    @staticmethod
    def check_password(username, password):
        return UserProxy(username)

    def config(self, external_config={}):
        return {
            'JWT_SECRET_KEY': 'test123',
            'JWT_ALGORITHM':'HS256',
            'JWT_AUTH_USERNAME_KEY':'username',
            'JWT_AUTH_PASSWORD_KEY':'password'
        }

    def dependencies(self):
        return [ ]

class SecurityProvider(Provider):

    def __init__(self):
       Provider.__init__(self,SecurityProvider.__name__)

    def init(self,app=None,api=None):
        self.jwt = JWTManager(app=app.app)
        #,authentication_handler=SecurityProvider.check_password, identity_handler=SecurityProvider.identity)
        #self.jwt.jwt_decode_callback = User.jwt_handler
        """
        :param app:
        :return:
        @type app: FlaskAppWrapper
        @type api: Api
        """

    @staticmethod
    def identity(payload):
        user_id = payload['identity']
        return {"username": user_id}

    def config(self, external_config={}):
        return {
            'JWT_SECRET_KEY': 'test123',
            'JWT_ALGORITHM':'HS256',
            'JWT_AUTH_USERNAME_KEY':'username',
            'JWT_AUTH_PASSWORD_KEY':'password'
        }

    def dependencies(self):
        return [ UserProvider]

class UserProvider(Provider):

    def __init(self):
        Provider.__init__(self, name='UserProvider')

    def init(self, app=None, api=None):
        db.init_app(app.app)

    def config(self, external_config = {}):
        return {
            'SQLALCHEMY_DATABASE_URI': get_value_from_config(external_config,'SQLALCHEMY_DATABASE_URI','sqlite:////tmp/test.db'),
            'SQLALCHEMY_TRACK_MODIFICATIONS':False
        }

    def check_password(sel, username, password):
        user = db.session.query(User).filter(User.username==username).first()
        if user is not None:
            return UserProxy(username) if user.password == User.generate_hash(password) else None
        else:
            return None

    def get_users(self,username=None):
        if username is not None:
            return db.session.query(User).filter(User.username==username).first()
        return User.query.all()

    def add_user(self,username, password):
        user = self.get_users(username)
        if user is not None:
            user.password = User.generate_hash(password)
            db.session.merge(user)
        else:
            db.session.add(User(username=username, password= User.generate_hash(password)))
        db.session.commit()

class AlchemyEncoder(JSONEncoder):

    """
    Will need improvement here to be mor selective
    The idea is the add an optional __json__ method to the obj
    that returns which fiels to place in the 'fields'
    """
    def default(self, obj):
        def _prim_check(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj.__class__, InstrumentedList) or type(obj) == InstrumentedList:
                return [self.default(item) for item in obj]
            else:
                return obj

        def _complex_check(obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # an SQLAlchemy class
                fields = {}
                valid_values = obj.__json__() if hasattr(obj, '__json__') else None
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and \
                        (valid_values is None or x in valid_values)]:
                    data = obj.__getattribute__(field)
                    if isinstance(data, BaseQuery):
                        continue
                    result = _complex_check(data)
                    fields[field] = result
                return fields

            if isinstance(obj.__class__, InstrumentedList) or type(obj) == InstrumentedList:
                return [_complex_check(item) for item in obj]

            return _prim_check(obj)

        try:
            return _complex_check(obj)
        except TypeError as e:
            log(ERROR,str(e))
            return None
