#coding=utf-8
#!/usr/bin/python

import requests
import os
import re
import json

def call_mcp_api_demo():
    """
        Args:
            
        Return
            {'success': True,
                 'data': '{"city":"乌鲁木齐市","forecasts":[{"date":"2025-06-18","week":"3","dayweather":"晴","nightweather":"多云","daytemp":"32","nighttemp":"22","daywind":"北","nightwind":"北","daypower":"1-3","nightpower":"1-3","daytemp_float":"32.0","nighttemp_float":"22.0"},{"date":"2025-06-19","week":"4","dayweather":"晴","nightweather":"晴","daytemp":"33","nighttemp":"23","daywind":"南","nightwind":"南","daypower":"1-3","nightpower":"1-3","daytemp_float":"33.0","nighttemp_float":"23.0"},{"date":"2025-06-20","week":"5","dayweather":"晴","nightweather":"多云","daytemp":"35","nighttemp":"24","daywind":"东南","nightwind":"东南","daypower":"1-3","nightpower":"1-3","daytemp_float":"35.0","nighttemp_float":"24.0"},{"date":"2025-06-21","week":"6","dayweather":"多云","nightweather":"晴","daytemp":"34","nighttemp":"22","daywind":"西北","nightwind":"西北","daypower":"1-3","nightpower":"1-3","daytemp_float":"34.0","nighttemp_float":"22.0"}]}',
                 'error': None}
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            "Content-Type": "application/json"
        }
        url = 'http://127.0.0.1:5000/api/query'
        input_params = {
            "server_id": "amap-amap-sse", 
            "tool_name": 'maps_weather',
            "tool_input": {
                "city": "乌鲁木齐"
            }
        }
        response = requests.post(url, data=json.dumps(input_params), headers=headers, timeout=5)
        result_json = response.json()
        print (result_json)

    except Exception as e:
        print (e)

def main():
    call_mcp_api_demo()

if __name__ == '__main__':
    main()
