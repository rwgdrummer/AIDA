# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
import os
import uuid

from aida.api.provider import load_config
from aida.api.textloader import create_db_app
from aida.ldctools.textloader import map_column_values, log, FileWriter, FileReader
from aida.media.key_frame_extractor import SegmentLoader
from traceback import print_tb
from sys import exc_info, stdout
from sqlalchemy import bindparam

"""
The DAO for the LDC KB model
"""

from aida.ldcrepo.model import Hypothesis, db,KB, EntityMention,RelativeMention,\
    ParentChildDetail, Media, Entity, CanonicalMention, Segment, SegmentText, \
    SegmentObject,SegmentObjectMatch
from logging import INFO, ERROR


def loadMedia(filename):
    def processor(session, columns):
        values = map_column_values(columns,['id','media_type'],Media)
        session.add(Media(**values))
    FileReader(filename).read(db.session,processor)

def loadHypothesis(filename):
    def processor(session, columns):
        values = map_column_values(columns,['id','topic_name','text_query','hypothesis'],Hypothesis)
        session.add(Hypothesis(**values))
    FileReader(filename).read(db.session,processor)

def loadObjects(object_type, filename):
    from aida.media.object import MediaObject, MediaObjectIdentifier
    loader = MediaObjectIdentifier()
    data = loader.load(filename,object_type)
    matches = {}
    preloads = {}
    premappings = set()
    for x in db.session.query(Segment.frame_file_name, Segment.id).all():
        matches[x.frame_file_name] = x.id
    for x in db.session.query(SegmentObject.segment_id, SegmentObject.bounding_box, SegmentObject.id).all():
        preloads[x.segment_id + SegmentObject.bounding_box] = x.id
    for x in db.session.query(SegmentObjectMatch.to_obj, SegmentObjectMatch.from_obj).all():
        premappings.add(x.to_obj + x.from_obj)
    mappings = {}
    for v in data.values():
        item = None
        levels = 3
        while levels > 0 and item is None:
            search_id = v.id.split(os.path.sep)[-levels:]
            key = os.path.sep.join(search_id)
            if key in matches:
                item = matches[key]
            levels -= 1
        if item is None:
            log(ERROR, "Cannot find file {} ".format(v.id))
        elif item + v.text_bounding_box() in preloads:
            mappings[v.id] = preloads[item + v.text_bounding_box()]
            continue
        else:
            log(INFO, "File {} ".format(v.id))
            new_id = uuid.uuid4().urn
            db.session.add(SegmentObject(id=new_id,
                                         bounding_box=v.text_bounding_box(),
                                         object_type=v.object_type,
                                         segment_id=item
                                         ))
            mappings[v.id] = new_id
    db.session.commit()
    commit_time = 1000
    for v in data.values():
        for rel in v.relationships:
            new_id = uuid.uuid4().urn
            #print("%s %s" % (mappings[rel[0]], mappings[v.id]))
            if (mappings[rel[0]] + mappings[v.id]) in premappings:
                continue
            db.session.add(SegmentObjectMatch(id=new_id,
                                              to_obj=mappings[rel[0]],
                                              from_obj=mappings[v.id],
                                              measure=rel[1]
                                              ))
            commit_time-=1
            if commit_time == 0:
                commit_time = 1000
                db.session.commit()
    db.session.commit()

def loadKB(filename):
    from functools import partial
    loaded_ids = set()
    def processor(loaded_ids, session, columns):
        if columns[1] is None:
            print('Null topic_id for %s' % columns[0])
            columns[1] = 'NIL'
        if  columns[0] in loaded_ids:
            return
        loaded_ids.add(columns[0])
        values = map_column_values(columns,['id','topic_id','category','handle','description'],KB)
        session.add(KB(**values))
    FileReader(filename).read(db.session, partial(processor,loaded_ids))

def loadKBEntities(filename):
    from functools import partial
    mappings = ['id','topic_id','category','handle','description']
    loaded_ids = set([x[0] for x in db.session.query(KB.id).all()])
    def processor(loaded_ids, session, columns):
        # move entity_id over into id
        if columns[7] is None or len(columns[7]) == 0:
            columns[7] = columns[6]
        row = [columns[-1], 'NIL','entity', columns[7][:128], columns[7][:512]]
        if  row[0] in loaded_ids:
            return
        loaded_ids.add(row[0])
        values = map_column_values(row, mappings, KB)
        session.add(KB(**values))
    FileReader(filename).read(db.session, partial(processor,loaded_ids))
    #print(loaded_ids)

def loadMediaEntities(filename):
    from functools import partial
    mappings = ['id','media_type']
    loaded_ids = set([x[0] for x in db.session.query(Media.id).all()])
    def processor(loaded_ids, session, columns):
        # move entity_id over into id
        row = [columns[3], 'unk']
        if  row[0] in loaded_ids:
            return
        loaded_ids.add(row[0])
        values = map_column_values(row, mappings, Media)
        session.add(Media(**values))
    FileReader(filename).read(db.session, partial(processor,loaded_ids))
    #print(loaded_ids)

