# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from flask_restful import Resource
from .provider import UserProvider, Provider, SecurityProvider,InvalidCredentials
from flask_jwt import jwt_required
from flask import  request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)

class UserAuth(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def post(self):
        data = request.get_json(silent=True)
        user = self.provider.check_password(data['username'],data['password'])
        if user is not None:
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                    'message': 'Logged in as {}'.format(user.id),
                    'access_token': access_token,
                    'refresh_token': refresh_token}
        else:
            raise InvalidCredentials('Wrong credentials')



class UserResource(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    @jwt_required
    def get(self,username=None):
        if username == '?':
            return {"username": get_jwt_identity()}
        if username is not None:
            user = self.provider.get_users(username)
            return {"username": user.username if username is not None else 'NA'}
        else:
            return {"users": [user.username for user in self.provider.get_users()]}


class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

class UserRepo(Provider):

    def __init(self):
        Provider.__init__(self, name=UserRepo.__name__)

    def init(self, app=None,api=None):
        provider = app.get_provider_by_name(UserProvider.__name__)
        api.add_resource(UserResource, '/users', resource_class_kwargs={'provider':provider})
        api.add_resource(UserResource, '/users/username/<string:username>', endpoint='get_byname',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(TokenRefresh, '/refresh')
        api.add_resource(UserAuth, '/login', resource_class_kwargs={'provider': provider})

    def dependencies(self):
        return [SecurityProvider, UserProvider]

