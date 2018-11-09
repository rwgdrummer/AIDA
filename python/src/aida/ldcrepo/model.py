# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from aida.api.model import db
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case
from sqlalchemy.schema import Index

class KB(db.Model):
    __tablename__ = 'kb'
    id = db.Column(db.String(64), primary_key=True)
    topic_id = db.Column(db.String(10), unique=False, nullable=False)
    category = db.Column(db.String(64), unique=False, nullable=False)
    handle = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(512), unique=False, nullable=False)
    relative_mentions = db.relationship('RelativeMention', backref='kb', lazy=True)
    entity_mentions = db.relationship('EntityMention', backref='kb', lazy=True)

    def __repr__(self):
        return '<KB %r>' % self.id

class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.String(64), primary_key=True)
    media_type = db.Column(db.String(10), unique=False, nullable=False)

    def __repr__(self):
        return '<Media %r>' % self.id

    def __json__(self):
        return ['id','media_type']

class Entity(db.Model):
    __tablename__ = 'entity'
    id = db.Column(db.String(64), primary_key=True)
    tree_id = db.Column(db.Integer(), unique=False, nullable=False)
    description = db.Column(db.String(512), unique=False, nullable=True)
    entity_type =  db.Column(db.String(40), unique=False, nullable=False)
    kb_id = db.Column(db.String(64), db.ForeignKey('kb.id'), nullable=False)

    def __json__(self):
        return ['id','tree_id','description','entity_type','kb_id']

class EntityMention(db.Model):
    columns =  ['id','tree_id','entity_id','provenance','textoffset_startchar',
                'textoffset_endchar','justification','text_string','mention_type',
                'level','kb_id', 'status',
                'media', 'segment_comments']

    __tablename__ = 'entity_mention'
    id = db.Column(db.String(64), primary_key=True)
    tree_id = db.Column(db.Integer(), unique=False, nullable=False)
    entity_id = db.Column(db.String(40), db.ForeignKey('entity.id'),unique=False, nullable=False)
    provenance = db.Column(db.String(10), db.ForeignKey('media.id'),unique=False,nullable=False)
    textoffset_startchar = db.Column(db.Integer(), unique=False, nullable=True)
    textoffset_endchar = db.Column(db.Integer(), unique=False, nullable=True)
    text_string = db.Column(db.String(256), unique=False, nullable=True)
    justification = db.Column(db.String(256), unique=False, nullable=True)
    mention_type = db.Column(db.String(40), unique=False, nullable=False)
    level = db.Column(db.String(40), unique=False, nullable=True)
    kb_id = db.Column(db.String(64), db.ForeignKey('kb.id'), nullable=False)
    status = db.Column(db.String(16), default="Approved")

    media = relationship("Media",foreign_keys=[provenance])
    entity = relationship("Entity", foreign_keys=[entity_id])#,primaryjoin='foreign(EntityMention.provenance) == remote(Media.id)')

    @hybrid_property
    def description(self):
        if self.justification is not None:
            return self.justification
        else:
            return self.text_string

    @description.expression
    def description(cls):
        return case([
            (cls.justification != None, cls.justification),
        ], else_=cls.text_string)

    def __json__(self):
        return self.columns


class Hypothesis(db.Model):
    __tablename__ = 'hypothesis'
    id = db.Column(db.String(64), primary_key=True)
    topic_name = db.Column(db.String(256), unique=False, nullable=False)
    hypothesis = db.Column(db.String(256), unique=False, nullable=False)
    text_query = db.Column(db.String(256), unique=False, nullable=False)

    def __json__(self):
        return ['id','hypothesis','topic_name','text_query']

class RelativeMention(db.Model):
    __tablename__ = 'relative_mention'
    id = db.Column(db.String(64), primary_key=True)
    tree_id = db.Column(db.Integer(), unique=False, nullable=False)
    relation_id = db.Column(db.String(40), unique=False, nullable=False)
    provenance = db.Column(db.String(40), unique=False, nullable=False)
    textoffset_startchar = db.Column(db.Integer(), unique=False, nullable=True)
    textoffset_endchar = db.Column(db.Integer(), unique=False, nullable=True)
    text_string = db.Column(db.String(256), unique=False, nullable=True)
    justification = db.Column(db.String(256), unique=False, nullable=True)
    mention_type = db.Column(db.String(40), unique=False, nullable=False)
    subtype = db.Column(db.String(40), unique=False, nullable=False)
    attribute = db.Column(db.String(40), unique=False, nullable=False)
    start_date_type = db.Column(db.String(40), unique=False, nullable=False)
    end_date_type = db.Column(db.String(40), unique=False, nullable=False)
    start_date = db.Column(db.DateTime(), unique=False, nullable=False)
    end_date = db.Column(db.DateTime(), unique=False, nullable=False)
    kb_id = db.Column(db.String(64), db.ForeignKey('kb.id'), nullable=False)

    def __json__(self):
        return ['id','tree_id','relation_id','provenance','textoffset_startchar',
                'textoffset_endchar','text_string','justification','mention_type','subtype',
                'start_date_type','end_date_type','start_date','end_date', 'kb_id']


class ParentChildDetail(db.Model):
    __tablename__ = 'parent_child_detail'
    id = db.Column(db.String(64), primary_key=True)
    parent_uid = db.Column(db.String(64), unique=False, nullable=False)
    child_file = db.Column(db.String(64), unique=False, nullable=False)
    url = db.Column(db.String(512), unique=False, nullable=True)
    dtype = db.Column(db.String(64), unique=False, nullable=False)
    rel_pos = db.Column(db.Integer(), unique=False, nullable=True)
    wrapped_md5 = db.Column(db.String(64), unique=False, nullable=True)
    unwrapped_md5 = db.Column(db.String(64), unique=False, nullable=False)
    download_date = db.Column(db.DateTime(), unique=False, nullable=False)

    def __repr__(self):
        return '<ParentChildDetail %r>' % self.ref_id

    def __json__(self):
        return ['id','parent_uid','child_file','url','dtype',
                'rel_pos','wrapped_md5','unwrapped_md5','download_date']


