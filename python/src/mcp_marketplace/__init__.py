# -*- coding: utf-8 -*-
# @Time    : 2024/06/27
# @Author  : Derek

import logging
from .base import Client
from .config import ConfigurationManager
from .constants import *

config_manager = ConfigurationManager()

## add default config
config_manager.configure(name="deepnlp", endpoint="http://www.deepnlp.org/api/mcp_marketplace/v1")
config_manager.configure(name="pulsemcp", endpoint="https://api.pulsemcp.com/v0beta/servers")
config_manager.configure(name="deepnlp_tool", endpoint="http://www.deepnlp.org/api/mcp_marketplace/v1/tools")
config_manager.configure(name="deepnlp_server", endpoint="http://www.deepnlp.org/api/mcp_marketplace/v1/server")

_default_client = Client()

DEFAULT_CONFIG_NAME = "deepnlp"

def set_endpoint(config_name="", url=""):
    config = config_manager.get_config(config_name)
    if config is not None:
        _default_client.set_endpoint(config.endpoint)
    else:
        _default_client.set_endpoint(url)

def set_endpoint_from_params(params):
    """ Check if params contains config keys
    """
    if KEY_CONFIG_NAME in params or KEY_URL in params:
        config_name = params[KEY_CONFIG_NAME] if KEY_CONFIG_NAME in params else ""
        url = params[KEY_URL] if KEY_URL in params else ""
        set_endpoint(config_name, url)
    else:
        # without setting endpoint using defaujt
        set_endpoint(DEFAULT_CONFIG_NAME, "")

def get(resource_id, **params):
    set_endpoint_from_params(params)
    return _default_client.get(resource_id)

def create(data, **params):
    return _default_client.create(data)

def delete(resource_id, **params):
    set_endpoint_from_params(params)
    return _default_client.delete(resource_id)

def list(**params):
    set_endpoint_from_params(params)
    return _default_client.list(**params)

def search(**query_params):
    set_endpoint_from_params(query_params)
    print('GET Endpoint %s' % _default_client.endpoint)
    return _default_client.search(**query_params)

def search_batch(query_params_list):
    if len(query_params_list) > 0:
        set_endpoint_from_params(query_params_list[0])
    print('GET Endpoint %s' % _default_client.endpoint)        
    return _default_client.search_batch(query_params_list)

def list_tools(**params):
    """ assembly config and client
    """
    set_endpoint_from_params(params)
    print('GET Endpoint %s' % _default_client.endpoint)    
    return _default_client.list_tools(**params)

def list_tools_batch(query_params_list):
    if len(query_params_list) > 0:
        set_endpoint_from_params(query_params_list[0])
    print('GET Endpoint %s' % _default_client.endpoint)        
    return _default_client.list_tools_batch(query_params_list)

def load_config_batch(server_ids, **params):
    set_endpoint_from_params(params)
    print('GET Endpoint %s' % _default_client.endpoint)    
    return _default_client.load_config_batch(server_ids, **params)
