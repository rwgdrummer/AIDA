#!/usr/bin/python3.6
import os
import json

with open('config.json','w') as f:
    data = {
        "SQLALCHEMY_DATABASE_URI" : os.getenv('SQLALCHEMY_DATABASE_URI',''),
        "MEDIA_LOCATION": os.getenv('MEDIA_LOCATION',''),
        "EXTRACTOR_LOCATION" : os.getenv('EXTRACTOR_LOCATION', ''),
        "host": "0.0.0.0",
        "REDIS_HOST":"redis",
        "INDEX_KEY_FRAME_EXTRACTOR": {
            "name": "FixedLocationKeyFrameExtractor",
            "parameters" : {
                "extractor_location" : os.getenv('EXTRACTOR_LOCATION', ''),
                "results_location" : os.getenv('MEDIA_LOCATION','')
            }
        }
    }
    f.write(json.dumps(data))
