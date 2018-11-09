# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

import datetime
import os

from aida.ldcrepo.model import Hypothesis, db, KB, EntityMention,RelativeMention,ParentChildDetail,\
    Segment,Entity,CanonicalMention,Media, SegmentText, SegmentComment, SegmentObject, SegmentObjectMatch
from aida.api.provider import Provider, get_value_from_config, InvalidUsage
from aida.media.video import getReferenceFrames
from aida.media.key_frame_extractor import SingleFrameKeyFrameExtractor
from aida.ldctools.textloader import format_value_by_name
from sqlalchemy import func, bindparam

class LDCDBProvider(Provider):

    def __init(self):
        Provider.__init__(self, name=LDCDBProvider.__name__)

    def init(self, app=None, api=None):
        db.init_app(app.app)

    def config(self, external_config = {}):
        return {
            'SQLALCHEMY_DATABASE_URI': get_value_from_config(external_config,'SQLALCHEMY_DATABASE_URI','sqlite:////tmp/test.db'),
            'SQLALCHEMY_TRACK_MODIFICATIONS':False
        }

    def entity_mentions(self, id=None, status=None):
        if id is not None:
            r =  db.session.query(EntityMention).filter(EntityMention.id==id).first()
            if r is None:
                raise InvalidUsage('Cannot find %s' % id)
            return r
        if status is not None:
            return db.session.query(EntityMention).join(Media).filter(EntityMention.status==status).all()
        return db.session.query(EntityMention).join(Media).all()

    def entity_mentions_by_entity(self, id=None):
        if id is not None:
            return db.session.query(EntityMention).filter(EntityMention.entity_id==id).first()
        return db.session.query(EntityMention).join(Media).all()

    def segments_by_object(self, object_id, min_similarity=0):
        return db.session.query(SegmentObject, SegmentObjectMatch.measure, Segment).\
            join(Segment).\
            join(SegmentObjectMatch, SegmentObjectMatch.to_obj == SegmentObject.id).\
                   filter(SegmentObjectMatch.from_obj == object_id,
                          SegmentObjectMatch.measure >= bindparam('min_similarity')).\
                   params(min_similarity=min_similarity).all() + \
               db.session.query(SegmentObject, Segment). \
                   join(Segment). \
                   join(SegmentObjectMatch, SegmentObjectMatch.from_obj == SegmentObject.id). \
               filter(SegmentObjectMatch.to_obj == object_id,
               SegmentObjectMatch.measure >= bindparam('min_similarity')).\
                   params(min_similarity=min_similarity).all()

    def segments_by_text(self, text=None):
        return db.session.query(Segment).join(SegmentText).filter(SegmentText.text.contains(text)).all()

    def get_segment_by(self,file_id=None, frame_no=None, page_no=None, segment_id = None):
        if segment_id is not None:
            return Segment.query.filter(Segment.id == segment_id).first()
        elif file_id is not None:
            if frame_no is not None:
                return Segment.query.filter(Segment.file_id == file_id,
                                     Segment.segment_start <= int(frame_no),
                                     Segment.segment_end >= int(frame_no)
                                     ).first()
            else:
                return Segment.query.filter(Segment.file_id == file_id,
                                     Segment.segment_start <= page_no,
                                     Segment.segment_end >= page_no
                                     ).first()
        raise InvalidUsage('requires segment_id and one of frame_no or page_no')

    def segments(self, file_id=None):
        if file_id is not None:
            return Segment.query.filter(Segment.file_id == file_id).all()
        q = db.session.query(Segment)
        return q.all()

    def entities_with_canonical_count(self, upper_bound=None):
        q = db.session.query(EntityMention.entity_id,
                             Entity.description,
                             Entity.entity_type,
                             func.count(EntityMention.id).label('mentions'),
                             func.count(ParentChildDetail.id).label('media'),
                             func.count(CanonicalMention.id).label('canonicals')
                             ).\
           outerjoin(CanonicalMention). \
           filter(Entity.id == EntityMention.entity_id). \
           outerjoin(ParentChildDetail,ParentChildDetail.child_file.like(EntityMention.provenance + '.%')).\
           group_by(EntityMention.entity_id)
        if upper_bound is not None:
            q = q.having(func.count(CanonicalMention.id) <= bindparam('upper_bound')).params(upper_bound=upper_bound)
        return q.all()

    def entity_mentions_with_canonical_count(self,upper_bound=None, mention_types=['tme']):
        q = db.session.query(EntityMention.id,
                             EntityMention.description,
                             EntityMention.mention_type,
                             func.count(ParentChildDetail.id).label('media'),
                             func.count(CanonicalMention.id).label('canonicals')
                             ).\
                outerjoin(CanonicalMention). \
                outerjoin(ParentChildDetail, ParentChildDetail.child_file.like(EntityMention.provenance + '.%')). \
                group_by(EntityMention.id).\
                filter(EntityMention.mention_type.notin_(bindparam('mention_types',expanding=True))).\
            params(mention_types=mention_types)
        if upper_bound is not None:
            q = q.having(func.count(CanonicalMention.id) <= bindparam('upper_bound')).params(upper_bound=upper_bound)
        return q.all()

    def entity_mentions_with_canonicals(self):
        q = db.session.query(EntityMention,CanonicalMention)
        q = q.join(CanonicalMention,EntityMention.id == CanonicalMention.entity_mention_id)
        return q.all()

    def parent_child_detail(self,id=None,unwrapper_md5=None,child_file=None,provenance=None):
        base_query = db.session.query(ParentChildDetail.id,
                                      ParentChildDetail.parent_uid,
                                      ParentChildDetail.child_file,
                                      ParentChildDetail.download_date,
                                      ParentChildDetail.dtype,
                                      ParentChildDetail.rel_pos,
                                      ParentChildDetail.unwrapped_md5,
                                      ParentChildDetail.url,
                                      ParentChildDetail.wrapped_md5,
                                      func.count(Segment.id).label('segment_count')). \
            outerjoin(Segment,Segment.file_id==ParentChildDetail.child_file)
        if id is not None:
            base_query =  base_query.filter(ParentChildDetail.id==id)
        elif provenance is not None:
            base_query = base_query.filter(ParentChildDetail.child_file.like(provenance + '.%'))
        elif unwrapper_md5 is not None:
            base_query =  base_query.filter(ParentChildDetail.unwrapper_md5==unwrapper_md5)
        elif child_file is not None:
            base_query =  base_query.filter(ParentChildDetail.child_file==child_file)
        base_query  = base_query.group_by(ParentChildDetail.id,
                                      ParentChildDetail.parent_uid,
                                      ParentChildDetail.child_file,
                                      ParentChildDetail.download_date,
                                      ParentChildDetail.dtype,
                                      ParentChildDetail.rel_pos,
                                      ParentChildDetail.unwrapped_md5,
                                      ParentChildDetail.url,
                                      ParentChildDetail.wrapped_md5)
        return [x._asdict() for x in base_query.all()]

    def entity_mentions_for_entity(self, entity_id):
        q = db.session.query(EntityMention).filter(EntityMention.entity_id == entity_id)
        return q.all()

    def entities(self, id=None):
        if id is not None:
            return db.session.query(Entity).filter(Entity.id==id).first()
        return db.session.query(Entity).all()

    def entities_without_canonical_mentions(self):
        q = db.session.query(Entity).join(EntityMention)
        subquery = db.session.query(CanonicalMention.entity_mention_id)
        q = q.filter(EntityMention.id.notin_(subquery))
        return q.all()

    def canonical_mentions_for_file(self, child_file):
        if child_file is not None:
            return CanonicalMention.query.filter(CanonicalMention.child_file == child_file).all()
        return []

    def canonical_mentions_for_entity(self, entity_id):
        if entity_id is not None:
            return db.session.query(CanonicalMention).join(EntityMention).filter(EntityMention.entity_id == entity_id).all()
        return []

    def canonical_mentions_for_entity_mention(self, mention_id):
        if mention_id is not None:
            return CanonicalMention.query.filter(CanonicalMention.entity_mention_id == mention_id).all()
        return []

    def canonical_mentions(self,id = None):
        if id is not None:
            r =  CanonicalMention.query.filter(CanonicalMention.id==id).first()
            if r is None:
                raise InvalidUsage('Cannot find %s' % id)
            return r
        q = db.session.query(CanonicalMention)
        return q.all()

    def delete_canonical_mentions(self,id):
        mentions = self.canonical_mentions(id=id)
        if id is not None and mentions is not None:
            db.session.delete(mentions)
            db.session.commit()
            return "ok"
        raise InvalidUsage('Cannot find  %s' % (id))

    def update_entity_mention(self,
                              entity_mention_id,
                              provenance=None,
                              status=None,
                              textoffset_startchar=None,
                              textoffset_endchar=None,
                              text_string=None,
                              justification=None,
                              level=None,
                              kb_id=None,
                              tree_id=None
                              ):
        entity = db.session.query(EntityMention).filter(EntityMention.id == entity_mention_id).first()
        if entity is None:
            raise InvalidUsage('Cannot find entity mention %s' % id)
        entity.kb_id = entity.kb_id if kb_id is None else kb_id
        entity.textoffset_startchar = entity.textoffset_startchar if textoffset_startchar is None else textoffset_startchar
        entity.textoffset_endchar = entity.textoffset_endchar if textoffset_endchar is None else textoffset_endchar
        entity.text_string = entity.text_string if text_string is None else text_string
        entity.justification = entity.justification if justification is None else justification
        entity.level = entity.level if level is None else level
        entity.tree_id = entity.tree_id if tree_id is None else tree_id
        entity.provenance = entity.provenance if provenance is None else provenance
        entity.status = entity.status if status not in ['Approved','Recommended','Rejected'] else status
        db.session.add(entity)
        db.session.commit()


    def delete_entity_mention(self,
                              entity_mention_id,
                              force=False
                              ):
        entity_mention = db.session.query(EntityMention).filter(EntityMention.id == entity_mention_id).first()
        if entity_mention is None:
            raise InvalidUsage('Cannot find entity mention %s' % entity_mention_id)
        if force:
            canonicals = db.session.query(CanonicalMention).filter(CanonicalMention.entity_mention_id==entity_mention_id).all()
            for canonical in canonicals:
                db.session.delete(canonical)
            comments = db.session.query(SegmentComment).filter(
                SegmentComment.entity_mention_id == entity_mention_id).all()
            for comment in comments:
                db.session.delete(comment)
        elif entity_mention.status == 'Approved':
            raise InvalidUsage('Cannot delete approved entity mention %s' % entity_mention_id)
        db.session.delete(entity_mention)
        db.session.commit()
        return True

    def add_entity_mention(self, entity_id, provenance,
                       textoffset_startchar=None,
                       textoffset_endchar=None,
                       text_string=None,
                       justification=None,
                       level=None):
        import uuid
        entity = db.session.query(Entity).filter(Entity.id == entity_id).first()
        if entity is None:
            raise InvalidUsage('Cannot find entity %s' % id)
        matches = db.session.query(EntityMention).filter(EntityMention.entity_id == entity_id,
                                                         EntityMention.provenance == provenance).all()
        if len(matches) > 0:
            raise InvalidUsage('Entity %s and Provenance %s already matched in %s' % (entity_id, provenance, id))

        mention_id = uuid.uuid4().urn
        db.session.add(EntityMention(id = mention_id,
                                     entity_id = entity_id,
                                     provenance = provenance,
                                     textoffset_startchar = textoffset_startchar,
                                     textoffset_endchar = textoffset_endchar,
                                     text_string = text_string,
                                     justification = justification if justification is not None else entity.description,
                                     mention_type = entity.entity_type,
                                     level = level,
                                     kb_id=entity.kb_id,
                                     tree_id=entity.tree_id,
                                     status='Recommended'))
        db.session.commit()
        return mention_id

    def add_canonical_mention(self, entity_mention_id, child_file,
                              frame_number=None,
                              frame_time=None,
                              page_number=None,
                              bounding_box=None,
                              is_text=False,
                              user_id='Unknown'
                              ):
        import uuid
        import datetime
        choices = db.session.query(ParentChildDetail).filter(ParentChildDetail.child_file==child_file).all()
        if len(choices) == 0:
            raise InvalidUsage('Invalid child_file %s' % (child_file))
        finds = db.session.query(CanonicalMention).filter(CanonicalMention.entity_mention_id==entity_mention_id,
                                                  CanonicalMention.child_file==child_file).all()
        if len(finds) > 0:
            for mention in finds:
                if (frame_number is not None and mention.frame_number == frame_number) or \
                    (mention.page_number is not None and page_number is not None and \
                    mention.page_number == page_number):
                        raise InvalidUsage('Already in system %s' % (finds[0].id))
        id = uuid.uuid4().urn
        frame_number = format_value_by_name(CanonicalMention,
                                            'frame_number',
                                            frame_number)
        frame_time = format_value_by_name(CanonicalMention,
                                          'frame_time',
                                          frame_time)
        page_number = format_value_by_name(CanonicalMention,
                                           'page_number',
                                           page_number)
        is_text = format_value_by_name(CanonicalMention,
                                           'is_text',
                                            is_text)
        if type(bounding_box) == list:
            bounding_box = ','.join(bounding_box)
        db.session.add(CanonicalMention(id=id,
                                        entity_mention_id= entity_mention_id,
                                        child_file=child_file,
                                        frame_number=frame_number,
                                        frame_time=frame_time,
                                        page_number=page_number,
                                        bounding_box=bounding_box,
                                        is_text=is_text,
                                        user_id=user_id,
                                        record_time=datetime.datetime.now()))
        db.session.commit()
        return id

    def get_media(self):
        return db.session.query(Media).all()

    def add_comment(self, entity_mention_id, segment_id, comment, user_id):
        import uuid
        import datetime
        id = uuid.uuid4().urn
        db.session.add(SegmentComment(id=id,
                                   entity_mention_id=entity_mention_id,
                                   segment_id=segment_id,
                                   comment=comment,
                                   user_id=user_id,
                                   record_time=datetime.datetime.now()))
        db.session.commit()
        return id

    def get_comment(self, comment_id=None, segment_id=None):
        if segment_id is not None:
            return db.session.query(SegmentComment).filter(SegmentComment.segment_id == segment_id).all()
        if comment_id is None:
            return db.session.query(SegmentComment).all()
        return db.session.query(SegmentComment).filter(SegmentComment.id == comment_id).first()

    def delete_comment(self,comment_id):
        choices = db.session.query(SegmentComment).filter(SegmentComment.id == comment_id).all()
        if len(choices) == 0:
            raise InvalidUsage('Invalid comment id %s' % (comment_id))
        for choice in choices:
            db.session.delete(choice)
        db.session.commit()
        return comment_id



