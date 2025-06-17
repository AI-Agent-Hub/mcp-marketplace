# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import requests
import logging
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import json
from json.decoder import JSONDecodeError

from .constants import KEY_ID

def get_json_response(response):
    try:
        response.raise_for_status()
        if response.text == "":
            print(f"response.text empty|" + response.text + "| consider setting config or endpoint to /tools such as config_name=\"deepnlp_tool\"")
            return {}
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except JSONDecodeError:
        print("Response conten not in valid JSON|" + response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return {}

class Client:
    def __init__(self, endpoint=None):
        self.endpoint = endpoint

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint

    def get(self, resource_id):
        self._check_endpoint()
        url = self._build_resource_url(resource_id)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def create(self, data):
        self._check_endpoint()
        response = requests.post(self.endpoint, json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, resource_id):
        self._check_endpoint()
        url = self._build_resource_url(resource_id)
        response = requests.delete(url)
        response.raise_for_status()
        return self._handle_delete_response(response)

    def list(self, **params):
        self._check_endpoint()
        response = requests.get(self.endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def search(self, **query_params):
        self._check_endpoint()
        response = requests.get(self.endpoint, params=query_params)
        response.raise_for_status()
        return response.json()

    def search_batch(self, params_list):
        """
            args:
                params_list: list of kvargs
            output:
                list of tuples, [(params, results)]
        """
        parallel_num = len(params_list)
        results = []
        logging.info(f"MCP Marketplace function search_batch start Execution, {parallel_num} parallel tasks..")
        with ThreadPoolExecutor(max_workers=parallel_num) as executor:
            future_to_params = {}
            futures = [executor.submit(self.search, **params) for params in params_list]
            assert len(futures) == len(params_list)
            for params, future in zip(params_list, futures):
                future_to_params[future] = params
            for future in as_completed(futures):
                try:
                    result = future.result()
                    params = future_to_params[future] if future in future_to_params else {}
                    results.append((params, result))
                except Exception as e:
                    print(f"Task failed with error: {str(e)}")
        success_cnt = len(results)
        fail_cnt = parallel_num - success_cnt
        logging.info(f"MCP Marketplace function search_batch End Execution, Success Cnt {success_cnt} Fail Cnt {fail_cnt}...")
        return results

    def get_customized_endpoint(self, params):
        """
            default endpoint:  ${endpoint}/${id}
        """
        id_value = params[KEY_ID] if KEY_ID in params else ""
        return self.endpoint + "/" + id_value

    def list_tools(self, **params):
        """
            dict key: server_id
                value: list of tools
        """
        self._check_endpoint()
        try:
            customized_endpoint = self.get_customized_endpoint(params)
            logging.info(f"MCP Marketplace list_tools GET endpoint {customized_endpoint}")
            response = requests.get(customized_endpoint, params=params)
            data = get_json_response(response)
            return data
        except Exception as e:
            logging.info(f"MCP Marketplace list_tools GET failed. Perhaps you should check the endpoint if set correctly, such as /path/tools")
            logging.error(e)
            return {}

    def list_tools_batch(self, params_list):
        """
            dict key: server_id
                value: list of tools
        """
        parallel_num = len(params_list)
        results = []
        logging.info(f"MCP Marketplace function search_batch start Execution, {parallel_num} parallel tasks..")
        with ThreadPoolExecutor(max_workers=parallel_num) as executor:
            future_to_params = {}
            futures = [executor.submit(self.list_tools, **params) for params in params_list]
            assert len(futures) == len(params_list)
            for params, future in zip(params_list, futures):
                future_to_params[future] = params
            for future in as_completed(futures):
                try:
                    result = future.result()
                    params = future_to_params[future] if future in future_to_params else {}
                    results.append((params, result))
                except Exception as e:
                    print(f"Task failed with error: {str(e)}")
        success_cnt = len(results)
        fail_cnt = parallel_num - success_cnt
        logging.info(f"MCP Marketplace function search_batch End Execution, Success Cnt {success_cnt} Fail Cnt {fail_cnt}...")
        return results
    

    def load_config(self, server_id, **params):
        """
            server: str
        """
        self._check_endpoint()
        try:
            params[KEY_ID] = server_id
            customized_endpoint = self.get_customized_endpoint(params)
            logging.info(f"MCP Marketplace list_tools GET endpoint {customized_endpoint}")
            response = requests.get(customized_endpoint, params=params)
            data = get_json_response(response)
            return data
        except Exception as e:
            logging.info(f"MCP Marketplace list_tools GET failed. Perhaps you should check the endpoint if set correctly, such as /path/tools")
            logging.error(e)
            return {}

    def load_config_batch(self, server_ids, **params):
        """
            server_ids: List of String
            Loading MCP Configs Support Batch
        """
        self._check_endpoint()
        try:
            if not isinstance(server_ids, list):
                logging.info(f"Input Parameters not supported, server_ids should be a list, {server_ids}")
                return {}
            parallel_num = len(server_ids)
            results = []
            logging.info(f"MCP Marketplace function load_config start Execution, {parallel_num} parallel tasks..")
            with ThreadPoolExecutor(max_workers=parallel_num) as executor:
                future_to_params = {}
                futures = [executor.submit(self.load_config, server_id=server_id, **params) for server_id in server_ids]
                assert len(futures) == len(server_ids)
                for params, future in zip(server_ids, futures):
                    future_to_params[future] = params
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        params = future_to_params[future] if future in future_to_params else {}
                        results.append((params, result))
                    except Exception as e:
                        print(f"Task failed with error: {str(e)}")
            ## add post process
            return self.post_process_config(results)
        except Exception as e:
            logging.info(f'MCP Marketplace load_config_batch GET failed. Perhaps you should check the endpoint if set correctly, such as load_config_batch(server_ids, config="deepnlp_server")')
            logging.error(e)
            return {}

    def post_process_config(self, results):
        """
            list of (server_id, server_meta)
        """
        mcp_config_dict = {}
        for (server_id, server_meta) in results:
            config_dict = {}
            try:
                items = server_meta["items"] if "items" in server_meta else []
                config_dict = {}
                if len(items) > 0:
                    item = items[0]
                    config_list = item["config"] if "config" in item else []
                    if len(config_list) > 0:
                        ## Todo: chose suitable config/docker/npx/python
                        config_dict = config_list[0]
            except Exception as e:
                logger.error(f"Failed to post_process_config results {results}")
                logger.error(e)
            mcp_config_dict[server_id] = config_dict
        return mcp_config_dict

    def install(self, unique_id, source, **kwargs):
        """
            Install from Github
        """
        if source == "github":
            if "local_path" not in kwargs:
                logging.error("MCP Marketplace Client Install key local_path is missing in **kwargs %s" % str(kwargs))
                return
            git_clone("https://github.com/%s" % unique_id, kwargs["local_path"])
        elif source == "npmjs":
            npm_install(unique_id)
        else:
            logging.debug("MCP Marketplace Client %s Installed Source %s Not Supported..." % (unique_id, source))

    def _build_resource_url(self, resource_id):
        return urljoin(f"{self.endpoint}/", str(resource_id))

    def _check_endpoint(self):
        if not self.endpoint:
            raise ValueError("API endpoint is not set. Use set_endpoint() to configure it.")

    @staticmethod
    def _handle_delete_response(response):
        if response.status_code == 204:
            return {"status": "success", "message": "Resource deleted successfully"}
        return response.json()
