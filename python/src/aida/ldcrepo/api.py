# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

from json import dumps,loads
from aida.api.provider import Provider,get_value_from_config, AlchemyEncoder, SecurityProvider,InvalidUsage
from .provider import LDCDBProvider, MediaProvider
from flask import  request,jsonify,send_file
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)

class PingResource(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return {"hello":"AIDA Users"}

class ParentChildDetail(Resource):
    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self,id=None):
        if id is not None:
            return loads(dumps(self.provider.parent_child_detail(id=id), cls=AlchemyEncoder))
        return loads(dumps(self.provider.parent_child_detail(), cls=AlchemyEncoder))

class ParentChildDetailChildFile(Resource):
    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self,id=None):
        if id is not None:
            return loads(dumps(self.provider.parent_child_detail(child_file=id), cls=AlchemyEncoder))
        return loads(dumps(self.provider.parent_child_detail(), cls=AlchemyEncoder))

class ParentChildDetailParentID(Resource):
    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self,id=None):
        if id is not None:
            return loads(dumps(self.provider.parent_child_detail(provenance=id), cls=AlchemyEncoder))
        return loads(dumps(self.provider.parent_child_detail(), cls=AlchemyEncoder))

class ParentChildDetailMD5(Resource):
    def __init__(self, *args, **kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self,id=None):
        if id is not None:
            return loads(dumps(self.provider.parent_child_detail(md5=id), cls=AlchemyEncoder))
        return loads(dumps(self.provider.parent_child_detail(), cls=AlchemyEncoder))

