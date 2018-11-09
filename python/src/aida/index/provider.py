# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from aida.api.provider import Provider
from aida.index.index import NormalizeHash,ImageMatchHasher,resizeAndEquaHist,LSHIndex, redisStorage, memoryStorage
from aida.api.textloader import get_value_from_config
from aida.index.associated_metadata_index import RedisMetaDataIndex

class IndexStore(Provider):
    """
    Describes Index Repository Configuration
    """

    def __init__(self):
       Provider.__init__(self,IndexStore.__name__)

    def init(self,app=None,api=None):
        """
        :param app:
        :return:
        @type app: FlaskAppWrapper
        @type api: Api
        """
        from functools import partial
        #hard code for now
        self.hasher = NormalizeHash(ImageMatchHasher(), resizeAndEquaHist)
        if self.redis_host == 'NA':
            factory = memoryStorage
            self.metaindex= {}
        else:
            factory = partial(redisStorage,host=self.redis_host)
            self.metaindex = RedisMetaDataIndex(self.redis_host)
        self.indexer = LSHIndex(self.hasher,match_thresh=300,storage=factory)

    def config(self, external_config={}):
        "TODO eventually for DB config such threshold, hash, etc."
        self.index_dir = get_value_from_config(external_config,'INDEX_LOCATION','.')
        self.redis_host = get_value_from_config(external_config, 'REDIS_HOST', 'NA')
        self.extractor_directory = get_value_from_config(external_config, 'EXTRACTOR_LOCATION', '.')
        return {}

