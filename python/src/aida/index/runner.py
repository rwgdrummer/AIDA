# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from aida.api.provider import FlaskAppWrapper, load_config
from aida.index.api import AIDAIndex

def get_config_args():
    import sys
    if len(sys.argv) > 1 and sys.argv[1].endswith('json'):
        return sys.argv[1]
    return 'config.json'

if __name__ == '__main__':
    external_config = load_config(filename=get_config_args())
    app_wrapper = FlaskAppWrapper(providers=[AIDAIndex()],external_config=external_config)
    app_wrapper.create_app()
    app_wrapper.run_app(host='127.0.0.1' if 'host' not in external_config  else external_config['host'])