# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================
from aida.api.provider import FlaskAppWrapper, load_config, SecurityProvider
from aida.ldcrepo.api import AIDARepo
from aida.api.api import UserRepo
from aida.index.api import  AIDAIndex

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

def get_config_args():
    import sys
    if len(sys.argv) > 1 and sys.argv[1].endswith('json'):
        return sys.argv[1]
    return 'config.json'

def get_providers(external_config):
    if 'providers' in external_config:
        return [ get_class(provider)() for provider in external_config['providers']]
    return [ UserRepo(), AIDARepo(), AIDAIndex()]

if __name__ == '__main__':
    external_config = load_config(filename=get_config_args())
    app_wrapper = FlaskAppWrapper(providers=get_providers(external_config=external_config),external_config=external_config)
    app_wrapper.create_app()
    app_wrapper.run_app(host='127.0.0.1' if 'host' not in external_config  else external_config['host'])
