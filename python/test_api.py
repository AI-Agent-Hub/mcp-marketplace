# -*- coding: utf-8 -*-
# @Time    : 2025/03/01

import json
import mcp_marketplace as mcpm

def run_setup_config_deepnlp():

    mcpm.set_endpoint("deepnlp")
    # params = {"query": "map", "page_id":"0", "count_per_page":"20", "mode": "dict"}
    # result = mcpm.search(**params)
    result = mcpm.search(query="map", page_id=0, count_per_page=20, mode="dict")
    print ("DEBUG: run_setup_config_deepnlp result:")
    print (result)

def run_setup_config_pulsemcp():
    """
        https://www.pulsemcp.com/api
        query   
        count_per_page
        offset
    """
    mcpm.set_endpoint("pulsemcp")
    # params = {"query":"Map", "count_per_page":"20", "offset":"0"}
    result = mcpm.search(query="map", count_per_page=20, offset=0)
    print ("DEBUG: run_setup_config_pulsemcp result:")
    print (result)

def run_api_methods():

    """
    """
    ## list
    ## create
    ## delete
    ## 
    ### create
    run_setup_config_pulsemcp()


def main():

    run_setup_config_pulsemcp()

    run_setup_config_deepnlp()

if __name__ == '__main__':
    main()
