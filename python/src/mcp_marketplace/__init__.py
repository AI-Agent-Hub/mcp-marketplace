# -*- coding: utf-8 -*-
# @Time    : 2024/06/27
# @Author  : Derek

from .base import Client
from .config import ConfigurationManager

config_manager = ConfigurationManager()

## add default config
config_manager.configure(name="deepnlp", endpoint="http://www.deepnlp.org/api/mcp_marketplace/v1")
config_manager.configure(name="pulsemcp", endpoint="https://api.pulsemcp.com/v0beta/servers")

_default_client = Client()

def set_endpoint(config_name, url=""):
    config = config_manager.get_config(config_name)
    if config is not None:
        _default_client.set_endpoint(config.endpoint)

def get(resource_id):
    return _default_client.get(resource_id)

def create(data):
    return _default_client.create(data)

def delete(resource_id):
    return _default_client.delete(resource_id)

def list(**params):
    return _default_client.list(**params)

def search(**query_params):
    return _default_client.search(**query_params)

def list_tools(**params):
    return _default_client.list_tools(**params)