def loadEntities(filename):
    from functools import partial
    mappings = ['tree_id','id','entity_id','provenance','textoffset_startchar',
                'textoffset_endchar','text_string','description','entity_type','level','kb_id']
    loaded_ids = set()
    loaded_p = set([x[0] for x in db.session.query(Media.id).all()])
    def processor(loaded_ids, session, columns):
        # move entity_id over into id
        columns[1] = columns[2]
        if  columns[2] in loaded_ids:
            return
        loaded_ids.add(columns[2])
        if columns[7] is None or len(columns[7]) == 0:
            columns[7] = columns[6]
        if columns[3] not in loaded_p:
            print('%s %s' % (columns[1],columns[3]))
        values = map_column_values(columns, mappings, Entity)
        session.add(Entity(**values))
    FileReader(filename).read(db.session, partial(processor,loaded_ids))

def loadCanonicals(filename):
    def processor(session, columns):
        values = map_column_values(columns, CanonicalMention.columns, EntityMention)
        session.add(CanonicalMention(**values))
    FileReader(filename,skip_first_line=False).read(db.session, processor)

def dumpCanonicals(filename):
    iterator = db.session.query(CanonicalMention).all()
    FileWriter(filename).write(CanonicalMention.columns, iterator)

def loadSegments(filename):
    def processor(session, columns):
        values = map_column_values(columns, Segment.columns, EntityMention)
        session.add(Segment(**values))
    FileReader(filename,skip_first_line=False).read(db.session, processor)

def dumpSegments(filename):
    iterator = db.session.query(Segment).all()
    FileWriter(filename).write(Segment.columns, iterator)

def loadEntityMentions(filename):
    mappings = ['tree_id','id','entity_id','provenance','textoffset_startchar',
                'textoffset_endchar','text_string','justification','mention_type','level','kb_id']
    def processor(session, columns):
        values = map_column_values(columns,mappings,EntityMention)
        session.add(EntityMention(**values))
    FileReader(filename).read(db.session, processor)

def loadOCR(text_type,filename ):
    """
    :param segment_updater: function to update a segment
    :param filename:
    :return:
    """
    from functools import partial
    def processor(text_type, session, columns):
        """
        :param session:
        :param columns:
        :return:
        @type session: Session
        @type columns: list
        """
        frame_file_name = columns[0]
        objs = session.query(Segment).filter(Segment.frame_file_name == bindparam('frame_file_name')).\
            params(frame_file_name=frame_file_name).all()
        for obj in objs:
            values = {'id' : uuid.uuid4().urn,
                     'segment_id': obj.id,
                     'text_type': text_type,
                     'language': columns[1],
                     'text': columns[2][:1024]}
            session.add(SegmentText(**values))
    FileReader(filename,skip_first_line=False).read(db.session, partial(processor,text_type))

def loadRelativeMentions(filename):
    mappings = ['tree_id','id','relation_id','provenance','textoffset_startchar',
                'textoffset_endchar','text_string','justification','mention_type','subtype',
                'attribute','start_date_type','start_date','end_date_type','end_date',
               'kb_id']
    def processor(session, columns):
        values = map_column_values(columns,mappings,RelativeMention)
        session.add(RelativeMention(**values))
    FileReader(filename).read(db.session,processor)

def loadParentChildDetails(filename):
    mappings = ['parent_uid','child_file','url','dtype','rel_pos',
                'wrapped_md5','unwrapped_md5','download_date']
    def processor(session, columns):
        values = map_column_values(columns,mappings,ParentChildDetail)
        values['id'] = uuid.uuid4().urn
        session.add(ParentChildDetail(**values))
    FileReader(filename).read(db.session,processor)


def dumpWithinContext(dirs):
    dumping_functions = [('all_segments.tab', dumpSegments), ('all_canonicals.tab', dumpCanonicals)]
    for dumping_function in dumping_functions:
        log(INFO, "Storing %s" % (dumping_function[0]))
        filename = os.path.join(dirs[0], dumping_function[0])
        dumping_function[1](filename)

def dump(app, dirs):
    with app.app_context():
        db.init_app(app)
        dumpWithinContext(dirs)