class Segment(db.Model):
    columns =['id','file_id','segment_number','segment_start','segment_end',
                'segment_start_abs', 'segment_end_abs', 'representative_frame_number',
              'representative_frame_time', 'frame_file_name', 'is_stream',
              'segment_texts','segment_objects']

    """
    A Segment of a video representing a key frame
    """
    __tablename__ = 'segment'
    id = db.Column(db.String(64), primary_key=True)
    file_id = db.Column(db.String(64), nullable=False)
    segment_number = db.Column(db.Integer(), unique=False, nullable=False)
    segment_start = db.Column(db.Integer(), unique=False, nullable=False)
    segment_end = db.Column(db.Integer(), unique=False, nullable=False)
    segment_start_abs = db.Column(db.Float(), unique=False, nullable=True)
    segment_end_abs = db.Column(db.Float(), unique=False, nullable=True)
    representative_frame_number = db.Column(db.Integer(), unique=False, nullable=False)
    representative_frame_time = db.Column(db.Float(), unique=False, nullable=True)
    frame_file_name = db.Column(db.String(256), nullable=True)
    is_stream  = db.Column(db.Boolean, nullable=False)

    def __json__(self):
        return self.columns

    @staticmethod
    def createIndex():
        Index('segment_file_id_idx', Segment.file_id)


class SegmentObjectMatch(db.Model):
    columns = ['id', 'to_obj', 'from_obj', 'measure']

    __tablename__ = 'segment_object_matches'
    id = db.Column(db.String(64), primary_key=True)
    to_obj = db.Column(db.String(64), db.ForeignKey('segment_object.id'), nullable=False)
    from_obj = db.Column(db.String(64), db.ForeignKey('segment_object.id'), nullable=False)
    measure = db.Column(db.Float(), unique=False, nullable=False)

class SegmentObject(db.Model):
    #object type is 'fac','mm_','nat', etc.
    columns = ['id','segment_id', 'object_type', 'bounding_box']

    __tablename__ = 'segment_object'
    id = db.Column(db.String(64), primary_key=True)
    segment_id = db.Column(db.String(64), db.ForeignKey('segment.id'), nullable=False)
    bounding_box = db.Column(db.String(256), unique=False, nullable=True)
    object_type = db.Column(db.String(3), unique=False, nullable=False)
    segment_object = relationship("Segment", backref='segment_objects', foreign_keys=[segment_id])

    def __json__(self):
        return self.columns

class SegmentText(db.Model):
    columns = ['id', 'language','text','text_type']

    __tablename__ = 'segment_text'
    id = db.Column(db.String(64), primary_key=True)
    segment_id = db.Column(db.String(64), db.ForeignKey('segment.id'), nullable=False)
    language = db.Column(db.String(3), unique=False, nullable=False)
    text = db.Column(db.Text(1024, convert_unicode=True), unique=False, nullable=False)
    text_type = db.Column(db.String(3), unique=False, nullable=False)
    segment_text = relationship("Segment", backref='segment_texts', foreign_keys=[segment_id])

    def __json__(self):
        return self.columns

class CanonicalMention(db.Model):
    columns = ['id','entity_mention_id','child_file','frame_number','frame_time',
                'page_number', 'bounding_box', 'is_text', 'user_id', 'record_time']

    __tablename__ = 'canonical_mention'
    id = db.Column(db.String(64), primary_key=True)
    entity_mention_id = db.Column(db.String(64), db.ForeignKey('entity_mention.id'), nullable=False)
    child_file = db.Column(db.String(64), unique=False, nullable=False)
    # depending on media type, video and audio
    frame_number = db.Column(db.Integer(), unique=False, nullable=True)
    # depending on media type, video and audio
    frame_time = db.Column(db.Float(), unique=False, nullable=True)
    # depending on media type of pdf
    page_number = db.Column(db.Integer(), unique=False, nullable=True)
    # bounding box on media type of image, video
    bounding_box = db.Column(db.String(256), unique=False, nullable=True)
    #is text
    is_text = db.Column(db.Boolean(),unique=False)
    #user
    user_id = db.Column(db.String(64),unique=False,nullable=True)
    record_time = db.Column(db.DateTime(), unique=False, nullable=False)

    entity = relationship("EntityMention", foreign_keys=[entity_mention_id])  #

    @hybrid_property
    def bounding_box_list(self):
        return [m.strip() for m in self.bounding_box.strip('[]').split(',')]

    def __json__(self):
        return self.columns


class SegmentComment(db.Model):
    columns = ['id','entity_mention_id','segment_id','user_id','comment']

    __tablename__ = 'segment_comment'

    id = db.Column(db.String(64), primary_key=True)
    entity_mention_id = db.Column(db.String(64), db.ForeignKey('entity_mention.id'), nullable=False)
    segment_id = db.Column(db.String(64), db.ForeignKey('segment.id'), nullable=False)
    user_id = db.Column(db.String(64), unique=False, nullable=False)
    comment = db.Column(db.Text(1024,convert_unicode=True),unique=False, nullable=True)
    record_time = db.Column(db.DateTime(), unique=False, nullable=False)

    entity_mention = relationship("EntityMention", backref='segment_comments', foreign_keys=[entity_mention_id])
    segment = relationship("Segment",foreign_keys=[segment_id])

    def __json__(self):
        return self.columns