class MediaProvider(Provider):
    def __init(self):
        Provider.__init__(self, name=MediaProvider.__name__)

    def init(self, app=None, api=None):
        pass

    def config(self, external_config={}):
        self.location = get_value_from_config(external_config, 'MEDIA_LOCATION', '.')
        self.extractor_directory = get_value_from_config(external_config, 'EXTRACTOR_LOCATION', '.')
        return {
            'MEDIA_LOCATION': self.location,
            'EXTRACTOR_LOCATION': self.extractor_directory
        }

    def get_media_for_file(self, filename='', frame_number=0):
        ldcc_file_name = os.path.join(self.location, filename)
        real_file_name = os.path.join(self.location, os.path.splitext(filename)[0])
        if not os.path.exists(ldcc_file_name) and not os.path.exists(real_file_name):
            raise InvalidUsage('Cannot find %s' % ldcc_file_name)
        if filename.endswith('ldcc') and not os.path.exists(real_file_name):
            from aida.ldctools import ldc
            real_file_name = ldc.unwrap(real_file_name)
        if os.path.splitext(real_file_name)[1] in ['.jpg','.png']:
            return real_file_name
        r = Segment.query.filter(Segment.file_id == filename).all()
        if len(r) > 0:
            for segment in r:
                if segment.segment_start <= frame_number and segment.segment_end >= frame_number and \
                    segment.frame_file_name is not None:
                        location = os.path.abspath(os.path.join(self.location,segment.frame_file_name))
                        if os.path.exists(location):
                            return location

        return [x for x in getReferenceFrames(real_file_name,extractor=SingleFrameKeyFrameExtractor(frame=frame_number))][0].frame_file_name