class EntityMentions(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('entity_id', type=str)
        self.parser.add_argument('id', type=str)
        self.parser.add_argument('status', type=str)
        self.parser.add_argument('force', type=str)

    def get(self):
        args = self.parser.parse_args()
        status = None
        if 'status' in args and args['status'] is not None:
            status = args['status']
        if 'entity_id' in args and args['entity_id'] is not None:
            entity_id = args['entity_id']
            return loads(dumps(self.provider.entity_mentions_for_entity(entity_id),cls=AlchemyEncoder))
        elif 'id' in args:
            id = args['id']
        else:
            id = None
        return loads(dumps(self.provider.entity_mentions(id=id, status=status), cls=AlchemyEncoder))

    @jwt_required
    def delete(self):
        args = self.parser.parse_args()
        force = (args['force'] == 'true') if 'force' in args else False
        if 'id' in args and args['id'] is not None:
            entity_id = args['id']
            return {"status": "ok" if self.provider.delete_entity_mention(entity_id,force=force) else "failed"}
        return {"status":"failed"}

    @jwt_required
    def post(self):
        content = request.get_json(silent=True)
        if 'id' in content:
            self.provider.update_entity_mention(content['id'],
                                                textoffset_startchar=get_value_from_config(content,
                                                                                           'textoffset_startchar',
                                                                                           None),
                                                textoffset_endchar=get_value_from_config(content, 'textoffset_endchar',
                                                                                         None),
                                                text_string=get_value_from_config(content, 'text_string', None),
                                                justification=get_value_from_config(content, 'justification', None),
                                                provenance=get_value_from_config(content, 'provenance', False),
                                                tree_id=get_value_from_config(content, 'tree_id', False),
                                                level=get_value_from_config(content, 'level', False),
                                                kb_id=get_value_from_config(content, 'kb_id', False),
                                                status=get_value_from_config(content, 'status', False))
            id = content['id']
        else:
            id = self.provider.add_entity_mention(content['entity_id'],
                                             content['provenance'],
                                             textoffset_startchar=get_value_from_config(content, 'textoffset_startchar',None),
                                             textoffset_endchar=get_value_from_config(content, 'textoffset_endchar', None),
                                             text_string=get_value_from_config(content, 'text_string', None),
                                             justification=get_value_from_config(content, 'justification', None),
                                             level=get_value_from_config(content, 'level', False))
        return {"status":"ok", "id":id}


class SegmentCommentResource(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str)
        self.parser.add_argument('segment_id', type=str)

    def get(self):
        args = self.parser.parse_args()
        id = args['id'] if 'id' in args else None
        segment_id =  args['segment_id'] if 'segment_id' in args else None
        return loads(dumps(self.provider.get_comment(comment_id=id, segment_id=segment_id), cls=AlchemyEncoder))

    @jwt_required
    def delete(self):
        args = self.parser.parse_args()
        if 'id' in args and args['id'] is not None:
            comment_id = args['id']
            return {"status": "ok" if self.provider.delete_comment(comment_id) else "failed"}
        return {"status":"failed"}

    @jwt_required
    def post(self):
        content = request.get_json(silent=True)
        if 'id' in content:
            raise InvalidUsage("Cannot update comment")
        else:
            id = self.provider.add_comment(content['entity_mention_id'],
                                           content['segment_id'],
                                           content['comment'],
                                           get_jwt_identity())
        return {"status":"ok", "id":id}

class EntityMentionsWithCanonical(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return loads(dumps(self.provider.entity_mentions_with_canonicals(), cls=AlchemyEncoder))

class EntitiesWithCanonicalCount(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('upper_bound', type=int)

    def get(self):
        args = self.parser.parse_args()
        upper_bound = args['upper_bound'] if 'upper_bound' in args else None
        return loads(dumps(self.provider.entities_with_canonical_count(upper_bound=upper_bound), cls=AlchemyEncoder))

class EntitiesWithOutCanonicalMentions(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return loads(dumps(self.provider.entities_without_canonical_mentions(), cls=AlchemyEncoder))

class EntityMentionsWithCanonicalCount(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return loads(dumps(self.provider.entity_mentions_with_canonical_count(), cls=AlchemyEncoder))

class EntitiesWithOutCanonicalMentions(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return loads(dumps(self.provider.entities_without_canonical_mentions(), cls=AlchemyEncoder))

class CanonicalMentionsMedia(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self,id=None):
        return loads(dumps(self.provider.canonical_mentions_for_file(id), cls=AlchemyEncoder))


class CanonicalMentionsEntityMention(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self, id=None):
        return loads(dumps(self.provider.canonical_mentions_for_entity_mention(id), cls=AlchemyEncoder))

class CanonicalMentionsEntity(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self, *args, **kwargs)
        self.provider = provider

    def get(self, id=None):
        return loads(dumps(self.provider.canonical_mentions_for_entity(id), cls=AlchemyEncoder))

class Entities(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self):
        return loads(dumps(self.provider.entities(), cls=AlchemyEncoder))

class EntitiesById(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self,id=None):
        return loads(dumps(self.provider.entities(id=id), cls=AlchemyEncoder))

class SegmentById(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.provider = provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_id', type=str)
        self.parser.add_argument('page_no', type=str)
        self.parser.add_argument('frame_no', type=str)
        self.parser.add_argument('segment_id', type=str)

    def get(self):
        args = self.parser.parse_args()
        file_id = args['file_id'] if 'file_id' in args else None
        segment_id =  args['segment_id'] if 'segment_id' in args else None
        frame_no = args['frame_no'] if 'frame_no' in args else None
        page_no = args['page_no'] if 'page_no' in args else None
        return loads(dumps(self.provider.get_segment_by(frame_no=frame_no,
                                                        page_no=page_no,
                                                        file_id=file_id,
                                                        segment_id=segment_id), cls=AlchemyEncoder))

class SegmentsByObject(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('min_similarity', type=float)

    def get(self,id=None):
        args = self.parser.parse_args()
        min_similarity = args['min_similarity'] if 'min_similarity' in args and args['min_similarity'] is not None else 0
        return loads(dumps(self.provider.segments_by_object(id, min_similarity=min_similarity), cls=AlchemyEncoder))

class SegmentsByText(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self,text=None):
        return loads(dumps(self.provider.segments_by_text(text=text), cls=AlchemyEncoder))

class Segments(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self,file_id=None):
        return loads(dumps(self.provider.segments(file_id=file_id), cls=AlchemyEncoder))

class MediaResource(Resource):

    def __init__(self,*args,**kwargs):
        media_provider = kwargs.pop('media_provider')
        query_provider = kwargs.pop('query_provider')
        Resource.__init__(self,*args,**kwargs)
        self.media_provider = media_provider
        self.query_provider = query_provider
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file_id', type=str)
        self.parser.add_argument('frame_number', type=int)

    def get(self):
        import os
        args = self.parser.parse_args()
        if 'file_id' not in args or args['file_id'] is None:
            return loads(dumps(self.query_provider.get_media(), cls=AlchemyEncoder))
        file_id = args['file_id']
        frame_number = args['frame_number']  #
        filename = self.media_provider.get_media_for_file(filename=file_id,frame_number=frame_number)
        #TODO: determine mimetype based on file type (e.g. gif)
        return send_file(filename, mimetype='image/%s' % (os.path.splitext(filename)[1])[1:])


class CanonicalMentions(Resource):

    def __init__(self,*args,**kwargs):
        provider = kwargs.pop('provider')
        Resource.__init__(self,*args,**kwargs)
        self.provider = provider

    def get(self,id=None):
        return loads(dumps(self.provider.canonical_mentions(id), cls=AlchemyEncoder))

    @jwt_required
    def delete(self,id=None):
        return {"status": self.provider.delete_canonical_mentions(id=id)}

    @jwt_required
    def post(self):
        content = request.get_json(silent=True)
        self.provider.add_canonical_mention(content['entity_mention_id'],
                                            content['child_file'],
                                            frame_number=get_value_from_config(content, 'frame_number',None),
                                            frame_time=get_value_from_config(content, 'frame_time', None),
                                            page_number=get_value_from_config(content, 'page_number', None),
                                            bounding_box=get_value_from_config(content, 'bounding_box', None),
                                            is_text=get_value_from_config(content, 'is_text', False),
                                            user_id=get_jwt_identity()
                                            )
        return {"status":"ok"}


class AIDARepo(Provider):

    def __init(self):
        Provider.__init__(self, name=AIDARepo.__name__)

    def init(self, app=None,api=None):
        provider = app.get_provider_by_name(LDCDBProvider.__name__)
        media_provider = app.get_provider_by_name(MediaProvider.__name__)
        api.add_resource(PingResource, '/', resource_class_kwargs={'provider':provider})
        api.add_resource(EntityMentions, '/entity_mentions', resource_class_kwargs={'provider': provider})
        api.add_resource(EntityMentionsWithCanonical, '/entity_mentions_with_canonical', resource_class_kwargs={'provider':provider})
        api.add_resource(EntityMentionsWithCanonicalCount, '/entity_mentions_with_canonical_count',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(Entities, '/entities', resource_class_kwargs={'provider': provider})
        api.add_resource(EntitiesById, '/entities/id/<string:id>', endpoint='e_byid',resource_class_kwargs={'provider': provider})
        api.add_resource(EntitiesWithOutCanonicalMentions, '/entities_without_canonical',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(EntitiesWithCanonicalCount, '/entities_with_canonical_count',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(CanonicalMentions, '/canonical_mentions',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(CanonicalMentions, '/canonical_mentions/<string:id>',
                         endpoint='cm_byid',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(CanonicalMentionsEntity, '/canonical_mentions/entity/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(CanonicalMentionsEntityMention, '/canonical_mentions/entity_mention/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(CanonicalMentionsMedia, '/canonical_mentions/media/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(ParentChildDetail, '/parent_child_detail',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(ParentChildDetail, '/parent_child_detail/<string:id>',
                         endpoint='pc_byid',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(ParentChildDetailChildFile, '/parent_child_detail/file/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(ParentChildDetailParentID, '/parent_child_detail/provenance/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(ParentChildDetailMD5, '/parent_child_detail/md5/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(Segments, '/segments',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(SegmentById, '/segment',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(Segments, '/segments/<string:file_id>',
                         endpoint='sm_byid',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(SegmentsByText, '/segments_text/<string:text>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(SegmentsByObject, '/segments_object/<string:id>',
                         resource_class_kwargs={'provider': provider})
        api.add_resource(MediaResource, '/media',
                         resource_class_kwargs={'media_provider': media_provider, 'query_provider': provider})
        api.add_resource(SegmentCommentResource,'/comment',
                         resource_class_kwargs={'provider': provider})

    def dependencies(self):
        return [SecurityProvider, LDCDBProvider, MediaProvider]