def loadWithinContext(dirs):
    import re
    from functools import partial
    # map to loading functions
    # order by the order loading.
    # None is indicative of future use!
    loading_function_mappings = [
        ("hypothesis_info\.tab", loadHypothesis),
        ("media_list.tab", loadMedia),
        ("parent_children\.tab", loadParentChildDetails),
        ("twitter_info\.tab", None),
        ("uid_info\.tab", None),
        ("uids_missing_video\.tab", None),
        ("T.*KB\.tab", loadKB),
        ("T.*ent_mentions\.tab", loadKBEntities),  # yes, same file
        ("T.*ent_mentions\.tab", loadMediaEntities),  # yes, same file
        ("T.*ent_mentions\.tab", loadEntities),  # yes, same file
        ("T.*ent_mentions\.tab", loadEntityMentions),
        ("T.*evt_mentions\.tab", None),
        ("T.*evt_slots\.tab", None),
        ("T.*rel_mentions\.tab", None),
        ("T.*rel_slots\.tab", None),
        ("T.*hypothesis\.tab", None),
        ("rel_evt_slot_mapping_table\.tab", None),
        ("doc_lang\.tab", None),
        (".*canonicals\.tab", loadCanonicals),
        (".*segments\.tab", loadSegments),
        (".*_multimediaobject\.json", loadKeyFrames),
        ("image.json",loadImages),
        ("ocr.txt", partial(loadOCR,'inf')),
        ("object_faces.*\.json",partial(loadObjects,'fac'))]
    loading_function_mappings = [(re.compile(mapping[0]), mapping[1]) for mapping in loading_function_mappings]

    # find the files; organize by name
    files_by_match = [[] for pos in range(len(loading_function_mappings))]
    count = 0
    for dir in dirs:
        log(INFO, "Scanning directory %s" % (dir))
        for root, walked_dirs, files in os.walk(dir):
            for name in files:
                for pos in range(len(loading_function_mappings)):
                    if loading_function_mappings[pos][1] is None:
                        continue
                    if loading_function_mappings[pos][0].match(name) is not None:
                        count += 1
                        files_by_match[pos].append(os.path.join(root, name))

    log(INFO, "Loading %d files" % (count))
    for pos in range(len(loading_function_mappings)):
        mapping = loading_function_mappings[pos]
        matched_files = files_by_match[pos]
        # have a loading function?
        if mapping[1] is not None:
            # load each matching the mapping's name
            for matched_file in matched_files:
                log(INFO, "Loading %s" % (matched_file))
                try:
                    mapping[1](matched_file)
                except Exception as e:
                    log(ERROR, "Failed to load %s: %s" % (matched_file, str(e)))
                    exc_type, exc_value, exc_traceback = exc_info()
                    print_tb(exc_traceback, limit=1, file=stdout)
                    raise e
    db.session.commit()
    log(INFO, "Loading complete")

def load(app, dirs, create_db=True):
    with app.app_context():
        db.init_app(app)
        if create_db:
            db.create_all()
        loadWithinContext(dirs)
        if create_db:
            Segment.createIndex()

def loadImage(filename):
    session = db.session
    real_file_name = os.path.basename(os.path.splitext(filename)[0] if filename.endswith("ldcc") else filename)
    ldcc_file_name = os.path.basename(filename if filename.endswith("ldcc") else filename + '.ldcc')
    values = {    'id':uuid.uuid4().urn,
                      'file_id': ldcc_file_name,
                      'segment_number': 1,
                      'segment_start': 1,
                      'segment_end': 1,
                      'segment_start_abs': 0,
                      'segment_end_abs': 0,
                      'representative_frame_number':1,
                      'representative_frame_time':0,
                      'frame_file_name':real_file_name,
                      'is_stream':False}
    session.add(Segment(**values))

def loadImages(filename):
    from json import load
    count = 0
    with open(filename,'r') as fp:
        imageset = load(fp)
        for i in imageset['images']:
            loadImage(i)
            count+=1
    print ('load %d images' % count)

def loadKeyFrames(filename):
    segment_loader = SegmentLoader(filename)
    session = db.session
    for segment in  segment_loader.load_segments():
        values = {    'id':uuid.uuid4().urn,
                      'file_id': os.path.basename(segment.file_name + '.ldcc'),
                      'segment_number':segment.segment_number,
                      'segment_start': segment.start,
                      'segment_end': segment.end,
                      'segment_start_abs': segment.start_abs,
                      'segment_end_abs': segment.end_abs,
                      'representative_frame_number':segment.representative_frame_number,
                      'representative_frame_time':segment.representative_frame_number * (segment.end_abs/segment.end_abs),
                      'frame_file_name':segment.frame_file_name,
                      'is_stream':True}
        session.add(Segment(**values))

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Load DB Models.')
    parser.add_argument('--dirs', nargs='+',
                        help='directories to search')
    parser.add_argument('--config',
                        help='JSON config file')
    parser.add_argument('--dump', action='store_true',
                        help='Output')

    args = parser.parse_args()
    dirs = args.dirs
    config = load_config(filename=args.config)
    app = create_db_app(name='aida',external_config=config)
    if args.dump:
        dump(app,dirs)
    else:
        load(app,dirs)

if __name__ == "__main__":
    # execute only if run as a script
    main()
