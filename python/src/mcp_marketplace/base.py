# -*- coding: utf-8 -*-
# @Time    : 2024/06/27

import requests
from urllib.parse import urljoin

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

    def list_tools(self, **params):
        available_tools = []
        return available_tools

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
